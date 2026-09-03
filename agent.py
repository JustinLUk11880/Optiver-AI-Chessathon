"""The submission entrypoint. The platform imports this file and calls get_move."""
# package and test:
# uv run python -m harness.play --white . --black baselines/greedy
# uv run python -m harness.package

import random

import chess

PIECE_VALUE = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
}

MATE = 1_000_000
DEPTH = 4


def evaluate(board: chess.Board) -> int:
    """Material balance in centipawns, from the side to move's point of view."""
    mover = board.turn
    return sum(
        value * (len(board.pieces(piece, mover)) - len(board.pieces(piece, not mover)))
        for piece, value in PIECE_VALUE.items()
    )


def search(board: chess.Board, depth: int, alpha: int, beta: int, ply: int) -> int:
    moves = list(board.legal_moves)
    if not moves:
        return -MATE + ply if board.is_check() else 0
    if depth == 0:
        return evaluate(board)

    best = -MATE
    for move in moves:
        board.push(move)
        score = -search(board, depth - 1, -beta, -alpha, ply + 1)
        board.pop()
        if score > best:
            best = score
        if best > alpha:
            alpha = best
        if alpha >= beta:
            break
    return best


def search_root(board: chess.Board, depth: int) -> chess.Move:
    alpha = -MATE - 1
    best: list[chess.Move] = []
    for move in board.legal_moves:
        board.push(move)
        score = -search(board, depth - 1, -MATE, -alpha, 1)
        board.pop()
        if score > alpha:
            alpha = score
            best = [move]
        elif score == alpha:
            best.append(move)
    return random.choice(best)


def get_move(fen: str, time_left_ms: int) -> str:
    board = chess.Board(fen)
    return search_root(board, DEPTH).uci()
