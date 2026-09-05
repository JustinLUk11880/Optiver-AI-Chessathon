import chess

import agent

board = chess.Board("r3k3/R7/p2B1Q2/3N1B2/8/P4N2/P1P2PPP/5RK1 w - - 7 34")

agent.TT.clear()
print("cold TT:", agent.get_move(board.fen(), 30_000))

print("warm TT:", agent.get_move(board.fen(), 30_000))
print("TT size:", len(agent.TT))

agent.TT.clear()
clock = agent.Clock(10.0)
for d in range(1, 7):
    agent.TT.clear()
    move, complete = agent.search_root(board, d, agent.Clock(10.0))
    print(f"depth {d}: {move} complete={complete}")