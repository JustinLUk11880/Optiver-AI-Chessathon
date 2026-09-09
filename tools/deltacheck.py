import random

import chess

import agent


def raw(board):
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
    return mg, eg, phase


random.seed(7)
bad = 0
for _game in range(400):
    board = chess.Board()
    for _ in range(random.randint(1, 80)):
        moves = list(board.legal_moves)
        if not moves:
            break
        move = random.choice(moves)
        before = raw(board)
        delta = agent.move_delta(board, move)
        board.push(move)
        after = raw(board)
        expected = tuple(b + d for b, d in zip(before, delta, strict=True))        
        if expected != after:
            bad += 1
            if bad <= 5:
                print(f"MISMATCH {move.uci()} exp={expected} got={after} {board.fen()}")
print(f"{bad} mismatches")