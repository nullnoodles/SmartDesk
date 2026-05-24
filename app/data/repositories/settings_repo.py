"""Repository for app_settings table — generic key/value store."""
from __future__ import annotations

from app.data.database import Database


class SettingsRepository:
    """Key/value settings store backed by SQLite."""

    def __init__(self, db: Database):
        self.db = db

    def get(self, key: str, default: str | None = None) -> str | None:
        rows = self.db.execute("SELECT value FROM app_settings WHERE key=?", (key,))
        if not rows:
            return default
        value = rows[0]["value"]
        return value if value is not None else default

    def set(self, key: str, value: str | None) -> None:
        self.db.execute(
            """INSERT INTO app_settings(key, value) VALUES (?, ?)
               ON CONFLICT(key) DO UPDATE SET value=excluded.value""",
            (key, value if value is not None else ""),
        )

    def get_all(self) -> dict[str, str]:
        rows = self.db.execute("SELECT key, value FROM app_settings")
        return {row["key"]: row["value"] for row in rows}

    def delete(self, key: str) -> None:
        self.db.execute("DELETE FROM app_settings WHERE key=?", (key,))
