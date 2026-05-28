"""Clients page — Studio Graphite redesign with stat row + clean table."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.data.database import Database
from app.data.repositories.client_repo import ClientRepository
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedButton
from app.ui.widgets.page_header import PageHeader
from app.ui.widgets.stat_card import StatCard


class ClientsPage(QWidget):
    """Client list with add/edit/delete/search — Studio Graphite design."""

    def __init__(self, db: Database):
        super().__init__()
        self.repo = ClientRepository(db)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # ─── Header ───────────────────────────────────────────────────────
        self.header = PageHeader(
            title="Clients",
            subtitle="Manage your active client base and relationships",
            count_text="0 total",
        )

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search clients...")
        self.search_input.setFixedWidth(280)
        self.search_input.textChanged.connect(self._on_search)
        self.header.add_action(self.search_input)

        add_btn = AnimatedButton("+ Add Client", accent=Colors.ACCENT_PRIMARY)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_client)
        self.header.add_action(add_btn)

        layout.addWidget(self.header)

        # ─── Stat row ─────────────────────────────────────────────────────
        self.card_total = StatCard(
            "Total Clients", "0", icon="👥", accent=Colors.ACCENT_PRIMARY_LIGHT,
            sub_text="Active relationships",
        )
        self.card_new = StatCard(
            "New This Month", "0", icon="🌱", accent=Colors.ACCENT_SUCCESS,
            sub_text="—", sub_color=Colors.ACCENT_SUCCESS,
        )
        self.card_companies = StatCard(
            "Companies", "0", icon="🏢", accent=Colors.ACCENT_INFO,
            sub_text="Distinct employers",
        )

        stat_row = QHBoxLayout()
        stat_row.setSpacing(20)
        for card in (self.card_total, self.card_new, self.card_companies):
            stat_row.addWidget(card, 1)
        layout.addLayout(stat_row)

        # ─── Table ────────────────────────────────────────────────────────
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Email", "Phone", "Company", "Created"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.doubleClicked.connect(self._edit_client)
        layout.addWidget(self.table)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        edit_btn = AnimatedButton("Edit", accent=Colors.ACCENT_INFO)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(self._edit_client)
        btn_row.addWidget(edit_btn)

        del_btn = AnimatedButton("Delete", accent=Colors.ACCENT_DANGER)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(self._delete_client)
        btn_row.addWidget(del_btn)
        layout.addLayout(btn_row)

        self.refresh()

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        try:
            clients = self.repo.get_all()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load clients: {e}")
            clients = []
        self.header.set_count(f"{len(clients)} total")
        self.card_total.set_value(str(len(clients)))

        # Companies count (distinct, non-empty)
        companies = {(c["company"] or "").strip() for c in clients if (c["company"] or "").strip()}
        self.card_companies.set_value(str(len(companies)))

        # New this month — use created_date string starting with current YYYY-MM
        from datetime import date
        prefix = date.today().strftime("%Y-%m")
        new_count = sum(1 for c in clients if (c["created_date"] or "").startswith(prefix))
        self.card_new.set_value(str(new_count))
        self.card_new.set_sub_text(
            "↑ This month" if new_count else "No new clients this month",
            color=Colors.ACCENT_SUCCESS if new_count else Colors.TEXT_MUTED,
        )

        self._populate_table(clients)

    def _populate_table(self, clients: list) -> None:
        if not clients:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("No clients yet — click '+ Add Client' to add one")
            empty_item.setFlags(Qt.ItemIsEnabled)
            empty_item.setForeground(QColor(Colors.TEXT_MUTED))
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 6)
            return

        self.table.clearSpans()
        self.table.setRowCount(len(clients))
        for i, c in enumerate(clients):
            self.table.setItem(i, 0, QTableWidgetItem(str(c["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(c["name"]))
            self.table.setItem(i, 2, QTableWidgetItem(c["email"] or "—"))
            self.table.setItem(i, 3, QTableWidgetItem(c["phone"] or "—"))
            self.table.setItem(i, 4, QTableWidgetItem(c["company"] or "—"))
            self.table.setItem(i, 5, QTableWidgetItem(c["created_date"] or "—"))

    def _on_search(self, text: str) -> None:
        try:
            results = self.repo.search(text) if text.strip() else self.repo.get_all()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Search failed: {e}")
            results = []
        self._populate_table(results)

    # ------------------------------------------------------------------
    # CRUD handlers
    # ------------------------------------------------------------------
    def _add_client(self) -> None:
        dialog = ClientDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.repo.add(**data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not add client: {e}")
                return
            self.refresh()

    def _edit_client(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if item is None or not item.text().isdigit():
            return
        client_id = int(item.text())
        client = self.repo.get_by_id(client_id)
        if not client:
            return
        dialog = ClientDialog(self, client)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.repo.update(client_id, **data)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not update client: {e}")
                return
            self.refresh()

    def _delete_client(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if item is None or not item.text().isdigit():
            return
        client_id = int(item.text())
        reply = QMessageBox.question(self, "Delete", "Delete this client and all related data?")
        if reply == QMessageBox.Yes:
            try:
                self.repo.delete(client_id)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete client: {e}")
                return
            self.refresh()


class ClientDialog(QDialog):
    """Add/Edit client dialog."""

    def __init__(self, parent=None, client=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Client" if client else "Add Client")
        self.setMinimumWidth(440)

        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        self.name_input = QLineEdit(client["name"] if client else "")
        self.name_input.setPlaceholderText("Client name")
        self.email_input = QLineEdit(client["email"] if client else "")
        self.email_input.setPlaceholderText("email@example.com")
        self.phone_input = QLineEdit(client["phone"] if client else "")
        self.phone_input.setPlaceholderText("+91 XXXXX XXXXX")
        self.address_input = QLineEdit(client["address"] if client else "")
        self.address_input.setPlaceholderText("Address")
        self.company_input = QLineEdit(client["company"] if client else "")
        self.company_input.setPlaceholderText("Company name")

        layout.addRow("Name *", self.name_input)
        layout.addRow("Email", self.email_input)
        layout.addRow("Phone", self.phone_input)
        layout.addRow("Address", self.address_input)
        layout.addRow("Company", self.company_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def accept(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation", "Client name is required.")
            self.name_input.setFocus()
            return
        email = self.email_input.text().strip()
        if email and "@" not in email:
            QMessageBox.warning(self, "Validation", "Please enter a valid email address.")
            self.email_input.setFocus()
            return
        super().accept()

    def get_data(self) -> dict:
        return {
            "name": self.name_input.text().strip(),
            "email": self.email_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "address": self.address_input.text().strip(),
            "company": self.company_input.text().strip(),
        }
