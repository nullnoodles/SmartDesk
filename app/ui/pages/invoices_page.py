"""Invoices page — create, view, export PDF, mark paid — soft UI redesign."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QDoubleSpinBox, QSpinBox, QComboBox, QDialogButtonBox,
    QMessageBox, QFileDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from app.data.database import Database
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.project_repo import ProjectRepository
from app.core.invoice_service import InvoiceService
from app.core.pdf_exporter import PDFExporter
from app.core.settings_service import SettingsService
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedButton


class InvoicesPage(QWidget):
    """Invoice list with create, export PDF, and status management — redesigned."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.repo = InvoiceRepository(db)
        self.project_repo = ProjectRepository(db)
        self.service = InvoiceService(db)
        self.pdf_exporter = PDFExporter()
        self.settings = SettingsService(db)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header_row = QHBoxLayout()
        title = QLabel("Invoices")
        title.setObjectName("heading")
        header_row.addWidget(title)

        self._count_label = QLabel("")
        self._count_label.setObjectName("subheading")
        header_row.addWidget(self._count_label)
        header_row.addStretch()

        add_btn = AnimatedButton("+ Create Invoice", accent=Colors.ACCENT_PRIMARY)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._create_invoice)
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["#", "Invoice No.", "Client", "Project", "Total", "Due Date", "Status"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

        # Actions
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        pdf_btn = AnimatedButton("📄 Export PDF", accent=Colors.ACCENT_INFO)
        pdf_btn.setCursor(Qt.PointingHandCursor)
        pdf_btn.clicked.connect(self._export_pdf)
        btn_row.addWidget(pdf_btn)

        paid_btn = AnimatedButton("✓ Mark Paid", accent=Colors.ACCENT_SUCCESS)
        paid_btn.setCursor(Qt.PointingHandCursor)
        paid_btn.clicked.connect(self._mark_paid)
        btn_row.addWidget(paid_btn)
        layout.addLayout(btn_row)

        self.refresh()

    def refresh(self) -> None:
        try:
            invoices = self.repo.get_all()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load invoices: {e}")
            invoices = []
        self._count_label.setText(f"({len(invoices)} total)")

        # Empty state
        if not invoices:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("No invoices yet — click 'Create Invoice' to add one")
            empty_item.setFlags(Qt.ItemIsEnabled)
            empty_item.setForeground(QColor(Colors.TEXT_MUTED))
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 7)
            return

        self.table.clearSpans()
        self.table.setRowCount(len(invoices))
        for i, inv in enumerate(invoices):
            self.table.setItem(i, 0, QTableWidgetItem(str(inv["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(inv["invoice_number"]))
            self.table.setItem(i, 2, QTableWidgetItem(inv["client_name"]))
            self.table.setItem(i, 3, QTableWidgetItem(inv["project_name"]))
            self.table.setItem(i, 4, QTableWidgetItem(f"₹{inv['total']:,.2f}"))
            self.table.setItem(i, 5, QTableWidgetItem(inv["due_date"] or "—"))

            # Color-coded status (matches DB vocabulary: Paid / Unpaid / Cancelled)
            status_item = QTableWidgetItem(inv["status"])
            status_colors = {
                "Paid": Colors.ACCENT_SUCCESS,
                "Unpaid": Colors.ACCENT_WARNING,
                "Cancelled": Colors.TEXT_MUTED,
            }
            color = status_colors.get(inv["status"], Colors.TEXT_SECONDARY)
            status_item.setForeground(QColor(color))
            self.table.setItem(i, 6, status_item)

    def _create_invoice(self) -> None:
        projects = self.project_repo.get_all()
        if not projects:
            QMessageBox.warning(self, "No Projects", "Create a project first.")
            return
        default_due = self.settings.get_default_due_days()
        dialog = InvoiceDialog(self, projects, default_due_days=default_due)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.service.create_invoice(data["project_id"], data["amount"], due_days=data["due_days"])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create invoice: {e}")
                return
            self.refresh()

    def _export_pdf(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if item is None or not item.text().isdigit():
            return
        invoice_id = int(item.text())
        inv = self.repo.get_by_id(invoice_id)
        if not inv:
            return

        try:
            rows = self.db.execute("""
                SELECT i.*, p.name as project_name, c.name as client_name, c.email as client_email
                FROM invoices i
                JOIN projects p ON i.project_id = p.id
                JOIN clients c ON p.client_id = c.id
                WHERE i.id = ?
            """, (invoice_id,))
            if not rows:
                return

            data = rows[0]
            invoice_data = {
                "invoice_number": data["invoice_number"],
                "client_name": data["client_name"],
                "client_email": data["client_email"],
                "project_name": data["project_name"],
                "amount": data["amount"],
                "tax": data["tax"],
                "total": data["total"],
                "date_issued": data["date_issued"],
                "due_date": data["due_date"],
            }

            business = self.settings.export_business_as_dict()
            path = self.pdf_exporter.export_invoice(invoice_data, business=business)
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Could not export PDF: {e}")
            return
        QMessageBox.information(self, "Exported", f"PDF saved to:\n{path}")

    def _mark_paid(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if item is None or not item.text().isdigit():
            return
        invoice_id = int(item.text())
        try:
            self.service.mark_paid(invoice_id)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not mark paid: {e}")
            return
        self.refresh()


class InvoiceDialog(QDialog):
    """Create invoice dialog — soft styled."""

    def __init__(self, parent=None, projects=None, default_due_days: int = 14):
        super().__init__(parent)
        self.setWindowTitle("Create Invoice")
        self.setMinimumWidth(420)

        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        self.project_combo = QComboBox()
        for p in (projects or []):
            self.project_combo.addItem(f"{p['name']} ({p['client_name']})", p["id"])

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(100, 10_000_000)
        self.amount_input.setPrefix("₹ ")
        self.amount_input.setValue(5000)

        self.due_days_input = QSpinBox()
        self.due_days_input.setRange(1, 90)
        self.due_days_input.setValue(default_due_days)
        self.due_days_input.setSuffix(" days")

        layout.addRow("Project", self.project_combo)
        layout.addRow("Amount (before GST)", self.amount_input)
        layout.addRow("Payment Due In", self.due_days_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self) -> dict:
        return {
            "project_id": self.project_combo.currentData(),
            "amount": self.amount_input.value(),
            "due_days": self.due_days_input.value(),
        }
