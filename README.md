# Optiver AI Chessathon — chess engine

A classical alpha-beta chess engine written in Python for the [AI Chessathon](https://aichessathon.com),
sponsored by Optiver. Built solo over nine days with no prior game-engine experience.

**Result:** 215th of 334 in the 13-round qualification Swiss (6.0/13, Buchholz 76.5).
Peak ladder rating 1645, final 1556, across 115 rated games.

**Reliability:** zero timeouts, zero crashes, and zero illegal moves across every rated
game played. This was the first design priority and it held.

---

## The contract

The platform imports a single file and calls one function:

```python
def get_move(fen: str, time_left_ms: int) -> str:
    ...  # returns a move in UCI notation, e.g. "e2e4"
```

One core, 2 GB, 120s + 0.5s increment, no network. Only `python-chess` and four other
libraries are available. Games start from curated near-level opening positions, and
illegal moves, crashes and timeouts are all scored as losses.

---

## Architecture

### Search

| Technique | What it does |
|---|---|
| Alpha-beta negamax | Prunes branches that provably can't change the result |
| Iterative deepening | Searches depth 1, 2, 3... and keeps the deepest completed answer |
| Adaptive time budget | Spends more when the root move is unstable, banks clock when it isn't |
| Quiescence search | Keeps searching captures past the depth limit until the position is quiet |
| Delta pruning | Skips captures that can't reach alpha even if they win the piece for free |
| SEE | Full recursive static exchange evaluation — simulates the whole capture sequence |
| Transposition table | Caches results with exact/lower/upper bound flags and ply-normalised mate scores |
| Move ordering | TT move → SEE-scored captures → killer moves → aged history heuristic |
| Null-move pruning | If you're still winning after giving the opponent a free move, skim the branch |
| PVS | Full window on the first move, null window on the rest |
| Late move reductions | Reduces late quiet moves, re-searches when one surprises |
| Incremental evaluation | Carries running material/phase totals through push and pop |
| Repetition detection | Scores a return to a previously-seen position as a draw |

### Evaluation

Material and tapered PeSTO piece-square tables, blended between midgame and endgame
values by remaining non-pawn material. On top of that: passed pawns, king pawn shield,
bishop pair, rooks on open and half-open files, doubled and isolated pawns, a mop-up
term that drives a bare enemy king to the edge, and a penalty that decays the advantage
as the fifty-move counter climbs.

All terms are computed in a single pass over flat arrays, with pawn-structure terms
cached on the pawn bitboards.

---

## Performance

Node cost for a fixed-depth search from a standard middlegame position, measured across
the build:

| Milestone | Depth 4 |
|---|---|
| Alpha-beta, material eval only | 2.662s |
| + MVV-LVA move ordering | 0.437s |
| + transposition table | 1.587s (evaluation got heavier) |
| + PVS | 0.540s |
| + late move reductions | 0.240s |
| + SEE pruning in quiescence | 0.160s |
| + incremental evaluation | **0.136s** |

Roughly 20× over the week. Depth 8 completes where depth 5 was a stretch at the start.

Against the bundled baselines: 100% against `random`, `greedy`, `minimax` and `numba`.

---

## Running it

The project uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run python -m harness.play --white . --black baselines/minimax
uv run python -m harness.arena --opponent baselines/minimax --games 20
uv run python -m harness.package        # builds submission.zip
```

### Test tools

The local arena turned out to be unable to resolve changes smaller than about 50 Elo —
too few games, too many draws, and a large first-move advantage. The tools that actually
worked are targeted and fast:

| Tool | Answers |
|---|---|
| `tools/depths.py` | What does each extra ply cost? |
| `tools/matedepth.py` | Are mate scores ordered by distance? |
| `tools/repcheck.py` | Does it convert a won position instead of shuffling? |
| `tools/mate.py` | Can it mate with king and rook against a bare king? |
| `tools/seecheck.py` | Does SEE get constructed exchanges right? |
| `tools/deltacheck.py` | Does the incremental eval match a full recomputation? |

Every change was verified against these before shipping. Refactors were verified by
equality — run both versions over hundreds of random positions and require zero
mismatches.

---

## Bugs worth documenting

**Quiescence returned an unadjusted mate score.** `quiesce` returned `-MATE` where the
rest of the search used `-MATE + ply`. Every mating line therefore scored exactly
1,000,000, so mate-in-1 and mate-in-20 were indistinguishable and the engine picked
arbitrarily among dozens of tied moves. This presented as the engine repeating moves in
overwhelmingly won positions — which led to four separate attempts to fix "the repetition
problem", all of which failed because they targeted the symptom. It was found by printing
raw root scores instead of theorising, and fixed by adding two characters.

**Fail-hard and fail-soft mixed between functions.** `quiesce` returned the window bound
on a cutoff while `search` returned a true score. `search` then treated a bound as an
exact value and propagated it, corrupting everything above it in the tree. Quiescence
looked broken twice before the convention mismatch was identified.

**The root tie-break admitted rejected moves.** Fail-soft scores can land exactly on
alpha when a move fails low, and those were being appended to the list of "tied best
moves" and selected at random. Better move ordering made it worse, because good ordering
raises alpha faster and more moves land on that bound.

**Mate scores were stored in the transposition table without ply normalisation**, so a
mate found at one depth meant something different when reused at another.

---

## Things that were tried and rejected

Recorded because a negative result measured is worth more than a feature shipped on faith.

- **Repetition penalties in the search** — four variants, measured over 60+ games each.
  None helped; one scored 45% against a random opponent. The underlying cause was the
  mate-score bug above.
- **Check extensions** — depth 5 went from 7.0s to 10.4s with no improvement in move
  quality.
- **Aspiration windows** — no measurable effect once PVS and LMR were doing the pruning.
- **Numba on the evaluation** — measured roughly break-even. The Python↔numba boundary
  crossing costs about as much as the compiled code saves at this granularity.
- **Incremental Zobrist hashing** — 7% of positions mismatched on castling-rights changes
  and en-passant squares. A wrong hash means a wrong cache hit, which is silent corruption
  that no available test would catch, so it was dropped rather than half-fixed.

---

## Limitations

The ceiling here is the substrate. `python-chess` generates moves at roughly 250k per
second; a bitboard move generator compiled with numba does 5–20 million. That gap is
three to four plies, which is most of the distance to the top of the ladder. Every
technique in this engine squeezes more depth out of the same node budget — the remaining
gain is in nodes per second, and that means writing a move generator from scratch.

That was ruled out on day one as a 60-hour project against a nine-day budget, and the
decision still looks right: the alternative was shipping nothing.

Also missing: no mobility term, no king-attack evaluation beyond a three-file pawn
shield, and evaluation weights are published values rather than tuned on this engine's
own search.

---

## Licence

The harness and baselines come from the
[official starter repository](https://github.com/advitrocks9/aichessathon-starter).
Piece-square table values are PeSTO's, fitted by Ronald Friederich. Everything in
`agent.py` was written for this competition.