import chess
import numpy as np

import agent

FENS = [
    chess.STARTING_FEN,
    "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
    "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
    "r3k3/R7/p2B1Q2/3N1B2/8/P4N2/P1P2PPP/5RK1 w - - 7 34",
    "4k3/8/8/8/8/8/8/4K2R w K - 0 1",
]
import time

board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4")
white = np.uint64(board.occupied_co[chess.WHITE])

start = time.perf_counter()
for _ in range(20000):
    for piece_type, bb in (
        (1, board.pawns), (2, board.knights), (3, board.bishops),
        (4, board.rooks), (5, board.queens), (6, board.kings),
    ):
        agent._pst_side(np.uint64(bb & board.occupied), piece_type, white,
                        agent.MG_ARRAY, agent.EG_ARRAY)
print(f"jit: {time.perf_counter() - start:.3f}s")

start = time.perf_counter()
for _ in range(20000):
    agent.evaluate(board)
print(f"py evaluate: {time.perf_counter() - start:.3f}s")

for fen in FENS:
    board = chess.Board(fen)
    white = np.uint64(board.occupied_co[chess.WHITE])
    mg = eg = phase = 0
    for piece_type, bb in (
        (1, board.pawns), (2, board.knights), (3, board.bishops),
        (4, board.rooks), (5, board.queens), (6, board.kings),
    ):
        m, e, n = agent._pst_side(
            np.uint64(bb & board.occupied), piece_type, white, agent.MG_ARRAY, agent.EG_ARRAY
        )
        mg += m
        eg += e
        phase += agent.PHASE_WEIGHT[piece_type] * n

    mg2 = eg2 = phase2 = 0
    for square, piece in board.piece_map().items():
        offset = (384 if piece.color else 0) + piece.piece_type * 64 + square
        if piece.color:
            mg2 += agent.MG_TABLE[offset]
            eg2 += agent.EG_TABLE[offset]
        else:
            mg2 -= agent.MG_TABLE[offset]
            eg2 -= agent.EG_TABLE[offset]
        phase2 += agent.PHASE_WEIGHT[piece.piece_type]

    ok = (mg, eg, phase) == (mg2, eg2, phase2)
    print(f"{'OK ' if ok else 'BAD'} jit=({mg},{eg},{phase}) py=({mg2},{eg2},{phase2})")