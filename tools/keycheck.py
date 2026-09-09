"""Verify the engine's Zobrist key.

agent's key is its own random scheme, not polyglot-compatible, so numeric
equality with chess.polyglot is meaningless. What matters is the equivalence
relation it induces, and only one direction is safety-critical:

  same agent key  => genuinely the same position   (violation corrupts the TT)
  same polyglot key but different agent key        (only a missed transposition)

The second direction is expected to differ: polyglot hashes the en-passant
file only when a pawn can actually capture, while agent hashes it whenever
ep_square is set. That splits some positions polyglot would merge, which is
safe.
"""

import random
import sys

import chess
import chess.polyglot

sys.path.insert(0, ".")
import agent

GAMES = 600
random.seed(20260909)

drift = 0
pushes = 0
by_agent: dict[int, tuple[str, bool, int, int | None]] = {}
by_poly: dict[int, tuple[str, bool, int, int | None]] = {}
agent_collisions = 0
missed_transpositions = 0
kinds = {"castle": 0, "ep": 0, "promo": 0, "capture": 0, "quiet": 0, "null": 0}


def signature(board: chess.Board) -> tuple[str, bool, int, int | None]:
    """The position identity a transposition table must not confuse."""
    return (
        board.board_fen(),
        board.turn,
        board.castling_rights,
        board.ep_square if board.has_legal_en_passant() else None,
    )


for _game in range(GAMES):
    board = chess.Board()
    key = agent.placement_key(board)
    for _ in range(random.randint(0, 100)):
        moves = list(board.legal_moves)
        if not moves:
            break
        move = random.choice(moves)
        if board.is_castling(move):
            kinds["castle"] += 1
        elif board.is_en_passant(move):
            kinds["ep"] += 1
        elif move.promotion:
            kinds["promo"] += 1
        elif board.piece_at(move.to_square):
            kinds["capture"] += 1
        else:
            kinds["quiet"] += 1

        _, _, _, d_key = agent.move_delta(board, move)
        board.push(move)
        key ^= d_key
        pushes += 1

        # 1. the incremental placement key must equal a from-scratch recompute
        if key != agent.placement_key(board):
            drift += 1
            if drift <= 3:
                print(f"DRIFT after {move.uci()}: {board.fen()}")

        # 2. and the full key must equal placement ^ state
        if (key ^ agent.state_key(board)) != agent.full_key(board):
            drift += 1

        # 3. equivalence relation vs polyglot
        sig = signature(board)
        ak = agent.full_key(board)
        pk = chess.polyglot.zobrist_hash(board)
        if by_agent.setdefault(ak, sig) != sig:
            agent_collisions += 1
            if agent_collisions <= 3:
                print(f"AGENT KEY COLLISION: {by_agent[ak]} vs {sig}")
        if by_poly.setdefault(pk, sig) != sig:
            print(f"POLYGLOT COLLISION (reference itself): {by_poly[pk]} vs {sig}")

    # null move must keep placement and change state
    if board.legal_moves and not board.is_check():
        before_p, before_f = agent.placement_key(board), agent.full_key(board)
        board.push(chess.Move.null())
        kinds["null"] += 1
        if agent.placement_key(board) != before_p or agent.full_key(board) == before_f:
            drift += 1
            print(f"NULL MOVE key wrong: {board.fen()}")
        board.pop()

# polyglot merges some positions agent splits; count them
poly_groups: dict[int, set[int]] = {}
for _game in range(60):
    board = chess.Board()
    for _ in range(random.randint(0, 90)):
        moves = list(board.legal_moves)
        if not moves:
            break
        board.push(random.choice(moves))
        poly_groups.setdefault(chess.polyglot.zobrist_hash(board), set()).add(
            agent.full_key(board)
        )
missed_transpositions = sum(len(v) - 1 for v in poly_groups.values())

print(f"games {GAMES}, pushes {pushes}, distinct positions {len(by_agent)}")
print(f"move types: {kinds}")
print()
print(f"incremental key drift vs from-scratch : {drift}")
print(f"agent key collisions (UNSAFE if > 0)   : {agent_collisions}")
print(f"positions polyglot merges that agent splits (harmless): "
      f"{missed_transpositions} / {sum(len(v) for v in poly_groups.values())}")
print()
print("PASS" if drift == 0 and agent_collisions == 0 else "FAIL")
