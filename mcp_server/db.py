"""
db.py

Lightweight SQLite connection helper for the customer support MCP tools.

This module assumes that `support.db` lives in the same folder
as this file (i.e., the mcp_server directory).
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

# Path to support.db inside mcp_server/
DB_PATH = Path(__file__).resolve().parent / "support.db"


@contextmanager
def get_conn():
    """
    Context manager that yields a SQLite connection with Row factory enabled.

    Usage:
        with get_conn() as conn:
            conn.execute("SELECT ...")
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _row_to_dict(row: sqlite3.Row) -> dict:
    """
    Convert a sqlite3.Row to a plain Python dict.
    """
    return {k: row[k] for k in row.keys()}
