import random

import chess

import agent

random.seed(1)
bad = 0
for _game in range(300):
    board = chess.Board()
    for _ in range(random.randint(0, 70)):
        moves = list(board.legal_moves)
        if not moves:
            break
        board.push(random.choice(moves))
    if agent.evaluate(board) != agent.evaluate_old(board):
        bad += 1
        if bad <= 3:
            print(f"MISMATCH {agent.evaluate(board)} vs {agent.evaluate_old(board)}: {board.fen()}")
print(f"{bad} mismatches over 300 positions")