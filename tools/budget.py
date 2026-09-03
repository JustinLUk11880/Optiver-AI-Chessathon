import sys
import time

import chess

sys.path.insert(0, ".")

import agent

board = chess.Board()
for clock_ms in (120_000, 10_000, 5_000, 2_000, 500):
    start = time.perf_counter()
    agent.get_move(board.fen(), clock_ms)
    used = time.perf_counter() - start
    print(f"clock {clock_ms:>7}ms  used {used:6.3f}s")