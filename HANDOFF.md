# Handoff — agent.py session, 9 Sept 2026

Context for whoever picks this up. Everything below was **measured on this
machine**, not reasoned from general chess-engine knowledge. Where a number
appears, it came from a run. Commits `5afa1b3..5184281`, tree clean.

Environment: Windows, uv, python-chess 1.11.2, Python 3.12, one core.
Suite used after every single change:

```
uv run ruff check .; uv run mypy
uv run python -m tools.depths        (x3, take the min - see "gate noise")
uv run python -m tools.matedepth     999999 / 999997 / 999995
uv run python -m tools.repcheck      must mate in 1
uv run python -m tools.mate          KRvK must mate
uv run python -m harness.arena --opponent baselines/random --games 10 --base-ms 5000
```

---

## 1. What changed

Six commits, each gated on the full suite and committed separately.

| commit | change | effect |
|---|---|---|
| `5afa1b3` | `get_move` never raises | crash fix |
| `e8603a4` | promotions/en-passant no longer classed as quiet | correctness |
| `01c476c` | pawn-structure eval cache | depth 6 −11.2% |
| `52cb008` | incremental zobrist key | depth 6 −6.8% |
| `452e9b1` | iterative-deepening exit test | depth 5.56 → 6.11 |
| `71be1fe` | time reserve + pawn cache cap | depth 6.11 → 6.33 |

Net: **depth 6 search 1.727s → ~1.40s (−19%)**, and about **+0.8 ply** from
the clock work on top of that.

### 1.1 `get_move` never raises (`5afa1b3`)

`next(iter(board.legal_moves))` and `chess.Board(fen)` sat *outside* the
existing `try`. Verified against the old code: a checkmated or stalemated
position raised `StopIteration`, a malformed FEN raised `ValueError`. Both
killed the process, which forfeits the game. Whole preamble is now guarded
and falls back to `"0000"`.

### 1.2 Promotions and en-passant are not quiet (`e8603a4`)

`quiet = board.piece_type_at(move.to_square) is None` is true for a promotion
to an empty square and for en-passant (the captured pawn is not on
`to_square`). Both were being LMR-reduced and written into killers/history.

Used an inline bitboard test, not `board.is_capture(move)` — the readable
version benched **170.2 ns/move against 82.0 ns** for the old wrong one, and
that shows up in the gate. The inline test is 89.8 ns.

### 1.3 Pawn-structure cache (`01c476c`)

Passed / doubled / isolated pawns are a pure function of the two pawn
bitboards, so they were being recomputed at every leaf. Factored into
`pawn_terms()`, keyed on `(white_pawns, black_pawns)`, shared by **both**
`evaluate` and `evaluate_incr` so the two cannot drift.

- **92.2% hit rate from 3,881 entries** at depth 6
- refactored `evaluate()` is **bit-identical over 15,258 random positions**
- entries stay valid across moves *and games* (pure function)

### 1.4 Incremental zobrist key (`52cb008`)

`chess.polyglot.zobrist_hash` walked all 32 pieces per node: **13.7% of
runtime at 13.58 µs/call**.

**Design worth preserving.** Only *piece placement* is incremental, threaded
through `move_delta` alongside mg/eg/phase. Side to move, castling rights and
the en-passant file are read fresh from the board each node by `state_key()`.
Those three are the awkward cases — rights lost when a rook is captured, an ep
square expiring, a null move clearing it — and because they are never carried,
they cannot accumulate drift. `move_delta` already modelled every placement
special case (proven by `deltacheck`), so the incremental part rides on
already-verified logic.

Verification:

| check | result |
|---|---|
| incremental vs from-scratch, random moves | 0 / 66,730 (68 castles, 6 ep, 88 promos) |
| same, at every real search node | 0 drift / 47,512 nodes (incl. Kiwipete) |
| collisions on distinct positions | 0 / 89,700 |
| directed cases incl. promotion-with-capture | 15/15 exact |

`tools/matedepth.py` and `tools/deltacheck.py` were updated for the 4-tuple
`move_delta`. `tools/rootscores.py` was **already broken** before this session
(calls `agent.search` with 6 args) and was left alone.

### 1.5 The clock — the largest single win (`452e9b1`, `71be1fe`)

From the 79-game CSV in `losing_games_investigate/`: the engine spent a
**median 53% of its fair per-move share** and never finished a game with less
than **24.9s** left. Cause:

```python
if depth > 2 and elapsed + last_depth_s * 8 > limit: break
```

It assumed a new iteration costs **8x** the previous. Measured across six
positions at depth ≥5: **median 2.53, p90 4.80, max 5.58**. So it quit an
iteration early on most moves. The `Clock` is the real hard stop, so this line
was only ever an optimisation — pessimism here bought nothing.

Now `ITERATION_COST_FACTOR = 3.0` (near measured p75), plus an explicit
reserve: `budget = (remaining − TIME_RESERVE) / TIME_DIVISOR` with
`TIME_RESERVE = 5.0`, `TIME_DIVISOR = 10.0`.

The clock now follows `r' = 0.9r + 1.0`, which **converges to exactly 10.00s
and never drops below** — verified over 140 consecutive worst-case moves where
every move burns its full budget. The old reserve-less `remaining/12` settled
at 6s. So this is **deeper and safer** at once. Under 5s left it moves
instantly.

This settles the "/12 vs /15" open item in `notes.md`: it was never a divisor
question, it was a missing reserve plus a wrong branching-factor constant.

---

## 2. Do not retry these — measured failures

### 2.1 SEE out of move ordering → **reverted, not committed**

Replacing `see_gain` with MVV-LVA in `move_score`. Per-capture scoring got
**8.5x cheaper (3.186 → 0.373 µs)** and the engine got *slower*:

| | depth 4 min | depth 6 min |
|---|---|---|
| before | 0.115s | 1.731s |
| MVV-LVA ordering | **0.140s** (gate FAIL) | **1.812s** (+4.7%) |
| after revert | 0.129s | 1.736s |

Three runs each, tightly clustered. **SEE is load-bearing**: it sorts losing
captures *below* the killers, and dropping it pushes every capture above them.
That ordering loss costs more nodes than the arithmetic saves.

### 2.2 Staged move generation → **not attempted, modelled at −19.5%**

The cutoff statistics look ideal:

- **94.0%** of beta cutoffs land on the **first** move (97.5% within two)
- at cut-nodes, 311,364 moves generated to search 10,658 — **96.6% waste**
- only **2.3%** of cutoffs are caused by a quiet move

But python-chess recomputes pins/checkers/king-safety per call, so generation
does not decompose:

```
list(board.legal_moves)        29.28 us  (33 moves)   <- current, one call
generate_legal_captures()       9.03 us  ( 2 moves)
generate_legal_moves(~them)    28.05 us  (31 moves)   <- quiets alone ~= full call
captures + quiets, two calls   39.58 us               <- +35%
```

Applied to the measured node mix at depth 6:

```
cut-nodes :  9111 (16.9%)  save 20.25us each  ->  +0.180s
all-nodes : 44739 (83.1%)  cost 10.30us each  ->  -0.461s
net       : -0.281s on a 1.44s search           (-19.5%)
```

An all-node searches every move by definition, so the split penalty hits 83%
of nodes. Cheaper variants also fail: TT-move-first targets only 252 cutoffs
(~0.007s), and killer-first reorders killers ahead of captures — the same
class of change that made 2.1 backfire.

**Both 2.1 and 2.2 were my own earlier recommendations from a profiling
report.** They assumed costs decompose the way they would in a bitboard
engine. In python-chess they do not. The two optimisations that *did* work
won by deleting recomputation, never by restructuring the search. Apply that
filter to any new idea.

### 2.3 Already on the user's do-not list, with prior evidence

Check extensions (tried 5 Sept: depth 5 went 7.0s → 10.4s, no quality gain),
numba, pondering, aspiration windows (tried 8 Sept, unmeasurable), LMR table
rewrite.

---

## 3. Two beliefs that were wrong

- **`draw.pgn`** (up Q+R, drawn by threefold) is **already fixed**. The
  current build finds **Qe7# mate in 1** in that exact position. Historical
  artifact of an older build — do not chase it.
- **The one `Illegal` termination in the CSV was a Win.** That was the
  opponent's (0x88) illegal move. The "zero illegal moves ever" record stands.

---

## 4. Gate noise — read before trusting a timing result

The `depth 4 <= 0.136s` criterion is **inside the run-to-run noise band**.
Unmodified baseline code measured **0.151 / 0.126 / 0.127s** across three
identical runs — it fails the gate on run 1 and passes on 2 and 3 with zero
code change. Depth 7 swung 4.71s–11.24s.

**Run `tools.depths` three times and use the minimum.** Also watch **depth 6**,
which showed ~1.5% spread against depth 4's ~19%. Judging a change on a single
depth-4 sample will discard good work about a third of the time.

---

## 5. What is available to improve, ranked

Verified as real against the current code, not guessed. Elo figures are
rough-order estimates; everything here needs the usual gate.

### Tier A — cheap, low risk, verified present

**A1. TT replacement policy.** `agent.py:861` is an unconditional overwrite:

```python
if len(TT) < TT_MAX_ENTRIES:
    TT[key] = (depth, to_tt(best, ply), flag, best_move)
```

A depth-8 entry gets clobbered by a depth-1 one. There is no aging and no
depth preference, and when full it stops accepting entries entirely. In
practice TT reaches only ~136k entries in a real game (~28 MB at ~303
bytes/entry) so the freeze does not bind, but the always-overwrite does.
Fix: keep the entry if `stored_depth > depth` unless the key differs.
**~10–20 Elo, a few lines, near-zero risk.**

**A2. Use partial iteration results at the root.** `agent.py:940` discards an
aborted iteration entirely (`if not complete: break`). Root moves are ordered
best-first and `search_root` updates `best_move` as it goes, so a partial
depth N+1 often beats a complete depth N. Standard fix: accept the partial
result only if it improved on the previous iteration's best. This matters
*more* now that `ITERATION_COST_FACTOR = 3.0` starts more iterations.
**~10–20 Elo, low risk, needs care around root fail-low.**

**A3. In-tree repetition detection — now nearly free.** Current logic is
`if ply > 0 and key in HISTORY: return 0`. Three problems: only positions
where it was *our* turn are in `HISTORY` (all a FEN can give you); a single
occurrence is scored as a draw; and **repetitions inside the search path are
not detected at all**. Since the key is now threaded through `search`, adding
a path set costs almost nothing. This is the most likely fix for the
"6 of last 10 games shuffled" complaint in `notes.md`.
**~20–30 Elo in won/lost positions, moderate risk — this has failed 4 times
before, so gate it hard.**

**A4. Reverse futility / static null move** at depth ≤3: if
`static_eval − 120*depth >= beta`, return. Two lines, standard, **not** on the
do-not list. **~20–30 Elo.**

### Tier B — real bug, unquantified

**B1. `SHUFFLE_PENALTY` poisons the TT.** `evaluate`/`evaluate_incr` apply a
drift of `(halfmove_clock − 20) * 3` — up to ~240 cp at `halfmove_clock=100`.
But `halfmove_clock` is **not in the TT key**, so the same position at
different clock values shares an entry, and the same position reached by
different paths inside one search gets different evals. Note the old
`polyglot` hash had this too, so it is not a regression from this session —
but it is real. Options: drop the penalty and rely on a fixed A3 instead, or
apply the drift only at the root. **Quantify before changing.**

### Tier C — where the actual Elo is

The engine has PeSTO piece-square tables plus passed/doubled/isolated pawns,
rook files, bishop pair and a 3-file pawn shield. That is it.

**C1. Mobility.** No mobility term at all. Classic **~30–50 Elo**. Cost is
real — roughly 16 `attacks_mask` + popcount per eval, and eval is currently
~14% of runtime, so expect to give back some speed. Measure both sides.

**C2. King safety beyond the pawn shield.** No attacker-count king-danger
term. At this rating band, losing to king attacks is common. Weighted count of
attackers into the king zone is the standard construction. **~40–60 Elo**,
moderate cost.

**C3. Quiescence does not touch the TT** at all. Standard to probe/store
there, but quiescence is 20,071 of 30,701 ordering calls at only 2.2 moves
each, so hashing overhead may not pay. **Measure before building.**

### On the 1900 target

Be straight with the user about this. The work in this session is worth
roughly **+60–80 Elo** (~1400 → ~1480). Tier A + Tier C done well might add
another 100–150. That lands near 1600–1650, not 1900.

The gap is **eval and nodes/sec, not search structure**. 1900 engines search
depth 8–10; this one reaches 6–7. `AGENTS.md` is explicit that numba is how
Python gets fast here, and a numba bitboard movegen is 1–3M nps against the
current ~10–20k — six-plus plies, which dwarfs everything in Tier A–C
combined. That is a multi-day rewrite and was correctly ruled out for the
11 Sept deadline, but it is the only realistic path to 1900. Anything else is
incremental.

---

## 6. Validation state at handoff

```
ruff / mypy                 clean
depths  d4 min 0.088s   d6 min 1.369s        (gate 0.136s)
matedepth  999999 / 999997 / 999995 (11 rows)
repcheck   a7a8 CHECKMATE      mate  KRvK mates
incrcheck  0 mismatches        deltacheck  0 mismatches
arena vs random/greedy/minimax/numba @10s base   24/24, all checkmate, 0 flags
robustness  60 random positions x clocks {120s..0ms}: 0 illegal, 0 over budget
            worst overshoot +0.003s;  clock 0ms -> legal move in 0.003s
import time 0.001s (platform budget 60s)
submission.zip  8,491 bytes, agent.py at root, 31,244 unzipped
```
