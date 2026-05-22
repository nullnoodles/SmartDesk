"""Repository for clients table."""
from __future__ import annotations

from app.data.database import Database


class ClientRepository:
    def __init__(self, db: Database):
        self.db = db

    def add(self, name: str, email: str, phone: str, address: str, company: str, notes: str = "") -> int:
        return self.db.execute_returning_id(
            "INSERT INTO clients (name, email, phone, address, company, notes) VALUES (?, ?, ?, ?, ?, ?)",
            (name, email, phone, address, company, notes),
        )

    def get_all(self) -> list:
        return self.db.execute("SELECT * FROM clients ORDER BY name")

    def get_by_id(self, client_id: int):
        rows = self.db.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        return rows[0] if rows else None

    def search(self, keyword: str) -> list:
        kw = f"%{keyword}%"
        return self.db.execute(
            "SELECT * FROM clients WHERE name LIKE ? OR email LIKE ? OR company LIKE ?",
            (kw, kw, kw),
        )

    def update(self, client_id: int, name: str, email: str, phone: str, address: str, company: str, notes: str = "") -> None:
        self.db.execute(
            "UPDATE clients SET name=?, email=?, phone=?, address=?, company=?, notes=? WHERE id=?",
            (name, email, phone, address, company, notes, client_id),
        )

    def delete(self, client_id: int) -> None:
        self.db.execute("DELETE FROM clients WHERE id=?", (client_id,))

    def count(self) -> int:
        rows = self.db.execute("SELECT COUNT(*) as cnt FROM clients")
        return rows[0]["cnt"] if rows else 0
