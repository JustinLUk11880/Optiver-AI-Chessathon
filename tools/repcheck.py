import chess

import agent

board = chess.Board("r3k3/R7/p2B1Q2/3N1B2/8/P4N2/P1P2PPP/5RK1 w - - 7 34")
for i in range(12):
    if board.is_game_over():
        break
    move = chess.Move.from_uci(agent.get_move(board.fen(), 30_000))
    board.push(move)
    print(f"{i}: {move.uci()}")
    if board.is_game_over():
        break
    board.push(next(iter(board.legal_moves)))
print(board.outcome())