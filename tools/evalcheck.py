import chess

import agent

# board = chess.Board("4k3/8/4K3/4B3/8/8/8/5Q2 w - - 0 1")
board = chess.Board("r3k3/R7/p2B1Q2/3N1B2/8/P4N2/P1P2PPP/5RK1 w - - 7 34")
print("static eval:", agent.evaluate(board))
print()
for move in board.legal_moves:
    board.push(move)
    print(f"{move.uci()}  {-agent.evaluate(board):>6}")
    board.pop()