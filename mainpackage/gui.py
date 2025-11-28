import tkinter as tk
from tkinter import messagebox, ttk
from .engine import GameState
from .ai import best_ai_move


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PyTacToe+")
        self.resizable(False, False)

        self.state = GameState()
        self.vs_ai = tk.BooleanVar(value=True)
        self.ai_symbol = tk.StringVar(value="O")  # AI plays O by default
        self.difficulty = tk.StringVar(value="hard")

        self._build_ui()
        self._update_status()

    def _build_ui(self):
        root = ttk.Frame(self, padding=12)
        root.grid(row=0, column=0)

        # Scoreboard / Controls
        top = ttk.Frame(root)
        top.grid(row=0, column=0, sticky="ew")
        self.status = ttk.Label(top, text="", font=("Arial", 12))
        self.status.grid(row=0, column=0, padx=4)

        ttk.Button(top, text="New Game", command=self._new_game).grid(
            row=0, column=1, padx=6
        )
        ttk.Button(top, text="Reset Scores", command=self._reset_scores).grid(
            row=0, column=2, padx=6
        )

        # Options
        opts = ttk.Frame(root)
        opts.grid(row=1, column=0, sticky="ew", pady=(8, 4))
        ttk.Checkbutton(opts, text="Play vs AI", variable=self.vs_ai).grid(
            row=0, column=0, padx=4
        )

        ttk.Label(opts, text="AI Symbol:").grid(row=0, column=1)
        ttk.OptionMenu(opts, self.ai_symbol, self.ai_symbol.get(), "X", "O").grid(
            row=0, column=2, padx=4
        )

        ttk.Label(opts, text="Difficulty:").grid(row=0, column=3)
        ttk.OptionMenu(
            opts, self.difficulty, self.difficulty.get(), "easy", "medium", "hard"
        ).grid(row=0, column=4, padx=4)

        # Board
        self.buttons = []
        board = ttk.Frame(root, padding=8)
        board.grid(row=2, column=0)
        for r in range(3):
            for c in range(3):
                i = r * 3 + c
                b = ttk.Button(
                    board, text=" ", width=4, command=lambda i=i: self._on_click(i)
                )
                b.grid(row=r, column=c, ipadx=12, ipady=12, padx=4, pady=4)
                self.buttons.append(b)

        # Score labels
        self.score = ttk.Label(root, text="", font=("Arial", 11))
        self.score.grid(row=3, column=0, pady=(8, 0))

    def _update_status(self):
        self.score.config(
            text=f"X: {self.state.x_score}   O: {self.state.o_score}   Draws: {self.state.draws}"
        )
        self.status.config(text=f"Turn: {self.state.turn}")

        for i, cell in enumerate(self.state.board.cells):
            self.buttons[i].config(
                text=(cell if cell else " "),
                state=("disabled" if cell else "normal"),
            )

        # If it's AI's turn in vs AI mode, trigger AI move
        if self.vs_ai.get() and self.state.turn == self.ai_symbol.get():
            self.after(100, self._ai_move)

    def _new_game(self):
        self.state.reset_board()
        self._update_status()

    def _reset_scores(self):
        self.state.x_score = self.state.o_score = self.state.draws = 0
        self._new_game()

    def _on_click(self, idx: int):
        try:
            result = self.state.play(idx)
        except ValueError:
            return
        self._post_move(result)

    def _ai_move(self):
        # Temporarily disable all buttons to avoid double-clicks during AI move
        for b in self.buttons:
            b.config(state="disabled")

        move = best_ai_move(
            self.state.board, self.ai_symbol.get(), self.difficulty.get()
        )
        result = self.state.play(move)
        self._post_move(result)

    def _post_move(self, result):
        self._update_status()
        if result:
            if result == "Draw":
                message = "It's a draw!"
            else:
                message = f"{result} wins!"
            messagebox.showinfo("Game Over", message)
            self.state.reset_board()
            self._update_status()


def run():
    app = App()
    app.mainloop()
