"""CSV export utility for clients, projects, and invoices."""
from __future__ import annotations

import csv
from pathlib import Path

from app.data.database import Database
from app.data.repositories.client_repo import ClientRepository
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.project_repo import ProjectRepository


class CSVExporter:
    """Export tabular data to CSV files for accountants / spreadsheets."""

    def __init__(self, db: Database):
        self.db = db
        self.clients = ClientRepository(db)
        self.projects = ProjectRepository(db)
        self.invoices = InvoiceRepository(db)

    def export_clients(self, path: Path) -> Path:
        rows = self.clients.get_all()
        return self._write(
            path,
            ["id", "name", "email", "phone", "address", "company", "created_date"],
            rows,
        )

    def export_projects(self, path: Path) -> Path:
        rows = self.projects.get_all()
        return self._write(
            path,
            [
                "id",
                "name",
                "client_name",
                "type",
                "status",
                "deadline",
                "budget",
                "created_date",
            ],
            rows,
        )

    def export_invoices(self, path: Path) -> Path:
        rows = self.invoices.get_all()
        return self._write(
            path,
            [
                "id",
                "invoice_number",
                "client_name",
                "project_name",
                "amount",
                "tax",
                "total",
                "date_issued",
                "due_date",
                "status",
            ],
            rows,
        )

    @staticmethod
    def _write(path: Path, columns: list[str], rows: list) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            for row in rows:
                writer.writerow([row[c] if c in row.keys() else "" for c in columns])
        return path
