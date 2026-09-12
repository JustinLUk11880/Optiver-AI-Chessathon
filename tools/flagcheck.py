import sys
import time

import chess

sys.path.insert(0, ".")
import agent

board = chess.Board()
clock_ms = 10_000
ply = 0

while not board.is_game_over() and ply < 60:
    start = time.perf_counter()
    move = agent.get_move(board.fen(), clock_ms)
    used = time.perf_counter() - start
    clock_ms -= used * 1000
    clock_ms += 100
    print(f"ply {ply:>3}  used {used:5.3f}s  clock left {clock_ms/1000:6.3f}s")
    if clock_ms <= 0:
        print("FLAGGED")
        break
    board.push(chess.Move.from_uci(move))
    if board.is_game_over():
        break
    board.push(next(iter(board.legal_moves)))
    ply += 2

print(f"finished at ply {ply}, clock left {clock_ms/1000:.3f}s, outcome {board.outcome()}")