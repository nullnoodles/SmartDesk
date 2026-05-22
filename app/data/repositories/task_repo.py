"""Repository for tasks table."""
from __future__ import annotations

from app.data.database import Database


class TaskRepository:
    def __init__(self, db: Database):
        self.db = db

    def add(self, project_id: int, title: str, due_date: str = "") -> int:
        return self.db.execute_returning_id(
            "INSERT INTO tasks (project_id, title, due_date) VALUES (?, ?, ?)",
            (project_id, title, due_date),
        )

    def get_by_project(self, project_id: int) -> list:
        return self.db.execute(
            "SELECT * FROM tasks WHERE project_id = ? ORDER BY is_completed, due_date",
            (project_id,),
        )

    def toggle_complete(self, task_id: int) -> None:
        self.db.execute(
            "UPDATE tasks SET is_completed = CASE WHEN is_completed = 0 THEN 1 ELSE 0 END WHERE id = ?",
            (task_id,),
        )

    def delete(self, task_id: int) -> None:
        self.db.execute("DELETE FROM tasks WHERE id=?", (task_id,))

    def pending_count(self) -> int:
        rows = self.db.execute("SELECT COUNT(*) as cnt FROM tasks WHERE is_completed = 0")
        return rows[0]["cnt"] if rows else 0
