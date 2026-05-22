"""Repository for payments table."""
from __future__ import annotations

from app.data.database import Database


class PaymentRepository:
    def __init__(self, db: Database):
        self.db = db

    def add(self, invoice_id: int, amount_paid: float, payment_mode: str, reference: str = "") -> int:
        return self.db.execute_returning_id(
            "INSERT INTO payments (invoice_id, amount_paid, payment_mode, reference) VALUES (?, ?, ?, ?)",
            (invoice_id, amount_paid, payment_mode, reference),
        )

    def get_by_invoice(self, invoice_id: int) -> list:
        return self.db.execute(
            "SELECT * FROM payments WHERE invoice_id = ? ORDER BY payment_date DESC",
            (invoice_id,),
        )

    def total_paid_for_invoice(self, invoice_id: int) -> float:
        rows = self.db.execute(
            "SELECT COALESCE(SUM(amount_paid), 0) as total FROM payments WHERE invoice_id = ?",
            (invoice_id,),
        )
        return rows[0]["total"] if rows else 0
