"""Repository for projects table."""
from __future__ import annotations

from app.data.database import Database


class ProjectRepository:
    def __init__(self, db: Database):
        self.db = db

    def add(self, client_id: int, name: str, project_type: str, description: str, deadline: str, budget: float = 0) -> int:
        return self.db.execute_returning_id(
            "INSERT INTO projects (client_id, name, type, description, deadline, budget) VALUES (?, ?, ?, ?, ?, ?)",
            (client_id, name, project_type, description, deadline, budget),
        )

    def get_all(self) -> list:
        return self.db.execute(
            """SELECT p.*, c.name as client_name
               FROM projects p JOIN clients c ON p.client_id = c.id
               ORDER BY p.created_date DESC"""
        )

    def get_by_id(self, project_id: int):
        rows = self.db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        return rows[0] if rows else None

    def get_by_client(self, client_id: int) -> list:
        return self.db.execute("SELECT * FROM projects WHERE client_id = ? ORDER BY created_date DESC", (client_id,))

    def update_status(self, project_id: int, status: str) -> None:
        self.db.execute("UPDATE projects SET status=? WHERE id=?", (status, project_id))

    def update(self, project_id: int, name: str, project_type: str, description: str, deadline: str, budget: float, status: str) -> None:
        self.db.execute(
            "UPDATE projects SET name=?, type=?, description=?, deadline=?, budget=?, status=? WHERE id=?",
            (name, project_type, description, deadline, budget, status, project_id),
        )

    def delete(self, project_id: int) -> None:
        self.db.execute("DELETE FROM projects WHERE id=?", (project_id,))

    def count(self) -> int:
        rows = self.db.execute("SELECT COUNT(*) as cnt FROM projects")
        return rows[0]["cnt"] if rows else 0

    def count_by_status(self, status: str) -> int:
        rows = self.db.execute("SELECT COUNT(*) as cnt FROM projects WHERE status=?", (status,))
        return rows[0]["cnt"] if rows else 0

    def count_all_statuses(self) -> dict[str, int]:
        """Return counts for all statuses in a single query."""
        rows = self.db.execute("SELECT status, COUNT(*) as cnt FROM projects GROUP BY status")
        return {row["status"]: row["cnt"] for row in rows}
