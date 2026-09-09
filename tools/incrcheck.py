import random

import chess

import agent

random.seed(11)
bad = 0
for _game in range(300):
    board = chess.Board()
    for _ in range(random.randint(0, 70)):
        moves = list(board.legal_moves)
        if not moves:
            break
        board.push(random.choice(moves))
    mg = eg = phase = 0
    for square, piece in board.piece_map().items():
        offset = (384 if piece.color else 0) + piece.piece_type * 64 + square
        if piece.color:
            mg += agent.MG_TABLE[offset]
            eg += agent.EG_TABLE[offset]
        else:
            mg -= agent.MG_TABLE[offset]
            eg -= agent.EG_TABLE[offset]
        phase += agent.PHASE_WEIGHT[piece.piece_type]
    if agent.evaluate_incr(board, mg, eg, phase) != agent.evaluate(board):
        bad += 1
        if bad <= 3:
            print(f"MISMATCH {board.fen()}")
print(f"{bad} mismatches over 300 positions")