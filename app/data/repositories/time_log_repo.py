"""Repository for time_logs table."""
from __future__ import annotations

from app.data.database import Database


class TimeLogRepository:
    def __init__(self, db: Database):
        self.db = db

    def add(self, project_id: int, start_time: str, end_time: str, duration_hours: float, description: str = "") -> int:
        return self.db.execute_returning_id(
            "INSERT INTO time_logs (project_id, start_time, end_time, duration_hours, description) VALUES (?, ?, ?, ?, ?)",
            (project_id, start_time, end_time, duration_hours, description),
        )

    def get_by_project(self, project_id: int) -> list:
        return self.db.execute(
            "SELECT * FROM time_logs WHERE project_id = ? ORDER BY start_time DESC",
            (project_id,),
        )

    def total_hours_for_project(self, project_id: int) -> float:
        rows = self.db.execute(
            "SELECT COALESCE(SUM(duration_hours), 0) as total FROM time_logs WHERE project_id = ?",
            (project_id,),
        )
        return rows[0]["total"] if rows else 0

    def get_recent(self, limit: int = 20) -> list:
        return self.db.execute(
            """SELECT t.*, p.name as project_name
               FROM time_logs t JOIN projects p ON t.project_id = p.id
               ORDER BY t.start_time DESC LIMIT ?""",
            (limit,),
        )
