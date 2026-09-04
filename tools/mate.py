
import chess

import agent

board = chess.Board("8/8/8/4k3/8/8/8/4K2R w K - 0 1")
for _ply in range(120):
    if board.is_game_over():
        break
    if board.turn == chess.WHITE:
        move = chess.Move.from_uci(agent.get_move(board.fen(), 30_000))
    else:
        move = max(board.legal_moves, key=lambda m: len(list(board.legal_moves)))
    board.push(move)
print(f"plies {board.ply()}  outcome {board.outcome()}")
print(board)
