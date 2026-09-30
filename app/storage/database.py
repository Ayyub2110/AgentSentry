import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/agentsentry.db")


def get_connection() -> sqlite3.Connection:
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS traces (
            trace_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            application_id TEXT NOT NULL,
            user_query TEXT NOT NULL,
            trace_data TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()