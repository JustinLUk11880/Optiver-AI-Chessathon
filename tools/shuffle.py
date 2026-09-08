import chess

import agent

BASE = "8/5k2/8/8/8/2R5/5K2/8 w - - {} 60"

for clock in (0, 20, 40, 60, 80):
    board = chess.Board(BASE.format(clock))
    print(f"halfmove {clock:>3}: eval {agent.evaluate(board):>5}")