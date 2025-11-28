from __future__ import annotations
from functools import lru_cache
from typing import Optional, Tuple
from .engine import Board, opponent, Player


def score(board: Board, ai: Player) -> int:
    w = board.winner()
    if w == ai:
        return 1
    if w is None and board.is_full():
        return 0
    return -1 if w else 0


@lru_cache(maxsize=20000)
def _minimax_cached(cells_tuple: Tuple[Optional[Player], ...],
                    turn: Player,
                    ai: Player) -> int:
    board = Board()
    board.cells = list(cells_tuple)
    return _minimax_value(board, turn, ai, -2, 2)


def _minimax_value(board: Board,
                   turn: Player,
                   ai: Player,
                   alpha: int,
                   beta: int) -> int:
    if board.is_terminal():
        return score(board, ai)

    empties = board.empty_squares()

    # Move ordering: check for immediate wins first
    for move in empties:
        board.cells[move] = turn
        if board.winner() == turn:
            board.cells[move] = None
            return 1 if turn == ai else -1
        board.cells[move] = None

    if turn == ai:  # maximizing
        best = -2
        for move in empties:
            board.cells[move] = turn
            val = _minimax_cached(tuple(board.cells), opponent(turn), ai)
            board.cells[move] = None
            if val > best:
                best = val
            if best > alpha:
                alpha = best
            if beta <= alpha:
                break
        return best
    else:  # minimizing
        best = 2
        for move in empties:
            board.cells[move] = turn
            val = _minimax_cached(tuple(board.cells), opponent(turn), ai)
            board.cells[move] = None
            if val < best:
                best = val
            if best < beta:
                beta = best
            if beta <= alpha:
                break
        return best


def best_ai_move(board: Board, ai: Player, difficulty: str = "hard") -> int:
    empties = board.empty_squares()
    if not empties:
        raise ValueError("No moves available")

    # Easy: fully random
    if difficulty == "easy":
        import random
        return random.choice(empties)

    # Medium: sometimes random, sometimes optimal
    if difficulty == "medium":
        import random
        if random.random() < 0.4:
            return random.choice(empties)

    # Hard/Medium default: pick best move from minimax
    best_val, best_move = -2, None
    for move in empties:
        board.cells[move] = ai
        val = _minimax_cached(tuple(board.cells), opponent(ai), ai)
        board.cells[move] = None
        if val > best_val:
            best_val, best_move = val, move

    return best_move if best_move is not None else empties[0]
