# settings_db.py
import os
import sqlite3

DB_FILE = os.path.join(os.path.dirname(__file__), "settings.db")


def _get_conn():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            play_mode TEXT,
            ai_starts TEXT,
            difficulty TEXT,
            player_symbol TEXT
        )
    """)

    cur.execute("SELECT COUNT(*) FROM settings")
    count = cur.fetchone()[0]

    if count == 0:
        # default values
        cur.execute(
            "INSERT INTO settings (id, play_mode, ai_starts, difficulty, player_symbol) "
            "VALUES (1, 'vs_ai', 'player', 'easy', 'X')"
        )

    conn.commit()
    conn.close()


def load_settings():
    init_db()
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT play_mode, ai_starts, difficulty, player_symbol "
        "FROM settings WHERE id = 1"
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return {
            "play_mode": "vs_ai",
            "ai_starts": "player",
            "difficulty": "easy",
            "player_symbol": "X",
        }

    return {
        "play_mode": row[0],
        "ai_starts": row[1],
        "difficulty": row[2],
        "player_symbol": row[3],
    }


def save_settings(play_mode, ai_starts, difficulty, player_symbol):
    init_db()
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        "UPDATE settings "
        "SET play_mode = ?, ai_starts = ?, difficulty = ?, player_symbol = ? "
        "WHERE id = 1",
        (play_mode, ai_starts, difficulty, player_symbol),
    )

    conn.commit()
    conn.close()
