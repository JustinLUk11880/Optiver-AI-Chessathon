import chess

import agent

board = chess.Board("r3k3/R7/p2B1Q2/3N1B2/8/P4N2/P1P2PPP/5RK1 w - - 7 34")

for depth in (4, 5, 6):
    agent.TT.clear()
    clock = agent.Clock(20.0)
    alpha = -agent.MATE - 1
    rows = []
    for move in agent.order_moves(board, list(board.legal_moves)):
        board.push(move)
        score = -agent.search(board, depth - 1, -agent.MATE, agent.MATE, 1, clock)
        board.pop()
        rows.append((score, move.uci()))
    rows.sort(reverse=True)
    print(f"--- depth {depth} ---")
    for score, uci in rows[:6]:
        print(f"  {uci}  {score}")