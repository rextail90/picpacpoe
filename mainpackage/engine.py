from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

Player = str  # 'X' or 'O'

WIN_LINES: Tuple[Tuple[int, int, int], ...] = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


@dataclass
class Board:
    cells: List[Optional[Player]] = field(default_factory=lambda: [None] * 9)

    def empty_squares(self) -> List[int]:
        return [i for i, v in enumerate(self.cells) if v is None]

    def place(self, idx: int, player: Player) -> None:
        if self.cells[idx] is not None:
            raise ValueError("Square already taken")
        self.cells[idx] = player

    def winner(self) -> Optional[Player]:
        for a, b, c in WIN_LINES:
            v = self.cells[a]
            if v and v == self.cells[b] == self.cells[c]:
                return v
        return None

    def is_full(self) -> bool:
        return all(v is not None for v in self.cells)

    def is_terminal(self) -> bool:
        return self.winner() is not None or self.is_full()

    def clone(self) -> "Board":
        b = Board()
        b.cells = self.cells.copy()
        return b


def opponent(p: Player) -> Player:
    return "O" if p == "X" else "X"


@dataclass
class GameState:
    board: Board = field(default_factory=Board)
    turn: Player = "X"
    x_score: int = 0
    o_score: int = 0
    draws: int = 0

    def reset_board(self) -> None:
        self.board = Board()
        self.turn = "X"

    def play(self, idx: int) -> Optional[str]:
        """
        Play at index. Return 'X'/'O'/'Draw' when terminal, else None.
        """
        self.board.place(idx, self.turn)
        w = self.board.winner()
        if w:
            if w == "X":
                self.x_score += 1
            else:
                self.o_score += 1
            return w
        if self.board.is_full():
            self.draws += 1
            return "Draw"
        self.turn = opponent(self.turn)
        return None
