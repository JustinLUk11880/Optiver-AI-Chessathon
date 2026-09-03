import sys
import time

import chess

sys.path.insert(0, ".")

import agent

board = chess.Board()
clock = agent.Clock(3.0)
start = time.perf_counter()
try:
    result = agent.search_root(board, 4, clock)
    print(f"depth 4 ok: {result}  {time.perf_counter() - start:.3f}s")
except Exception as exc:
    print(f"raised {type(exc).__name__}: {exc}  after {time.perf_counter() - start:.3f}s")