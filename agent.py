import random
import time

import chess

PIECE_VALUE = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
}

MATE = 1_000_000
MAX_DEPTH = 24
CHECK_INTERVAL = 63


class TimeUp(Exception):
    pass


class Clock:
    def __init__(self, budget_s: float) -> None:
        self.deadline = time.perf_counter() + budget_s
        self.counter = 0

    def check(self) -> None:
        self.counter += 1
        if self.counter & CHECK_INTERVAL == 0 and time.perf_counter() > self.deadline:
            raise TimeUp


def evaluate(board: chess.Board) -> int:
    mover = board.turn
    return sum(
        value * (len(board.pieces(piece, mover)) - len(board.pieces(piece, not mover)))
        for piece, value in PIECE_VALUE.items()
    )


def search(board: chess.Board, depth: int, alpha: int, beta: int, ply: int, clock: Clock) -> int:
    clock.check()
    moves = list(board.legal_moves)
    if not moves:
        return -MATE + ply if board.is_check() else 0
    if depth == 0:
        return evaluate(board)

    best = -MATE
    for move in moves:
        board.push(move)
        score = -search(board, depth - 1, -beta, -alpha, ply + 1, clock)
        board.pop()
        if score > best:
            best = score
        if best > alpha:
            alpha = best
        if alpha >= beta:
            break
    return best


def search_root(board: chess.Board, depth: int, clock: Clock) -> tuple[chess.Move | None, bool]:
    alpha = -MATE - 1
    best: list[chess.Move] = []
    for move in list(board.legal_moves):
        board.push(move)
        try:
            score = -search(board, depth - 1, -MATE, -alpha, 1, clock)
        except TimeUp:
            board.pop()
            return (random.choice(best) if best else None), False
        board.pop()
        if score > alpha:
            alpha = score
            best = [move]
        elif score == alpha:
            best.append(move)
    return (random.choice(best) if best else None), True


def get_move(fen: str, time_left_ms: int) -> str:
    board = chess.Board(fen)
    fallback = next(iter(board.legal_moves)).uci()

    try:
        remaining_s = time_left_ms / 1000.0
        budget = max(0.01, min(remaining_s / 30.0, remaining_s * 0.1))
        start = time.perf_counter()
        clock = Clock(budget)
        chosen = fallback
        last_depth_s = 0.0

        for depth in range(1, MAX_DEPTH):
            elapsed = time.perf_counter() - start
            if depth > 2 and elapsed + last_depth_s * 6 > budget:
                break
            depth_start = time.perf_counter()
            move, complete = search_root(board, depth, clock)
            if move is not None:
                chosen = move.uci()
            if not complete:
                break
            last_depth_s = time.perf_counter() - depth_start

        return chosen
    except Exception:
        return fallback
