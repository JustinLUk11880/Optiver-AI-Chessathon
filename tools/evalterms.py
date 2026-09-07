import chess

import agent

# CASES = [
#     ("white passer on 7th", "8/4P3/8/8/8/8/8/4K2k w - - 0 1"),
#     ("white pawn blocked",  "8/4P3/3p4/8/8/8/8/4K2k w - - 0 1"),
#     ("white passer on 2nd", "8/8/8/8/8/8/4P3/4K2k w - - 0 1"),
#     ("black passer on 2nd", "4k2K/8/8/8/8/8/4p3/8 b - - 0 1"),
    
# ]

# CASES = [
#     ("castled, full shield", "4k3/8/8/8/8/8/5PPP/6K1 w - - 0 1"),
#     ("castled, g-pawn gone", "4k3/8/8/8/8/8/5P1P/6K1 w - - 0 1"),
#     ("castled, all gone",    "4k3/8/8/8/8/8/8/6K1 w - - 0 1"),
# ]

# CASES = [
#     ("W full shield", "rnbqkbnr/pppppppp/8/8/8/8/5PPP/6K1 w - - 0 1"),
#     ("W g-pawn gone", "rnbqkbnr/pppppppp/8/8/8/8/5P1P/6K1 w - - 0 1"),
#     ("W no shield",   "rnbqkbnr/pppppppp/8/8/8/8/8/6K1 w - - 0 1"),
# ]
CASES = [
    ("bishop pair",   "4k3/8/8/8/8/8/8/2B1KB2 w - - 0 1"),
    ("two knights",   "4k3/8/8/8/8/8/8/2N1KN2 w - - 0 1"),
    ("rook open",     "4k3/8/8/8/8/8/8/3RK3 w - - 0 1"),
    ("rook blocked",  "4k3/8/8/8/8/8/3P4/3RK3 w - - 0 1"),
    ("doubled pawns", "4k3/8/8/8/8/3P4/3P4/4K3 w - - 0 1"),
    ("split pawns",   "4k3/8/8/8/8/2P5/3P4/4K3 w - - 0 1"),
    ("isolated pawn", "4k3/8/8/8/8/8/3P4/4K3 w - - 0 1"),
]

for name, fen in CASES:
    board = chess.Board(fen)
    print(f"{name:>16}: structure={agent.structure(board)}")

# for name, fen in CASES:
#     board = chess.Board(fen)
#     # print(f"{name:>22}: passed={agent.passed_pawns(board)}  eval={agent.evaluate(board)}")
#     print(f"{name:>22}: shield={agent.king_safety(board)}  eval={agent.evaluate(board)}")