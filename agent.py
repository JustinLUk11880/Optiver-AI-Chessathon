"""The submission entrypoint. The platform imports this file and calls get_move."""

import random
import time

import chess

MATE = 1_000_000
MATE_BOUND = MATE - 1000
MAX_DEPTH = 24
CHECK_INTERVAL = 63

MOPUP_PHASE = 6
MOPUP_MARGIN = 400

TT_EXACT = 0
TT_LOWER = 1
TT_UPPER = 2
TT_MAX_ENTRIES = 2_000_000

NULL_MIN_PHASE = 4
DELTA_MARGIN = 200
SHUFFLE_PENALTY = 3
KING_SHIELD_PENALTY = 18

PIECE_VALUE_MG = {
    chess.PAWN: 82,
    chess.KNIGHT: 337,
    chess.BISHOP: 365,
    chess.ROOK: 477,
    chess.QUEEN: 1025,
    chess.KING: 0,
}

PIECE_VALUE_EG = {
    chess.PAWN: 94,
    chess.KNIGHT: 281,
    chess.BISHOP: 297,
    chess.ROOK: 512,
    chess.QUEEN: 936,
    chess.KING: 0,
}

PHASE_WEIGHT = {
    chess.PAWN: 0,
    chess.KNIGHT: 1,
    chess.BISHOP: 1,
    chess.ROOK: 2,
    chess.QUEEN: 4,
    chess.KING: 0,
}

MVV_LVA_VALUE = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 300,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

TOTAL_PHASE = 24

PAWN_MG = [
      0,   0,   0,   0,   0,   0,   0,   0,
     98, 134,  61,  95,  68, 126,  34, -11,
     -6,   7,  26,  31,  65,  56,  25, -20,
    -14,  13,   6,  21,  23,  12,  17, -23,
    -27,  -2,  -5,  12,  17,   6,  10, -25,
    -26,  -4,  -4, -10,   3,   3,  33, -12,
    -35,  -1, -20, -23, -15,  24,  38, -22,
      0,   0,   0,   0,   0,   0,   0,   0,
]

PAWN_EG = [
      0,   0,   0,   0,   0,   0,   0,   0,
    178, 173, 158, 134, 147, 132, 165, 187,
     94, 100,  85,  67,  56,  53,  82,  84,
     32,  24,  13,   5,  -2,   4,  17,  17,
     13,   9,  -3,  -7,  -7,  -8,   3,  -1,
      4,   7,  -6,   1,   0,  -5,  -1,  -8,
     13,   8,   8,  10,  13,   0,   2,  -7,
      0,   0,   0,   0,   0,   0,   0,   0,
]

KNIGHT_MG = [
   -167, -89, -34, -49,  61, -97, -15,-107,
    -73, -41,  72,  36,  23,  62,   7, -17,
    -47,  60,  37,  65,  84, 129,  73,  44,
     -9,  17,  19,  53,  37,  69,  18,  22,
    -13,   4,  16,  13,  28,  19,  21,  -8,
    -23,  -9,  12,  10,  19,  17,  25, -16,
    -29, -53, -12,  -3,  -1,  18, -14, -19,
   -105, -21, -58, -33, -17, -28, -19, -23,
]

KNIGHT_EG = [
    -58, -38, -13, -28, -31, -27, -63, -99,
    -25,  -8, -25,  -2,  -9, -25, -24, -52,
    -24, -20,  10,   9,  -1,  -9, -19, -41,
    -17,   3,  22,  22,  22,  11,   8, -18,
    -18,  -6,  16,  25,  16,  17,   4, -18,
    -23,  -3,  -1,  15,  10,  -3, -20, -22,
    -42, -20, -10,  -5,  -2, -20, -23, -44,
    -29, -51, -23, -15, -22, -18, -50, -64,
]

BISHOP_MG = [
    -29,   4, -82, -37, -25, -42,   7,  -8,
    -26,  16, -18, -13,  30,  59,  18, -47,
    -16,  37,  43,  40,  35,  50,  37,  -2,
     -4,   5,  19,  50,  37,  37,   7,  -2,
     -6,  13,  13,  26,  34,  12,  10,   4,
      0,  15,  15,  15,  14,  27,  18,  10,
      4,  15,  16,   0,   7,  21,  33,   1,
    -33,  -3, -14, -21, -13, -12, -39, -21,
]

BISHOP_EG = [
    -14, -21, -11,  -8,  -7,  -9, -17, -24,
     -8,  -4,   7, -12,  -3, -13,  -4, -14,
      2,  -8,   0,  -1,  -2,   6,   0,   4,
     -3,   9,  12,   9,  14,  10,   3,   2,
     -6,   3,  13,  19,   7,  10,  -3,  -9,
    -12,  -3,   8,  10,  13,   3,  -7, -15,
    -14, -18,  -7,  -1,   4,  -9, -15, -27,
    -23,  -9, -23,  -5,  -9, -16,  -5, -17,
]

ROOK_MG = [
     32,  42,  32,  51,  63,   9,  31,  43,
     27,  32,  58,  62,  80,  67,  26,  44,
     -5,  19,  26,  36,  17,  45,  61,  16,
    -24, -11,   7,  26,  24,  35,  -8, -20,
    -36, -26, -12,  -1,   9,  -7,   6, -23,
    -45, -25, -16, -17,   3,   0,  -5, -33,
    -44, -16, -20,  -9,  -1,  11,  -6, -71,
    -19, -13,   1,  17,  16,   7, -37, -26,
]

ROOK_EG = [
     13,  10,  18,  15,  12,  12,   8,   5,
     11,  13,  13,  11,  -3,   3,   8,   3,
      7,   7,   7,   5,   4,  -3,  -5,  -3,
      4,   3,  13,   1,   2,   1,  -1,   2,
      3,   5,   8,   4,  -5,  -6,  -8, -11,
     -4,   0,  -5,  -1,  -7, -12,  -8, -16,
     -6,  -6,   0,   2,  -9,  -9, -11,  -3,
     -9,   2,   3,  -1,  -5, -13,   4, -20,
]

QUEEN_MG = [
    -28,   0,  29,  12,  59,  44,  43,  45,
    -24, -39,  -5,   1, -16,  57,  28,  54,
    -13, -17,   7,   8,  29,  56,  47,  57,
    -27, -27, -16, -16,  -1,  17,  -2,   1,
     -9, -26,  -9, -10,  -2,  -4,   3,  -3,
    -14,   2, -11,  -2,  -5,   2,  14,   5,
    -35,  -8,  11,   2,   8,  15,  -3,   1,
     -1, -18,  -9,  10, -15, -25, -31, -50,
]

QUEEN_EG = [
     -9,  22,  22,  27,  27,  19,  10,  20,
    -17,  20,  32,  41,  58,  25,  30,   0,
    -20,   6,   9,  49,  47,  35,  19,   9,
      3,  22,  24,  45,  57,  40,  57,  36,
    -18,  28,  19,  47,  31,  34,  39,  23,
    -16, -27,  15,   6,   9,  17,  10,   5,
    -22, -23, -30, -16, -16, -23, -36, -32,
    -33, -28, -22, -43,  -5, -32, -20, -41,
]

KING_MG = [
    -65,  23,  16, -15, -56, -34,   2,  13,
     29,  -1, -20,  -7,  -8,  -4, -38, -29,
     -9,  24,   2, -16, -20,   6,  22, -22,
    -17, -20, -12, -27, -30, -25, -14, -36,
    -49,  -1, -27, -39, -46, -44, -33, -51,
    -14, -14, -22, -46, -44, -30, -15, -27,
      1,   7,  -8, -64, -43, -16,   9,   8,
    -15,  36,  12, -54,   8, -28,  24,  14,
]

KING_EG = [
    -74, -35, -18, -18, -11,  15,   4, -17,
    -12,  17,  14,  17,  17,  38,  23,  11,
     10,  17,  23,  15,  20,  45,  44,  13,
     -8,  22,  24,  27,  26,  33,  26,   3,
    -18,  -4,  21,  24,  27,  23,   9, -11,
    -19,  -3,  11,  21,  23,  16,   7,  -9,
    -27, -11,   4,  13,  14,   4,  -5, -17,
    -53, -34, -21, -11, -28, -14, -24, -43,
]

TABLE_MG = {
    chess.PAWN: PAWN_MG,
    chess.KNIGHT: KNIGHT_MG,
    chess.BISHOP: BISHOP_MG,
    chess.ROOK: ROOK_MG,
    chess.QUEEN: QUEEN_MG,
    chess.KING: KING_MG,
}

TABLE_EG = {
    chess.PAWN: PAWN_EG,
    chess.KNIGHT: KNIGHT_EG,
    chess.BISHOP: BISHOP_EG,
    chess.ROOK: ROOK_EG,
    chess.QUEEN: QUEEN_EG,
    chess.KING: KING_EG,
}

CENTER_DISTANCE = [
    max(3 - chess.square_file(s), chess.square_file(s) - 4)
    + max(3 - chess.square_rank(s), chess.square_rank(s) - 4)
    for s in chess.SQUARES
]

MG_TABLE = [0] * 832
EG_TABLE = [0] * 832

for _piece in (chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING):
    for _square in chess.SQUARES:
        _index = chess.square_mirror(_square)
        _white = 384 + _piece * 64 + _square
        _black = _piece * 64 + _square
        MG_TABLE[_white] = PIECE_VALUE_MG[_piece] + TABLE_MG[_piece][_index]
        EG_TABLE[_white] = PIECE_VALUE_EG[_piece] + TABLE_EG[_piece][_index]
        MG_TABLE[_black] = PIECE_VALUE_MG[_piece] + TABLE_MG[_piece][_square]
        EG_TABLE[_black] = PIECE_VALUE_EG[_piece] + TABLE_EG[_piece][_square]

PASSED_BONUS_MG = [0, 5, 10, 20, 35, 60, 100, 0]
PASSED_BONUS_EG = [0, 15, 25, 45, 75, 120, 180, 0]

PASSED_TABLE = [0] * 128

for _colour in (chess.WHITE, chess.BLACK):
    for _sq in chess.SQUARES:
        _file = chess.square_file(_sq)
        _rank = chess.square_rank(_sq)
        _mask = 0
        for _f in range(max(0, _file - 1), min(8, _file + 2)):
            _ranks = range(_rank + 1, 8) if _colour == chess.WHITE else range(0, _rank)
            for _r in _ranks:
                _mask |= chess.BB_SQUARES[chess.square(_f, _r)]
        PASSED_TABLE[(64 if _colour else 0) + _sq] = _mask

BISHOP_PAIR_MG = 25
BISHOP_PAIR_EG = 45
ROOK_OPEN_FILE = 22
ROOK_HALF_OPEN_FILE = 10
DOUBLED_PAWN_MG = -12
DOUBLED_PAWN_EG = -22
ISOLATED_PAWN_MG = -14
ISOLATED_PAWN_EG = -18

ADJACENT_FILES = [
    sum(chess.BB_FILES[f] for f in range(max(0, i - 1), min(8, i + 2)) if f != i)
    for i in range(8)
]

_ZOB = random.Random(0x5EED_1234)
# Same indexing as MG_TABLE: (384 if white else 0) + piece_type * 64 + square.
ZOBRIST_PIECE = [_ZOB.getrandbits(64) for _ in range(832)]
ZOBRIST_CASTLE_SQ = [_ZOB.getrandbits(64) for _ in range(64)]
ZOBRIST_EP_FILE = [_ZOB.getrandbits(64) for _ in range(8)]
ZOBRIST_TURN = _ZOB.getrandbits(64)
CASTLE_CACHE: dict[int, int] = {}

PAWN_CACHE_MAX = 100_000
PAWN_CACHE: dict[tuple[int, int], tuple[int, int]] = {}

TT: dict[int, tuple[int, int, int, chess.Move | None]] = {}
KILLERS: dict[int, list[chess.Move]] = {}
HISTORY_SCORE: dict[tuple[int, int], int] = {}
HISTORY: set[int] = set()

STABILITY_CUTOFF = 3

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


def to_tt(score: int, ply: int) -> int:
    if score > MATE_BOUND:
        return score + ply
    if score < -MATE_BOUND:
        return score - ply
    return score


def from_tt(score: int, ply: int) -> int:
    if score > MATE_BOUND:
        return score - ply
    if score < -MATE_BOUND:
        return score + ply
    return score


def mopup(board: chess.Board, winner: chess.Color) -> int:
    """Drive the losing king to the edge and walk the winning king toward it."""
    loser_king = board.king(not winner)
    winner_king = board.king(winner)
    if loser_king is None or winner_king is None:
        return 0
    edge = CENTER_DISTANCE[loser_king]
    gap = abs(chess.square_file(winner_king) - chess.square_file(loser_king)) + abs(
        chess.square_rank(winner_king) - chess.square_rank(loser_king)
    )
    return 5 * edge + 2 * (14 - gap)

def state_key(board: chess.Board) -> int:
    """Zobrist contribution of side to move, castling rights and en-passant file.

    Read from the board rather than updated incrementally. These are the parts
    that a move changes in awkward ways -- rights lost when a rook is captured,
    the en-passant square appearing and expiring, a null move clearing it -- so
    deriving them fresh each node removes that whole class of drift. Only piece
    placement is threaded through move_delta.
    """
    key = ZOBRIST_TURN if board.turn else 0

    rights = board.castling_rights
    if rights:
        cached = CASTLE_CACHE.get(rights)
        if cached is None:
            cached = 0
            for square in chess.scan_forward(rights):
                cached ^= ZOBRIST_CASTLE_SQ[square]
            CASTLE_CACHE[rights] = cached
        key ^= cached

    ep = board.ep_square
    if ep is not None:
        key ^= ZOBRIST_EP_FILE[chess.square_file(ep)]

    return key


def placement_key(board: chess.Board) -> int:
    """Zobrist of piece placement alone, computed from scratch."""
    key = 0
    for square, piece in board.piece_map().items():
        key ^= ZOBRIST_PIECE[(384 if piece.color else 0) + piece.piece_type * 64 + square]
    return key


def full_key(board: chess.Board) -> int:
    return placement_key(board) ^ state_key(board)


def move_delta(board: chess.Board, move: chess.Move) -> tuple[int, int, int, int]:
    """Change in (mg, eg, phase, placement key) from playing move. Call BEFORE push."""
    mover = board.piece_at(move.from_square)
    if mover is None:
        return 0, 0, 0, 0
    colour = mover.color
    piece_type = mover.piece_type
    sign = 1 if colour else -1
    base = 384 if colour else 0

    d_mg = 0
    d_eg = 0
    d_phase = 0
    d_key = 0

    from_off = base + piece_type * 64 + move.from_square
    d_mg -= sign * MG_TABLE[from_off]
    d_eg -= sign * EG_TABLE[from_off]
    d_key ^= ZOBRIST_PIECE[from_off]

    landed = move.promotion if move.promotion else piece_type
    to_off = base + landed * 64 + move.to_square
    d_mg += sign * MG_TABLE[to_off]
    d_eg += sign * EG_TABLE[to_off]
    d_key ^= ZOBRIST_PIECE[to_off]

    if move.promotion:
        d_phase += PHASE_WEIGHT[move.promotion] - PHASE_WEIGHT[chess.PAWN]

    if board.is_en_passant(move):
        captured_square = move.to_square + (-8 if colour else 8)
        cap_off = (0 if colour else 384) + chess.PAWN * 64 + captured_square
        d_mg -= -sign * MG_TABLE[cap_off]
        d_eg -= -sign * EG_TABLE[cap_off]
        d_key ^= ZOBRIST_PIECE[cap_off]
    else:
        captured = board.piece_at(move.to_square)
        if captured is not None:
            cap_base = 384 if captured.color else 0
            cap_off = cap_base + captured.piece_type * 64 + move.to_square
            cap_sign = 1 if captured.color else -1
            d_mg -= cap_sign * MG_TABLE[cap_off]
            d_eg -= cap_sign * EG_TABLE[cap_off]
            d_phase -= PHASE_WEIGHT[captured.piece_type]
            d_key ^= ZOBRIST_PIECE[cap_off]

    if board.is_castling(move):
        if move.to_square > move.from_square:
            rook_from = move.from_square + 3
            rook_to = move.from_square + 1
        else:
            rook_from = move.from_square - 4
            rook_to = move.from_square - 1
        rf = base + chess.ROOK * 64 + rook_from
        rt = base + chess.ROOK * 64 + rook_to
        d_mg += sign * (MG_TABLE[rt] - MG_TABLE[rf])
        d_eg += sign * (EG_TABLE[rt] - EG_TABLE[rf])
        d_key ^= ZOBRIST_PIECE[rf] ^ ZOBRIST_PIECE[rt]

    return d_mg, d_eg, d_phase, d_key

def pawn_terms(white_pawns: int, black_pawns: int) -> tuple[int, int]:
    """(mg, eg) for the terms that depend on pawn placement alone.

    Passed, doubled and isolated pawns are a pure function of the two pawn
    bitboards, so they can be cached across the whole game. Pawn structure
    survives most piece moves, so the table hits on the large majority of
    leaves, and this was the bulk of what evaluate_incr recomputed each time.
    """
    key = (white_pawns, black_pawns)
    cached = PAWN_CACHE.get(key)
    if cached is not None:
        return cached

    mg = 0
    eg = 0

    for square in chess.scan_forward(white_pawns):
        if not (PASSED_TABLE[64 + square] & black_pawns):
            rank = chess.square_rank(square)
            mg += PASSED_BONUS_MG[rank]
            eg += PASSED_BONUS_EG[rank]

    for square in chess.scan_forward(black_pawns):
        if not (PASSED_TABLE[square] & white_pawns):
            rank = 7 - chess.square_rank(square)
            mg -= PASSED_BONUS_MG[rank]
            eg -= PASSED_BONUS_EG[rank]

    for own_pawns, sign in ((white_pawns, 1), (black_pawns, -1)):
        for file_index in range(8):
            file_bb = chess.BB_FILES[file_index]
            count = bin(file_bb & own_pawns).count("1")
            if count > 1:
                mg += sign * DOUBLED_PAWN_MG * (count - 1)
                eg += sign * DOUBLED_PAWN_EG * (count - 1)
            if count and not (ADJACENT_FILES[file_index] & own_pawns):
                mg += sign * ISOLATED_PAWN_MG * count
                eg += sign * ISOLATED_PAWN_EG * count

    if len(PAWN_CACHE) < PAWN_CACHE_MAX:
        PAWN_CACHE[key] = (mg, eg)
    return mg, eg


def evaluate(board: chess.Board) -> int:
    white_bb = board.occupied_co[chess.WHITE]
    pawns_bb = board.pawns
    white_pawns = pawns_bb & white_bb
    black_pawns = pawns_bb & ~white_bb & board.occupied

    mg = 0
    eg = 0
    phase = 0

    for square, piece in board.piece_map().items():
        colour = piece.color
        piece_type = piece.piece_type
        offset = (384 if colour else 0) + piece_type * 64 + square
        if colour:
            mg += MG_TABLE[offset]
            eg += EG_TABLE[offset]
        else:
            mg -= MG_TABLE[offset]
            eg -= EG_TABLE[offset]
        phase += PHASE_WEIGHT[piece_type]

        if piece_type == chess.ROOK:
            file_bb = chess.BB_FILES[chess.square_file(square)]
            own_pawns = white_pawns if colour else black_pawns
            if not (file_bb & own_pawns):
                their_pawns = black_pawns if colour else white_pawns
                bonus = ROOK_OPEN_FILE if not (file_bb & their_pawns) else ROOK_HALF_OPEN_FILE
                if colour:
                    mg += bonus
                    eg += bonus
                else:
                    mg -= bonus
                    eg -= bonus

    for colour, sign in ((chess.WHITE, 1), (chess.BLACK, -1)):
        own_pawns = white_pawns if colour else black_pawns

        if len(board.pieces(chess.BISHOP, colour)) >= 2:
            mg += sign * BISHOP_PAIR_MG
            eg += sign * BISHOP_PAIR_EG

        king = board.king(colour)
        if king is not None:
            rank = chess.square_rank(king)
            if (colour and rank <= 2) or (not colour and rank >= 5):
                file = chess.square_file(king)
                missing = 0
                for f in range(max(0, file - 1), min(8, file + 2)):
                    if not (chess.BB_FILES[f] & own_pawns):
                        missing += 1
                mg -= sign * KING_SHIELD_PENALTY * missing

    pawn_mg, pawn_eg = pawn_terms(white_pawns, black_pawns)
    mg += pawn_mg
    eg += pawn_eg

    phase = min(phase, TOTAL_PHASE)
    score = (mg * phase + eg * (TOTAL_PHASE - phase)) // TOTAL_PHASE

    if phase <= MOPUP_PHASE and abs(score) > MOPUP_MARGIN:
        if score > 0:
            score += mopup(board, chess.WHITE)
        else:
            score -= mopup(board, chess.BLACK)

    if board.halfmove_clock > 20:
        drift = (board.halfmove_clock - 20) * SHUFFLE_PENALTY
        if score > 0:
            score -= drift
        elif score < 0:
            score += drift

    return score if board.turn == chess.WHITE else -score

def evaluate_incr(board: chess.Board, mg: int, eg: int, phase: int) -> int:
    white_bb = board.occupied_co[chess.WHITE]
    pawns_bb = board.pawns
    white_pawns = pawns_bb & white_bb
    black_pawns = pawns_bb & ~white_bb & board.occupied

    for square in chess.scan_forward(board.rooks & board.occupied):
        colour = bool(white_bb & chess.BB_SQUARES[square])
        file_bb = chess.BB_FILES[chess.square_file(square)]
        own_pawns = white_pawns if colour else black_pawns
        if not (file_bb & own_pawns):
            their_pawns = black_pawns if colour else white_pawns
            bonus = ROOK_OPEN_FILE if not (file_bb & their_pawns) else ROOK_HALF_OPEN_FILE
            if colour:
                mg += bonus
                eg += bonus
            else:
                mg -= bonus
                eg -= bonus

    for colour, sign in ((chess.WHITE, 1), (chess.BLACK, -1)):
        own_pawns = white_pawns if colour else black_pawns

        if len(board.pieces(chess.BISHOP, colour)) >= 2:
            mg += sign * BISHOP_PAIR_MG
            eg += sign * BISHOP_PAIR_EG

        king = board.king(colour)
        if king is not None:
            rank = chess.square_rank(king)
            if (colour and rank <= 2) or (not colour and rank >= 5):
                file = chess.square_file(king)
                missing = 0
                for f in range(max(0, file - 1), min(8, file + 2)):
                    if not (chess.BB_FILES[f] & own_pawns):
                        missing += 1
                mg -= sign * KING_SHIELD_PENALTY * missing

    pawn_mg, pawn_eg = pawn_terms(white_pawns, black_pawns)
    mg += pawn_mg
    eg += pawn_eg

    phase = min(phase, TOTAL_PHASE)
    score = (mg * phase + eg * (TOTAL_PHASE - phase)) // TOTAL_PHASE

    if phase <= MOPUP_PHASE and abs(score) > MOPUP_MARGIN:
        if score > 0:
            score += mopup(board, chess.WHITE)
        else:
            score -= mopup(board, chess.BLACK)

    if board.halfmove_clock > 20:
        drift = (board.halfmove_clock - 20) * SHUFFLE_PENALTY
        if score > 0:
            score -= drift
        elif score < 0:
            score += drift

    return score if board.turn == chess.WHITE else -score

def see_gain(board: chess.Board, move: chess.Move) -> int:
    """Net material from the full exchange sequence on the target square."""
    target = move.to_square
    victim = board.piece_type_at(target)
    if victim is None:
        return 0

    attacker = board.piece_type_at(move.from_square)
    if attacker is None:
        return MVV_LVA_VALUE[victim]

    occupied = board.occupied & ~chess.BB_SQUARES[move.from_square]
    side = not board.turn
    gains = [MVV_LVA_VALUE[victim]]
    on_square = attacker

    while True:
        attackers = board.attackers_mask(side, target) & occupied
        if not attackers:
            break
        best_square = -1
        best_value = 10_000
        for square in chess.scan_forward(attackers):
            piece_type = board.piece_type_at(square)
            if piece_type is None:
                continue
            value = MVV_LVA_VALUE[piece_type]
            if value < best_value:
                best_value = value
                best_square = square
        if best_square < 0:
            break
        next_piece = board.piece_type_at(best_square)
        if next_piece is None:
            break
        gains.append(MVV_LVA_VALUE[on_square] - gains[-1])
        on_square = next_piece
        occupied &= ~chess.BB_SQUARES[best_square]
        side = not side
        if len(gains) > 32:
            break

    for i in range(len(gains) - 2, -1, -1):
        gains[i] = -max(-gains[i], gains[i + 1])
    return gains[0]

def move_score(board: chess.Board, move: chess.Move, ply: int, tt_move: chess.Move | None) -> int:
    if tt_move is not None and move == tt_move:
        return 1_000_000

    victim = board.piece_type_at(move.to_square)
    if victim is not None:
        gain = see_gain(board, move)
        if gain >= 0:
            return 100_000 + gain
        return 50_000 + gain

    killers = KILLERS.get(ply)
    if killers is not None:
        if move == killers[0]:
            return 90_000
        if len(killers) > 1 and move == killers[1]:
            return 80_000

    return HISTORY_SCORE.get((move.from_square, move.to_square), 0)


def order_moves(
    board: chess.Board,
    moves: list[chess.Move],
    ply: int = 0,
    tt_move: chess.Move | None = None,
) -> list[chess.Move]:
    return sorted(moves, key=lambda m: move_score(board, m, ply, tt_move), reverse=True)

def quiesce(
    board: chess.Board, alpha: int, beta: int, ply: int, clock: Clock,
    mg: int, eg: int, phase: int,
) -> int:
    clock.check()

    if board.is_check():
        moves = list(board.legal_moves)
        if not moves:
            return -MATE + ply
        best = -MATE
        for move in order_moves(board, moves, ply):
            d_mg, d_eg, d_phase, _ = move_delta(board, move)
            board.push(move)
            score = -quiesce(
                board, -beta, -alpha, ply + 1, clock, mg + d_mg, eg + d_eg, phase + d_phase
            )
            board.pop()
            if score > best:
                best = score
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break
        return best

    best = evaluate_incr(board, mg, eg, phase)
    if best >= beta:
        return best
    if best > alpha:
        alpha = best

    endgame = board.occupied.bit_count() <= 8

    for move in order_moves(board, list(board.generate_legal_captures()), ply):
        if not endgame:
            if see_gain(board, move) < 0:
                continue
            victim = board.piece_type_at(move.to_square)
            gain = MVV_LVA_VALUE[victim] if victim is not None else 0
            if move.promotion:
                gain += 800
            if best + gain + DELTA_MARGIN < alpha:
                continue
        d_mg, d_eg, d_phase, _ = move_delta(board, move)
        board.push(move)
        score = -quiesce(
            board, -beta, -alpha, ply + 1, clock, mg + d_mg, eg + d_eg, phase + d_phase
        )
        board.pop()
        if score > best:
            best = score
        if best > alpha:
            alpha = best
        if alpha >= beta:
            break
    return best

def search(
    board: chess.Board, depth: int, alpha: int, beta: int, ply: int, clock: Clock,
    mg: int, eg: int, phase: int, pkey: int,
) -> int:
    clock.check()

    key = pkey ^ state_key(board)
    if ply > 0 and key in HISTORY:
        return 0
    tt_move: chess.Move | None = None
    entry = TT.get(key)
    if entry is not None:
        stored_depth, stored_score, stored_flag, stored_move = entry
        tt_move = stored_move
        if stored_depth >= depth:
            adjusted = from_tt(stored_score, ply)
            if stored_flag == TT_EXACT:
                return adjusted
            if stored_flag == TT_LOWER and adjusted >= beta:
                return adjusted
            if stored_flag == TT_UPPER and adjusted <= alpha:
                return adjusted

    moves = list(board.legal_moves)
    if not moves:
        return -MATE + ply if board.is_check() else 0
    if depth == 0:
        return quiesce(board, alpha, beta, ply, clock, mg, eg, phase)

    if (
        depth >= 3
        and ply > 0
        and not board.is_check()
        and beta < MATE - 1000
        and phase > NULL_MIN_PHASE
    ):
        board.push(chess.Move.null())
        null_score = -search(
            board, depth - 3, -beta, -beta + 1, ply + 1, clock, mg, eg, phase, pkey
        )
        board.pop()
        if null_score >= beta:
            return null_score

    original_alpha = alpha
    best = -MATE
    best_move: chess.Move | None = None

    for index, move in enumerate(order_moves(board, moves, ply, tt_move)):
        # A promotion or an en-passant capture leaves to_square empty beforehand,
        # so "nothing stands on to_square" is not the same thing as quiet. Both are
        # tactical: reducing them or storing them as killers loses material.
        quiet = (
            move.promotion is None
            and not (board.occupied & chess.BB_SQUARES[move.to_square])
            and not (
                move.to_square == board.ep_square
                and board.pawns & chess.BB_SQUARES[move.from_square]
            )
        )
        d_mg, d_eg, d_phase, d_key = move_delta(board, move)
        nmg, neg, nphase = mg + d_mg, eg + d_eg, phase + d_phase
        nkey = pkey ^ d_key
        board.push(move)
        if index == 0:
            score = -search(
                board, depth - 1, -beta, -alpha, ply + 1, clock, nmg, neg, nphase, nkey
            )
        else:
            reduction = 0
            if depth >= 3 and index >= 4 and quiet and not board.is_check():
                reduction = 1
            score = -search(
                board, depth - 1 - reduction, -alpha - 1, -alpha, ply + 1, clock,
                nmg, neg, nphase, nkey,
            )
            if score > alpha and reduction:
                score = -search(
                    board, depth - 1, -alpha - 1, -alpha, ply + 1, clock, nmg, neg, nphase, nkey
                )
            if alpha < score < beta:
                score = -search(
                    board, depth - 1, -beta, -alpha, ply + 1, clock, nmg, neg, nphase, nkey
                )
        board.pop()
        if score > best:
            best = score
            best_move = move
        if best > alpha:
            alpha = best
        if alpha >= beta:
            if quiet:
                slot = KILLERS.setdefault(ply, [])
                if not slot or slot[0] != move:
                    slot.insert(0, move)
                    del slot[2:]
                square_pair = (move.from_square, move.to_square)
                HISTORY_SCORE[square_pair] = HISTORY_SCORE.get(square_pair, 0) + depth * depth
            break

    if best <= original_alpha:
        flag = TT_UPPER
    elif best >= beta:
        flag = TT_LOWER
    else:
        flag = TT_EXACT

    if len(TT) < TT_MAX_ENTRIES:
        TT[key] = (depth, to_tt(best, ply), flag, best_move)

    return best


def search_root(board: chess.Board, depth: int, clock: Clock) -> tuple[chess.Move | None, bool]:
    mg = eg = phase = 0
    for square, piece in board.piece_map().items():
        offset = (384 if piece.color else 0) + piece.piece_type * 64 + square
        if piece.color:
            mg += MG_TABLE[offset]
            eg += EG_TABLE[offset]
        else:
            mg -= MG_TABLE[offset]
            eg -= EG_TABLE[offset]
        phase += PHASE_WEIGHT[piece.piece_type]

    alpha = -MATE - 1
    best_move: chess.Move | None = None
    pkey = placement_key(board)
    entry = TT.get(pkey ^ state_key(board))
    tt_move = entry[3] if entry is not None else None
    for move in order_moves(board, list(board.legal_moves), 0, tt_move):
        d_mg, d_eg, d_phase, d_key = move_delta(board, move)
        board.push(move)
        try:
            score = -search(
                board, depth - 1, -MATE, -alpha, 1, clock,
                mg + d_mg, eg + d_eg, phase + d_phase, pkey ^ d_key,
            )
        except TimeUp:
            board.pop()
            return best_move, False
        board.pop()
        if best_move is None or score > alpha:
            alpha = score
            best_move = move
    return best_move, True


def get_move(fen: str, time_left_ms: int) -> str:
    """Never raises: a crash forfeits the game, so every path returns a string."""
    try:
        board = chess.Board(fen)
        fallback = ""
        for legal in board.legal_moves:
            fallback = legal.uci()
            break
        if not fallback:
            return "0000"
        HISTORY.add(full_key(board))
        KILLERS.clear()
        for square_pair in HISTORY_SCORE:
            HISTORY_SCORE[square_pair] >>= 1
    except Exception:
        return "0000"

    try:
        remaining_s = time_left_ms / 1000.0
        budget = max(0.01, min(remaining_s / 12.0, remaining_s * 0.25))
        start = time.perf_counter()
        clock = Clock(budget)
        chosen = fallback
        last_depth_s = 0.0

        stable = 0
        previous = ""
        for depth in range(1, MAX_DEPTH):
            elapsed = time.perf_counter() - start
            limit = budget * (0.5 if stable >= STABILITY_CUTOFF else 1.0)
            if depth > 2 and elapsed + last_depth_s * 8 > limit:
                break
            depth_start = time.perf_counter()
            move, complete = search_root(board, depth, clock)
            if complete and move is not None:
                chosen = move.uci()
                stable = stable + 1 if chosen == previous else 0
                previous = chosen
            if not complete:
                break
            last_depth_s = time.perf_counter() - depth_start
        
        return chosen
    except Exception:
        return fallback