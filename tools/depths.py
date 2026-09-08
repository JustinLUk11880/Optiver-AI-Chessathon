import sys
import time

sys.path.insert(0, ".")
import chess

import agent

board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4")
clock = agent.Clock(30.0)
for d in range(1, 10):
    t = time.perf_counter()
    move, complete = agent.search_root(board, d, clock)
    print(f"depth {d}: {time.perf_counter()-t:6.3f}s  {move}  complete={complete}")
