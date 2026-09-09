import chess

import agent

board = chess.Board("r3k3/R7/p2B1Q2/3N1B2/8/P4N2/P1P2PPP/5RK1 w - - 7 34")

agent.TT.clear()
clock = agent.Clock(60.0)

mg = eg = phase = 0
for sq, piece in board.piece_map().items():
    off = (384 if piece.color else 0) + piece.piece_type * 64 + sq
    if piece.color:
        mg += agent.MG_TABLE[off]
        eg += agent.EG_TABLE[off]
    else:
        mg -= agent.MG_TABLE[off]
        eg -= agent.EG_TABLE[off]
    phase += agent.PHASE_WEIGHT[piece.piece_type]

rows = []
for move in list(board.legal_moves):
    d_mg, d_eg, d_phase = agent.move_delta(board, move)
    board.push(move)
    score = -agent.search(
        board, 5, -agent.MATE, agent.MATE, 1, clock,
        mg + d_mg, eg + d_eg, phase + d_phase,
    )
    board.pop()
    rows.append((score, move.uci()))

rows.sort(reverse=True)
for score, uci in rows:
    plies = (agent.MATE - abs(score) + 1) // 2
    note = f"MATE in {plies}" if abs(score) > 900_000 else ""
    print(f"{uci}  {score}  {note}")