"""SQLite database manager with persistent connection and schema initialization."""
from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Any

from app.config import DB_PATH


class Database:
    """SQLite wrapper with persistent thread-local connections, WAL mode, and query helpers."""

    def __init__(self, db_path: Path | str = DB_PATH):
        self.db_path = str(db_path)
        self._local = threading.local()

    # ------------------------------------------------------------------
    # Connection (persistent, thread-local)
    # ------------------------------------------------------------------

    def connect(self) -> sqlite3.Connection:
        """Return a persistent connection for the current thread."""
        conn = getattr(self._local, "conn", None)
        if conn is None:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=10)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
            conn.execute("PRAGMA cache_size = -8000")  # 8MB cache
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return conn

    def close(self) -> None:
        """Close the current thread's connection if open."""
        conn = getattr(self._local, "conn", None)
        if conn is not None:
            conn.close()
            self._local.conn = None

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Run schema.sql to create tables if they don't exist, then apply migrations."""
        import sys
        if getattr(sys, "frozen", False):
            schema_path = Path(sys.executable).parent / "_internal" / "app" / "data" / "schema.sql"
        else:
            schema_path = Path(__file__).parent / "schema.sql"

        schema_sql = schema_path.read_text(encoding="utf-8")
        conn = self.connect()
        conn.executescript(schema_sql)

        # Apply pending migrations
        from app.data.migrations import run_migrations
        run_migrations(conn)

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def execute(self, query: str, params: tuple = ()) -> list[Any]:
        """Execute a single query and return all rows."""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if not query.lstrip().upper().startswith("SELECT"):
                conn.commit()
            return cursor.fetchall()
        except sqlite3.OperationalError:
            # Connection may be stale — reset and retry once
            self._local.conn = None
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(query, params)
            if not query.lstrip().upper().startswith("SELECT"):
                conn.commit()
            return cursor.fetchall()

    def execute_many(self, query: str, param_list: list[tuple]) -> None:
        """Execute a query with multiple parameter sets (bulk insert/update)."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.executemany(query, param_list)
        conn.commit()

    def execute_returning_id(self, query: str, params: tuple = ()) -> int:
        """Execute an INSERT and return the last row id."""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid
