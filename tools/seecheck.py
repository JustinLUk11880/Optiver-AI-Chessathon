import chess

import agent

CASES = [
    ("free pawn", "4k3/8/8/3p4/8/8/8/3RK3 w - - 0 1", "d1d5", 100),
    ("defended pawn", "4k3/8/2p5/3p4/8/8/8/3RK3 w - - 0 1", "d1d5", -400),
    ("good trade", "4k3/8/8/3q4/8/8/8/3RK3 w - - 0 1", "d1d5", 900),
    ("bad grab", "3rk3/8/8/3p4/8/8/8/3RK3 w - - 0 1", "d1d5", -400),
]

for name, fen, uci, expected in CASES:
    board = chess.Board(fen)
    move = chess.Move.from_uci(uci)
    got = agent.see_gain(board, move)
    print(f"{'OK ' if got == expected else 'BAD'} {name:>15}: got {got}, expected {expected}")