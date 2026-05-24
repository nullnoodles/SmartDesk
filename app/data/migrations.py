"""Schema migration runner.

Tracks a single integer version in the `schema_version` table. Each migration
is a callable that receives the active sqlite connection and applies its
DDL/DML changes. Migrations are idempotent — they only run once per database.
"""
from __future__ import annotations

import sqlite3
from typing import Callable


# ---------------------------------------------------------------------------
# Migrations registry
# ---------------------------------------------------------------------------

def _migration_001_app_settings(conn: sqlite3.Connection) -> None:
    """Add app_settings table (key/value store for user preferences)."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )


# Ordered list of migrations: (target_version, callable)
MIGRATIONS: list[tuple[int, Callable[[sqlite3.Connection], None]]] = [
    (1, _migration_001_app_settings),
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def _ensure_version_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY
        )
        """
    )


def _current_version(conn: sqlite3.Connection) -> int:
    cur = conn.execute("SELECT MAX(version) FROM schema_version")
    row = cur.fetchone()
    return (row[0] or 0) if row else 0


def run_migrations(conn: sqlite3.Connection) -> int:
    """Run any pending migrations. Returns the new schema version."""
    _ensure_version_table(conn)
    version = _current_version(conn)

    for target, migration in MIGRATIONS:
        if target > version:
            migration(conn)
            conn.execute("INSERT INTO schema_version(version) VALUES (?)", (target,))
            version = target
            conn.commit()

    return version
