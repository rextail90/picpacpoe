from mainpackage.engine import Board, GameState


def test_win_detection_rows():
    b = Board(["X", "X", "X", None, None, None, None, None, None])
    assert b.winner() == "X"
    b = Board([None, None, None, "O", "O", "O", None, None, None])
    assert b.winner() == "O"


def test_play_and_scores():
    g = GameState()
    g.play(0)  # X
    g.play(3)  # O
    g.play(1)  # X
    g.play(4)  # O
    result = g.play(2)  # X wins
    assert result == "X"
    assert g.x_score == 1
