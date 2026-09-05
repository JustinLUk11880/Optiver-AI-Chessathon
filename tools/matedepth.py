import chess

import agent

board = chess.Board("r3k3/R7/p2B1Q2/3N1B2/8/P4N2/P1P2PPP/5RK1 w - - 7 34")
agent.TT.clear()
clock = agent.Clock(30.0)
rows = []
for move in list(board.legal_moves):
    board.push(move)
    score = -agent.search(board, 5, -agent.MATE, agent.MATE, 1, clock)
    board.pop()
    rows.append((score, move.uci()))
rows.sort(reverse=True)
for score, uci in rows:
    plies = (agent.MATE - abs(score) + 1) // 2
    note = f"MATE in {plies}" if abs(score) > 900_000 else ""
    print(f"{uci}  {score}  {note}")