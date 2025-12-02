import tkinter as tk
from tkinter import ttk, messagebox
from .engine import GameState, opponent
from .ai import best_ai_move


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PicPacPoe")
        self.geometry("340x340")
        self.resizable(False, False)

        # game stuff
        self.state = GameState()
        self.play_mode = tk.StringVar(value="vs_ai")   # "vs_ai" or "pvp"
        self.ai_starts = tk.StringVar(value="player")  # "player" or "ai"
        self.difficulty = tk.StringVar(value="easy")   # starts with easy mode
        self.player_symbol = "X"                       # player symbol (X or O)

        # container for frames
        self.container = ttk.Frame(self)
        self.container.grid(row=0, column=0)

        self.frames = {}
        for F in (MenuFrame, GameFrame, ResultFrame, SettingsFrame):
            frame = F(self.container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show("MenuFrame")

    def show(self, name):
        self.frames[name].tkraise()
        if hasattr(self.frames[name], "on_show"):
            self.frames[name].on_show()

    # game helpers
    def start_new_match(self):
        self.state.reset_board()

        if self.play_mode.get() == "vs_ai":
            if self.ai_starts.get() == "ai":
                self.state.turn = opponent(self.player_symbol)
            else:
                self.state.turn = self.player_symbol

        self.show("GameFrame")

        # if AI starts
        if self.play_mode.get() == "vs_ai" and self.state.turn != self.player_symbol:
            self.after(200, self.frames["GameFrame"].ai_move)

    def reset_scores(self):
        self.state.x_score = 0
        self.state.o_score = 0
        self.state.draws = 0
        self.frames["GameFrame"].update_ui()

# Menu


class MenuFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="PicPacPoe", font=(
            "Arial", 26, "bold")).pack(pady=20)

        style = ttk.Style()
        style.configure("MenuButton.TButton", font=("Arial", 12))

        ttk.Button(self, text="Start", width=25,
                   command=self.app.start_new_match, style="MenuButton.TButton").pack(pady=10, ipady=10)
        ttk.Button(self, text="Settings", width=25,
                   command=lambda: self.app.show("SettingsFrame"), style="MenuButton.TButton").pack(pady=10, ipady=10)
        ttk.Button(self, text="Exit", width=25,
                   command=self.app.destroy, style="MenuButton.TButton").pack(pady=10, ipady=10)


# Game
class GameFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        # top bar
        top = ttk.Frame(self)
        top.pack(fill="x", pady=20)

        reset_scores_btn = ttk.Button(top, text="Reset Scores",
                                      command=self.app.reset_scores)
        reset_scores_btn.pack(side="left", padx=10)

        self.turn_label = ttk.Label(top, text="", font=("Arial", 10))
        self.turn_label.pack(side="left", expand=True)

        new_game_btn = ttk.Button(top, text="New Game",
                                  command=self.app.start_new_match)
        new_game_btn.pack(side="left", padx=15)

        # board
        board = ttk.Frame(self)
        board.pack(pady=10, padx=10)

        self.buttons = []
        for r in range(3):
            for c in range(3):
                i = 3*r + c
                b = ttk.Button(board, text=" ", width=4,
                               command=lambda i=i: self.on_click(i))
                b.grid(row=r, column=c, padx=6, pady=6, ipadx=12, ipady=12)
                self.buttons.append(b)

        self.score_label = ttk.Label(self, text="")
        self.score_label.pack(pady=10)

        # bottom bar
        bottom = ttk.Frame(self)
        bottom.pack(fill="x")

        ttk.Button(bottom, text="Menu",
                   command=lambda: self.app.show("MenuFrame")).pack(anchor="center", padx=10)

    def on_show(self):
        self.update_ui()

    def update_ui(self):
        s = self.app.state

        # turn text
        if self.app.play_mode.get() == "pvp":
            self.turn_label.config(text=f"Turn: {s.turn}")
        else:
            if s.turn == self.app.player_symbol:
                self.turn_label.config(text=f"Player's Turn ({s.turn})")
            else:
                self.turn_label.config(text=f"AI's Turn ({s.turn})")

        # board
        for i, cell in enumerate(s.board.cells):
            txt = cell if cell else " "
            self.buttons[i].config(
                text=txt, state="disabled" if cell else "normal")

        # scores
        self.score_label.config(
            text=f"X: {s.x_score}   O: {s.o_score}   Draws: {s.draws}"
        )

    def on_click(self, idx):
        try:
            result = self.app.state.play(idx)
        except ValueError:
            return
        self.finish_move(result)

    def ai_move(self):
        for b in self.buttons:
            b.config(state="disabled")

        s = self.app.state
        ai_symbol = opponent(self.app.player_symbol)
        result = s.play(
            best_ai_move(s.board, ai_symbol, self.app.difficulty.get())
        )
        self.finish_move(result)

    def finish_move(self, result):
        self.update_ui()
        if result:
            self.app.frames["ResultFrame"].set_result(result)
            self.app.show("ResultFrame")
            return

        # trigger AI only when it’s truly AI’s turn
        if self.app.play_mode.get() == "vs_ai":
            if self.app.state.turn != self.app.player_symbol:
                self.after(150, self.ai_move)


# Result
class ResultFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        self.result_label = ttk.Label(
            self, text="", font=("Arial", 24, "bold"))
        self.result_label.pack(pady=20)

        self.score_label = ttk.Label(self, text="", font=("Arial", 12))
        self.score_label.pack(pady=10)

        btns = ttk.Frame(self)
        btns.pack(pady=20)

        ttk.Button(btns, text="Menu",
                   command=lambda: app.show("MenuFrame")).grid(row=0, column=0, padx=10)

        ttk.Button(btns, text="New Game",
                   command=app.start_new_match).grid(row=0, column=1, padx=10)

    def set_result(self, result):
        if result == "Draw":
            txt = "It's a Draw"
        else:
            txt = f"{result} Wins"
        self.result_label.config(text=txt)

        s = self.app.state
        self.score_label.config(
            text=f"X: {s.x_score}   O: {s.o_score}   Draws: {s.draws}"
        )


# Settings
class SettingsFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app

        ttk.Label(self, text="Settings", font=(
            "Arial", 20, "bold")).pack(pady=15)

        box = ttk.Frame(self)
        box.pack(pady=10, padx=10)

        # Play mode
        ttk.Label(box, text="Play Mode:").grid(
            row=0, column=0, sticky="w", pady=10)
        ttk.Radiobutton(box, text="Vs AI", value="vs_ai",
                        variable=app.play_mode).grid(row=0, column=1, sticky="w", padx=15)
        ttk.Radiobutton(box, text="PvP", value="pvp",
                        variable=app.play_mode).grid(row=0, column=2, sticky="w", padx=15)

        # AI Starts
        ttk.Label(box, text="First Turn:").grid(
            row=1, column=0, sticky="w", pady=10)
        ttk.Radiobutton(box, text="Player", value="player",
                        variable=app.ai_starts).grid(row=1, column=1, sticky="w", padx=15)
        ttk.Radiobutton(box, text="AI", value="ai", variable=app.ai_starts).grid(
            row=1, column=2, sticky="w", padx=15)

        # Play As (X or O)
        ttk.Label(box, text="Play As:").grid(
            row=2, column=0, sticky="w", pady=10)

        self.playas_var = tk.StringVar(value=self.app.player_symbol)

        ttk.Radiobutton(box, text="X", value="X",
                        variable=self.playas_var).grid(row=2, column=1, sticky="w", padx=15)
        ttk.Radiobutton(box, text="O", value="O",
                        variable=self.playas_var).grid(row=2, column=2, sticky="w", padx=15)

        # Difficulty
        ttk.Label(box, text="Difficulty:").grid(
            row=3, column=0, sticky="w", pady=10)
        for i, diff in enumerate(["easy", "medium", "hard"], start=1):
            ttk.Radiobutton(box, text=diff.capitalize(),
                            value=diff, variable=app.difficulty).grid(row=3, column=i, sticky="w", padx=15)

        ttk.Button(self, text="Back",
                   command=lambda: (self.apply_changes(), app.show("MenuFrame"))).pack(pady=20)

    def on_show(self):
        self.playas_var.set(self.app.player_symbol)
        self.last_mode = self.app.play_mode.get()

    def apply_changes(self):
        old_symbol = self.app.player_symbol
        new_symbol = self.playas_var.get()

        # save new symbol
        self.app.player_symbol = new_symbol

        # determine score reset conditions
        mode_changed = (self.app.play_mode.get() != self.last_mode)
        symbol_changed = (new_symbol != old_symbol)

        if mode_changed or symbol_changed:
            self.app.state.x_score = 0
            self.app.state.o_score = 0
            self.app.state.draws = 0


def run():
    app = App()
    app.mainloop()
