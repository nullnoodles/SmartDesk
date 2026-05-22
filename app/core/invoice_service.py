
from __future__ import annotations

import datetime

from app.config import GST_RATE
from app.data.database import Database
from app.data.repositories.invoice_repo import InvoiceRepository


class InvoiceService:
    """Handles invoice creation logic, number generation, and status transitions."""

    def __init__(self, db: Database):
        self.repo = InvoiceRepository(db)

    def create_invoice(self, project_id: int, amount: float, due_days: int = 14, notes: str = "") -> str:
        """Create a new invoice with auto-generated number and GST calculation."""
        invoice_number = self.repo.next_invoice_number()
        tax = round(amount * GST_RATE, 2)
        total = round(amount + tax, 2)
        due_date = (datetime.date.today() + datetime.timedelta(days=due_days)).isoformat()

        self.repo.add(
            project_id=project_id,
            invoice_number=invoice_number,
            amount=amount,
            tax=tax,
            total=total,
            due_date=due_date,
            notes=notes,
        )
        return invoice_number

    def mark_paid(self, invoice_id: int) -> None:
        self.repo.update_status(invoice_id, "Paid")

    def mark_cancelled(self, invoice_id: int) -> None:
        self.repo.update_status(invoice_id, "Cancelled")
