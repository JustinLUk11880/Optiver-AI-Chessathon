# AI Chessathon — state as of 7 Sept 2026

## Context
UK student, solo, team "IDK". Uploads close 11 Sept 11:00.
Qualification = 13-round Swiss over locked builds, 50 London seats. Ladder only seeds it.
Rating ~1450-1550, rank ~250/356. 50th place ~1900.

## Environment
Windows, C:\GitHub\Optiver-AI-Chessathon, uv (not pip/venv).
`uv run python -m harness.arena --opponent X --games N --base-ms M`
`uv run python -m harness.package` → submission.zip (agent.py only)
Gate: ruff + mypy + arena vs random @5000ms.

## Shipped in agent.py
Search: alpha-beta negamax, iterative deepening (budget = remaining/12,
capped at 25% remaining), quiescence (fail-soft, ply-adjusted mates),
MVV-LVA + TT move + killers + history ordering, transposition table with
exact/lower/upper flags, null-move pruning.
Eval: tapered PeSTO piece-square tables, mop-up endgame, passed pawns,
king pawn shield, bishop pair, rook open/half-open file, doubled/isolated pawns.
All consolidated into one evaluate() pass.

## Test tools (tools/)
depths.py — per-ply node cost. Depth 4 ≈ 0.81s, depth 6 completes.
matedepth.py — mate-in-N scores. Must be 999999 / 999997 / 999995.
repcheck.py — conversion in won position. Must mate in 1.
mate.py — KRvK. bench.py — perft.
100-game arena vs prev is USELESS (colour bias, 35% draws) — don't use.
All 4 baselines at 100%.

## Bugs that cost the most
1. File not saving — always `cat agent.py` after editing before testing.
2. quiesce returned -MATE without +ply → all mates tied → shuffling.
3. Root tie-break admitted fail-low moves scoring == alpha.
4. LMR attempt broke depths 10x; reverted, do not retry.
5. Repetition: 4 failed attempts. Current live version has
   `if ply > 0 and key in HISTORY: return 0` in search + HISTORY.add in get_move.
   Unverified on ladder.

## Session 9 Sept (Claude) — measured, not guessed

Clock was the big one. Across the 79-game CSV the engine spent a median 53%
of its fair per-move share and never finished below 24.9s left. Cause was
`elapsed + last_depth_s * 8` in the ID loop: real iteration cost ratio is
median 2.5 / p90 4.8, so it quit one iteration early nearly every move.
Now ITERATION_COST_FACTOR = 3.0. Mean depth 5.56 -> 6.11.
Then TIME_DIVISOR = 10 with TIME_RESERVE = 5s: clock follows r' = 0.9r + 1.0,
settles at a 10s floor (old reserve-less /12 settled at 6s). Depth -> 6.33.
So /12 vs /15 is settled: neither, use a reserve. Not a divisor question.

Things that did NOT work, with evidence — do not retry:
- SEE out of move ordering (MVV-LVA instead). Per-capture scoring got 8.5x
  cheaper but depth 6 went 1.731 -> 1.812s, depth 4 failed the gate on all
  3 runs. SEE is load-bearing: it sorts losing captures BELOW killers, and
  losing that ordering costs more nodes than the arithmetic saves.
- Staged move generation. Cutoff stats look ideal (94% of cutoffs on move 0,
  96.6% of generation at cut-nodes wasted) but python-chess recomputes
  pins/checkers per call, so captures+quiets separately = 39.58us vs 29.28us
  combined. All-nodes are 83% of nodes and need everything. Model: -19.5%.

What did work: pawn-structure cache (92% hit rate, ~4k entries, depth 6
-11.2%) and an incremental zobrist key (polyglot hash was 13.7% of runtime
at 13.58us/call). Both won by deleting recomputation, not by restructuring
the search. Depth 6 overall 1.727 -> ~1.40s.

draw.pgn (Q+R up, threefold) is FIXED in the current build — it now finds
Qe7# there. Historical artifact, don't chase it.
The one "Illegal" termination in the CSV was a Win: the opponent's illegal
move, not ours. Clean record stands.

## Open
- Repetition fix needs ladder confirmation (6 of last 10 games shuffled).
- Eval only has PeSTO + passed/doubled/isolated/rook-file/bishop-pair/shield.
  No mobility, no real king safety. That is where the remaining Elo is, and
  it is an eval problem, not a search problem.
- SHUFFLE_PENALTY makes eval depend on halfmove_clock, which is NOT in the TT
  key. Same position at different halfmove_clock shares an entry. Unquantified.
- README not written.