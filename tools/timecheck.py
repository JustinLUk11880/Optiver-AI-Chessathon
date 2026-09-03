import time

import chess

import agent

for name, fen in [
    ("opening", chess.STARTING_FEN),
    ("middlegame", "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"),
]:
    start = time.perf_counter()
    move = agent.get_move(fen, 120_000)
    print(f"{name:>12}: {move}  {time.perf_counter() - start:5.2f}s")