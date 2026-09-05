import chess
import chess.pgn

with open("draw.pgn") as handle:
    game = chess.pgn.read_game(handle)

board = game.board()
seen: dict[str, int] = {}
for move in game.mainline_moves():
    board.push(move)
    key = board.board_fen() + str(board.turn)
    seen[key] = seen.get(key, 0) + 1
    if seen[key] >= 2 and board.turn == chess.WHITE:
        print(f"repeat #{seen[key]} at ply {board.ply()}")
        print(board.fen())