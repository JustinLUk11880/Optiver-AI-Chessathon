import chess

import agent

CASES = [
    ("white passer on 7th", "8/4P3/8/8/8/8/8/4K2k w - - 0 1"),
    ("white pawn blocked",  "8/4P3/3p4/8/8/8/8/4K2k w - - 0 1"),
    ("white passer on 2nd", "8/8/8/8/8/8/4P3/4K2k w - - 0 1"),
    ("black passer on 2nd", "4k2K/8/8/8/8/8/4p3/8 b - - 0 1"),
]

for name, fen in CASES:
    board = chess.Board(fen)
    print(f"{name:>22}: passed={agent.passed_pawns(board)}  eval={agent.evaluate(board)}")