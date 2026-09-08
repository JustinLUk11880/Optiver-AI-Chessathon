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

## Open
- /12 vs /15 clock: /12 has 4 bad games. Check CSV, revert if losses continue.
- Repetition fix needs ladder confirmation (6 of last 10 games shuffled).
- README not written.