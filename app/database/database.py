import sqlite3
from pathlib import Path

from app.utils.time_utils import parse_time


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Default location (desktop / development).
DATABASE_PATH = BASE_DIR / "data" / "attendance.db"


def configure_database(path):
    """Choose where the database file lives.

    On Android the app folder is not a safe place to keep data (it is
    replaced on every update), so main.py points this at the app's
    private user_data_dir instead.
    """
    global DATABASE_PATH
    DATABASE_PATH = Path(path)


def get_connection():
    """Create and return a connection to the SQLite database."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    # Allows us to access columns by name
    connection.row_factory = sqlite3.Row

    # Enable foreign key support
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def _normalize_legacy_times(connection):
    """One-time clean-up: convert old '11:23 PM' values to '23:23'.

    Older versions saved some times in 12-hour format and some in 24-hour
    format, which made ORDER BY time give wrong results.
    """
    rows = connection.execute(
        "SELECT id, time FROM attendance"
    ).fetchall()

    for row in rows:
        try:
            fixed = parse_time(row["time"])
        except ValueError:
            continue  # leave unknown values untouched

        if fixed != row["time"]:
            connection.execute(
                "UPDATE attendance SET time = ? WHERE id = ?",
                (fixed, row["id"]),
            )


def initialize_database():
    """Create the required database tables."""

    connection = get_connection()

    try:
        # Subjects table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_name TEXT NOT NULL,
                subject_code TEXT NOT NULL UNIQUE,
                professor_name TEXT NOT NULL
            )
        """)

        # Attendance table
        connection.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),

                FOREIGN KEY (subject_id)
                    REFERENCES subjects(id)
                    ON DELETE CASCADE
            )
        """)

        # Speeds up the per-subject history / calendar queries
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_attendance_subject_date
            ON attendance (subject_id, date, time)
        """)

        _normalize_legacy_times(connection)

        connection.commit()

    finally:
        connection.close()
