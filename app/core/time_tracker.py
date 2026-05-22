"""Time tracking service with start/stop and manual entry."""
from __future__ import annotations

import datetime

from app.data.database import Database
from app.data.repositories.time_log_repo import TimeLogRepository


class TimeTracker:
    """Manages time logging for projects."""

    def __init__(self, db: Database):
        self.repo = TimeLogRepository(db)
        self._active_session: dict | None = None

    @property
    def is_running(self) -> bool:
        return self._active_session is not None

    def start(self, project_id: int, description: str = "") -> None:
        """Start a new time tracking session."""
        if self._active_session:
            raise RuntimeError("A session is already running. Stop it first.")
        self._active_session = {
            "project_id": project_id,
            "start_time": datetime.datetime.now().isoformat(),
            "description": description,
        }

    def stop(self) -> float:
        """Stop the current session and save to DB. Returns hours logged."""
        if not self._active_session:
            raise RuntimeError("No active session to stop.")

        end_time = datetime.datetime.now()
        start_time = datetime.datetime.fromisoformat(self._active_session["start_time"])
        duration = (end_time - start_time).total_seconds() / 3600

        self.repo.add(
            project_id=self._active_session["project_id"],
            start_time=self._active_session["start_time"],
            end_time=end_time.isoformat(),
            duration_hours=round(duration, 2),
            description=self._active_session["description"],
        )
        self._active_session = None
        return round(duration, 2)

    def add_manual(self, project_id: int, hours: float, description: str = "") -> None:
        """Add a manual time entry."""
        now = datetime.datetime.now()
        start = (now - datetime.timedelta(hours=hours)).isoformat()
        self.repo.add(
            project_id=project_id,
            start_time=start,
            end_time=now.isoformat(),
            duration_hours=hours,
            description=description,
        )
