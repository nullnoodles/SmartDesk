"""Repository for contracts table."""
from __future__ import annotations

from app.data.database import Database


class ContractRepository:
    def __init__(self, db: Database):
        self.db = db

    def add(self, project_id: int, contract_text: str, hourly_rate: float,
            revision_rounds: int, timeline_days: int, risk_score: int,
            risk_level: str, findings: str) -> int:
        return self.db.execute_returning_id(
            """INSERT INTO contracts
               (project_id, contract_text, hourly_rate, revision_rounds,
                timeline_days, risk_score, risk_level, findings)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_id, contract_text, hourly_rate, revision_rounds,
             timeline_days, risk_score, risk_level, findings),
        )

    def get_by_project(self, project_id: int):
        rows = self.db.execute(
            "SELECT * FROM contracts WHERE project_id = ? ORDER BY analyzed_date DESC",
            (project_id,),
        )
        return rows[0] if rows else None

    def get_all(self) -> list:
        return self.db.execute("SELECT * FROM contracts ORDER BY analyzed_date DESC")
