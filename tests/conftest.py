"""Shared pytest fixtures for SmartDesk tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path so `import app...` works
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.data.database import Database  # noqa: E402


@pytest.fixture
def db(tmp_path) -> Database:
    """Provide a clean Database instance backed by a per-test SQLite file."""
    db_file = tmp_path / "test_smartdesk.db"
    database = Database(db_file)
    database.initialize()
    yield database
    database.close()
