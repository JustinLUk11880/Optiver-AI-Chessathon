import time

import chess


def perft(board: chess.Board, depth: int) -> int:
    if depth == 0:
        return 1
    total = 0
    for move in board.legal_moves:
        board.push(move)
        total += perft(board, depth - 1)
        board.pop()
    return total


CASES = [
    ("opening", chess.STARTING_FEN, 4),
    ("middlegame", "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4", 3),
    ("endgame", "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1", 4),
]

for name, fen, depth in CASES:
    board = chess.Board(fen)
    start = time.perf_counter()
    nodes = perft(board, depth)
    elapsed = time.perf_counter() - start
    print(f"{name:>12} d{depth}: {nodes:>9,} nodes  {elapsed:5.2f}s  {nodes / elapsed:>9,.0f} nps")
