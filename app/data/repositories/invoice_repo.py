"""Repository for invoices table."""
from __future__ import annotations

from app.data.database import Database


class InvoiceRepository:
    def __init__(self, db: Database):
        self.db = db

    def add(self, project_id: int, invoice_number: str, amount: float, tax: float, total: float, due_date: str, notes: str = "") -> int:
        return self.db.execute_returning_id(
            """INSERT INTO invoices (project_id, invoice_number, amount, tax, total, due_date, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (project_id, invoice_number, amount, tax, total, due_date, notes),
        )

    def get_all(self) -> list:
        return self.db.execute(
            """SELECT i.*, p.name as project_name, c.name as client_name
               FROM invoices i
               JOIN projects p ON i.project_id = p.id
               JOIN clients c ON p.client_id = c.id
               ORDER BY i.date_issued DESC"""
        )

    def get_by_id(self, invoice_id: int):
        rows = self.db.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        return rows[0] if rows else None

    def get_by_number(self, invoice_number: str):
        rows = self.db.execute("SELECT * FROM invoices WHERE invoice_number = ?", (invoice_number,))
        return rows[0] if rows else None

    def get_unpaid(self) -> list:
        return self.db.execute(
            """SELECT i.*, p.name as project_name, c.name as client_name
               FROM invoices i
               JOIN projects p ON i.project_id = p.id
               JOIN clients c ON p.client_id = c.id
               WHERE i.status = 'Unpaid'
               ORDER BY i.due_date ASC"""
        )

    def get_overdue(self) -> list:
        return self.db.execute(
            """SELECT i.*, p.name as project_name, c.name as client_name
               FROM invoices i
               JOIN projects p ON i.project_id = p.id
               JOIN clients c ON p.client_id = c.id
               WHERE i.status = 'Unpaid' AND i.due_date < DATE('now')
               ORDER BY i.due_date ASC"""
        )

    def update_status(self, invoice_id: int, status: str) -> None:
        self.db.execute("UPDATE invoices SET status=? WHERE id=?", (status, invoice_id))

    def next_invoice_number(self) -> str:
        """Generate next invoice number using current year, scoped per-year."""
        from datetime import date
        from app.config import INVOICE_PREFIX
        year = date.today().year
        prefix = f"{INVOICE_PREFIX}-{year}-"
        rows = self.db.execute(
            "SELECT COUNT(*) as cnt FROM invoices WHERE invoice_number LIKE ?",
            (f"{prefix}%",),
        )
        count = (rows[0]["cnt"] if rows else 0) + 1
        return f"{prefix}{count:04d}"

    def total_earned(self) -> float:
        rows = self.db.execute("SELECT COALESCE(SUM(total), 0) as total FROM invoices WHERE status='Paid'")
        return rows[0]["total"] if rows else 0

    def total_pending(self) -> float:
        rows = self.db.execute("SELECT COALESCE(SUM(total), 0) as total FROM invoices WHERE status='Unpaid'")
        return rows[0]["total"] if rows else 0
