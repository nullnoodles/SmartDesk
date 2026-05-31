"""Invoices page — Studio Graphite redesign with stat row, clean table, status pills."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QMessageBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.email_service import EmailService
from app.core.invoice_service import InvoiceService
from app.core.pdf_exporter import PDFExporter
from app.core.settings_service import SettingsService
from app.data.database import Database
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.project_repo import ProjectRepository
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedButton
from app.ui.widgets.page_header import PageHeader
from app.ui.widgets.stat_card import StatCard
from app.ui.widgets.status_pill import StatusPill


class InvoicesPage(QWidget):
    """Invoice list with create/export/mark paid — Studio Graphite design."""

    STATUS_COLORS = {
        "Paid": Colors.ACCENT_SUCCESS,
        "Unpaid": Colors.ACCENT_WARNING,
        "Cancelled": Colors.TEXT_MUTED,
    }

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.repo = InvoiceRepository(db)
        self.project_repo = ProjectRepository(db)
        self.service = InvoiceService(db)
        self.pdf_exporter = PDFExporter()
        self.settings = SettingsService(db)
        self.email = EmailService(db)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # ─── Header ───────────────────────────────────────────────────────
        self.header = PageHeader(
            title="Invoices",
            subtitle="Track payments, export PDFs, and stay on top of receivables",
            count_text="0 total",
        )

        add_btn = AnimatedButton("+ Create Invoice", accent=Colors.ACCENT_PRIMARY)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._create_invoice)
        self.header.add_action(add_btn)
        layout.addWidget(self.header)

        # ─── Stat row ─────────────────────────────────────────────────────
        self.card_revenue = StatCard(
            "Total Revenue", "₹0", icon="💰", accent=Colors.ACCENT_SUCCESS,
            sub_text="Lifetime earnings",
        )
        self.card_pending = StatCard(
            "Pending Payment", "₹0", icon="⏳", accent=Colors.ACCENT_WARNING,
            sub_text="Awaiting collection",
        )
        self.card_overdue = StatCard(
            "Overdue", "₹0", icon="🚨", accent=Colors.ACCENT_DANGER,
            sub_text="Past due date",
        )

        stat_row = QHBoxLayout()
        stat_row.setSpacing(20)
        for c in (self.card_revenue, self.card_pending, self.card_overdue):
            stat_row.addWidget(c, 1)
        layout.addLayout(stat_row)

        # ─── Table ────────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["#", "Invoice No.", "Client", "Project", "Total", "Due Date", "Status"]
        )
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        pdf_btn = AnimatedButton("📄 Export PDF", accent=Colors.ACCENT_INFO)
        pdf_btn.setCursor(Qt.PointingHandCursor)
        pdf_btn.clicked.connect(self._export_pdf)
        btn_row.addWidget(pdf_btn)

        email_btn = AnimatedButton("✉️ Email Invoice", accent=Colors.ACCENT_INFO)
        email_btn.setCursor(Qt.PointingHandCursor)
        email_btn.clicked.connect(self._email_invoice)
        btn_row.addWidget(email_btn)

        remind_btn = AnimatedButton("🔔 Send Reminders", accent=Colors.ACCENT_WARNING)
        remind_btn.setCursor(Qt.PointingHandCursor)
        remind_btn.clicked.connect(self._send_overdue_reminders)
        btn_row.addWidget(remind_btn)

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

        self.header.set_count(f"{len(invoices)} total")

        # Stat values
        try:
            self.card_revenue.set_value(f"₹{self.repo.total_earned():,.0f}")
            self.card_pending.set_value(f"₹{self.repo.total_pending():,.0f}")
            overdue_rows = self.repo.get_overdue()
            overdue_total = sum(float(r["total"]) for r in overdue_rows) if overdue_rows else 0.0
            self.card_overdue.set_value(f"₹{overdue_total:,.0f}")
            self.card_overdue.set_sub_text(
                f"{len(overdue_rows)} invoice(s) overdue" if overdue_rows else "All caught up",
                color=Colors.ACCENT_DANGER if overdue_rows else Colors.ACCENT_SUCCESS,
            )
        except Exception:
            pass

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

            color = self.STATUS_COLORS.get(inv["status"], Colors.TEXT_SECONDARY)
            self.table.setCellWidget(i, 6, StatusPill(inv["status"], color))

    # ------------------------------------------------------------------
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
            rows = self.db.execute(
                """
                SELECT i.*, p.name as project_name, c.name as client_name, c.email as client_email
                FROM invoices i
                JOIN projects p ON i.project_id = p.id
                JOIN clients c ON p.client_id = c.id
                WHERE i.id = ?
                """,
                (invoice_id,),
            )
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

    # ------------------------------------------------------------------
    # Email helpers
    # ------------------------------------------------------------------
    def _selected_invoice_data(self) -> dict | None:
        row = self.table.currentRow()
        if row < 0:
            return None
        item = self.table.item(row, 0)
        if item is None or not item.text().isdigit():
            return None
        invoice_id = int(item.text())
        rows = self.db.execute(
            """
            SELECT i.*, p.name as project_name, c.name as client_name, c.email as client_email
            FROM invoices i
            JOIN projects p ON i.project_id = p.id
            JOIN clients c ON p.client_id = c.id
            WHERE i.id = ?
            """,
            (invoice_id,),
        )
        return rows[0] if rows else None

    def _email_invoice(self) -> None:
        data = self._selected_invoice_data()
        if not data:
            QMessageBox.information(self, "Email Invoice", "Select an invoice first.")
            return
        if not data["client_email"]:
            QMessageBox.warning(
                self,
                "Missing Email",
                f"{data['client_name']} has no email address on file.",
            )
            return

        # Build PDF if missing
        try:
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
            pdf_path = self.pdf_exporter.export_invoice(invoice_data, business=business)
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Could not generate PDF: {e}")
            return

        biz_name = self.settings.get_business().name
        subject = self.email.invoice_subject(data["invoice_number"], biz_name)
        body = self.email.invoice_body(
            client_name=data["client_name"],
            invoice_number=data["invoice_number"],
            total=float(data["total"]),
            due_date=data["due_date"] or "—",
            business_name=biz_name,
        )

        confirm = QMessageBox.question(
            self,
            "Send Invoice",
            f"Send {data['invoice_number']} to {data['client_email']}?\n\n"
            "Subject: " + subject,
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            self.email.send(data["client_email"], subject, body, attachment=pdf_path)
        except Exception as e:
            QMessageBox.critical(self, "Email Failed", f"Could not send: {e}")
            return
        QMessageBox.information(self, "Sent", f"Invoice emailed to {data['client_email']}.")

    def _send_overdue_reminders(self) -> None:
        try:
            overdue_rows = self.db.execute(
                """
                SELECT i.invoice_number, i.total, i.due_date, c.name as client_name,
                       c.email as client_email
                FROM invoices i
                JOIN projects p ON i.project_id = p.id
                JOIN clients c ON p.client_id = c.id
                WHERE i.status = 'Unpaid' AND i.due_date < DATE('now')
                ORDER BY i.due_date ASC
                """
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load overdue invoices: {e}")
            return

        with_emails = [r for r in overdue_rows if r["client_email"]]
        if not with_emails:
            QMessageBox.information(
                self,
                "No Reminders Needed",
                "No overdue invoices have a client email address on file.",
            )
            return

        confirm = QMessageBox.question(
            self,
            "Send Reminders",
            f"Send overdue reminders to {len(with_emails)} client(s)?",
        )
        if confirm != QMessageBox.Yes:
            return

        from datetime import date

        biz_name = self.settings.get_business().name
        sent = 0
        failures: list[str] = []
        today = date.today()

        for row in with_emails:
            try:
                due = date.fromisoformat(row["due_date"])
                days_overdue = max((today - due).days, 1)
            except Exception:
                days_overdue = 1

            subject = self.email.overdue_subject(row["invoice_number"])
            body = self.email.overdue_body(
                client_name=row["client_name"],
                invoice_number=row["invoice_number"],
                total=float(row["total"]),
                due_date=row["due_date"] or "—",
                days_overdue=days_overdue,
                business_name=biz_name,
            )
            try:
                self.email.send(row["client_email"], subject, body)
                sent += 1
            except Exception as e:
                failures.append(f"{row['invoice_number']}: {e}")

        if failures:
            QMessageBox.warning(
                self,
                "Partial Success",
                f"Sent {sent} reminder(s). Failed:\n" + "\n".join(failures[:5]),
            )
        else:
            QMessageBox.information(self, "Done", f"Sent {sent} overdue reminder(s).")


class InvoiceDialog(QDialog):
    """Create invoice dialog."""

    def __init__(self, parent=None, projects=None, default_due_days: int = 14):
        super().__init__(parent)
        self.setWindowTitle("Create Invoice")
        self.setMinimumWidth(440)

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
