"""
Clients Page — Modern client management with CRUD operations.

Features: Add/Edit/Delete clients, search functionality, stats overview,
and clean table interface following Studio Graphite design system.
"""
from __future__ import annotations

from datetime import date

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
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
    """
    Client management page with search, stats, and CRUD operations.
    
    Layout Structure:
    ┌─────────────────────────────────────────────────────────────┐
    │ Page Header          [Search]  [+ Add Client]              │
    │ ─────────────────────────────────────────────────────────── │
    │ [Total Clients]  [New This Month]  [Companies]             │
    │ ─────────────────────────────────────────────────────────── │
    │ Clients Table                                               │
    │ ─────────────────────────────────────────────────────────── │
    │                              [Edit]  [Delete]               │
    └─────────────────────────────────────────────────────────────┘
    """

    def __init__(self, db: Database):
        super().__init__()
        self.repo = ClientRepository(db)

        # Main layout with consistent spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(28)

        # Build UI sections
        self._build_header(layout)
        self._build_stat_cards(layout)
        self._build_table(layout)
        self._build_action_buttons(layout)
        
        # Load initial data
        self.refresh()

    # ══════════════════════════════════════════════════════════════════
    # UI CONSTRUCTION METHODS
    # ══════════════════════════════════════════════════════════════════

    def _build_header(self, parent_layout: QVBoxLayout) -> None:
        """Build page header with title, search, and add button."""
        self.header = PageHeader(
            title="Clients",
            subtitle="Manage your active client base and relationships",
            count_text="0 total",
        )

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Search clients by name, email, or company...")
        self.search_input.setFixedWidth(320)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_ELEVATED};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: 10px;
                padding: 9px 14px;
                color: {Colors.TEXT_PRIMARY};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Colors.BORDER_FOCUS};
                background-color: {Colors.BG_CARD};
            }}
            QLineEdit::placeholder {{
                color: {Colors.TEXT_MUTED};
            }}
        """)
        self.search_input.textChanged.connect(self._on_search)
        self.header.add_action(self.search_input)

        # Add client button
        add_btn = AnimatedButton("+ Add Client", accent=Colors.ACCENT_PRIMARY)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(38)
        add_btn.clicked.connect(self._add_client)
        self.header.add_action(add_btn)

        parent_layout.addWidget(self.header)

    def _build_stat_cards(self, parent_layout: QVBoxLayout) -> None:
        """Build KPI stat cards row."""
        stat_row = QHBoxLayout()
        stat_row.setSpacing(22)

        # Total clients card
        self.card_total = StatCard(
            "Total Clients",
            "0",
            icon="👥",
            accent=Colors.ACCENT_PRIMARY_LIGHT,
            sub_text="Active relationships",
        )

        # New clients this month card
        self.card_new = StatCard(
            "New This Month",
            "0",
            icon="🌱",
            accent=Colors.ACCENT_SUCCESS,
            sub_text="—",
            sub_color=Colors.ACCENT_SUCCESS,
        )

        # Companies card
        self.card_companies = StatCard(
            "Companies",
            "0",
            icon="🏢",
            accent=Colors.ACCENT_INFO,
            sub_text="Distinct employers",
        )

        # Add all cards with equal stretch
        for card in (self.card_total, self.card_new, self.card_companies):
            stat_row.addWidget(card, 1)
        
        parent_layout.addLayout(stat_row)

    def _build_table(self, parent_layout: QVBoxLayout) -> None:
        """Build the clients data table."""
        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Name",
            "Email",
            "Phone",
            "Company",
            "Created"
        ])
        
        # Table configuration
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(400)
        
        # Double-click to edit
        self.table.doubleClicked.connect(self._edit_client)
        
        # Adjust column widths for better proportions
        header = self.table.horizontalHeader()
        header.setDefaultSectionSize(140)
        self.table.setColumnWidth(0, 60)   # ID (narrow)
        self.table.setColumnWidth(1, 180)  # Name (wider)
        self.table.setColumnWidth(2, 220)  # Email (wider)
        
        parent_layout.addWidget(self.table)

    def _build_action_buttons(self, parent_layout: QVBoxLayout) -> None:
        """Build action buttons row (Edit, Delete)."""
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)
        btn_row.addStretch()

        # Edit button
        edit_btn = AnimatedButton("✏️  Edit", accent=Colors.ACCENT_INFO)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setFixedHeight(38)
        edit_btn.setMinimumWidth(100)
        edit_btn.clicked.connect(self._edit_client)
        btn_row.addWidget(edit_btn)

        # Delete button
        del_btn = AnimatedButton("🗑️  Delete", accent=Colors.ACCENT_DANGER)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setFixedHeight(38)
        del_btn.setMinimumWidth(100)
        del_btn.clicked.connect(self._delete_client)
        btn_row.addWidget(del_btn)
        
        parent_layout.addLayout(btn_row)

    # ══════════════════════════════════════════════════════════════════
    # DATA LOADING AND REFRESH
    # ══════════════════════════════════════════════════════════════════

    def refresh(self) -> None:
        """
        Refresh all client data from database.
        Updates stats and table with latest information.
        """
        try:
            clients = self.repo.get_all()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load clients: {e}")
            clients = []
        
        # Update header count
        self.header.set_count(f"{len(clients)} total")
        
        # Update total clients card
        self.card_total.set_value(str(len(clients)))

        # Update companies count (distinct, non-empty)
        companies = {
            (c["company"] or "").strip()
            for c in clients
            if (c["company"] or "").strip()
        }
        self.card_companies.set_value(str(len(companies)))

        # Update new clients this month
        prefix = date.today().strftime("%Y-%m")
        new_count = sum(
            1 for c in clients
            if (c["created_date"] or "").startswith(prefix)
        )
        self.card_new.set_value(str(new_count))
        self.card_new.set_sub_text(
            "↑ This month" if new_count else "No new clients this month",
            color=Colors.ACCENT_SUCCESS if new_count else Colors.TEXT_MUTED,
        )

        # Populate table
        self._populate_table(clients)

    def _populate_table(self, clients: list) -> None:
        """
        Populate table with client data.
        
        Args:
            clients: List of client dictionaries from repository
        """
        # Empty state handling
        if not clients:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem(
                "No clients yet — click '+ Add Client' to get started"
            )
            empty_item.setFlags(Qt.ItemIsEnabled)
            empty_item.setForeground(QColor(Colors.TEXT_MUTED))
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 6)
            return

        # Clear any previous spans
        self.table.clearSpans()
        
        # Populate rows
        self.table.setRowCount(len(clients))
        for i, c in enumerate(clients):
            # ID column
            id_item = QTableWidgetItem(str(c["id"]))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setForeground(QColor(Colors.TEXT_MUTED))
            self.table.setItem(i, 0, id_item)
            
            # Name column (bold)
            name_item = QTableWidgetItem(c["name"])
            name_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            self.table.setItem(i, 1, name_item)
            
            # Email column
            email_item = QTableWidgetItem(c["email"] or "—")
            email_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 2, email_item)
            
            # Phone column
            phone_item = QTableWidgetItem(c["phone"] or "—")
            phone_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 3, phone_item)
            
            # Company column
            company_item = QTableWidgetItem(c["company"] or "—")
            company_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 4, company_item)
            
            # Created date column
            created_item = QTableWidgetItem(c["created_date"] or "—")
            created_item.setForeground(QColor(Colors.TEXT_MUTED))
            self.table.setItem(i, 5, created_item)

    def _on_search(self, text: str) -> None:
        """
        Handle search input changes.
        Filters table based on search text.
        
        Args:
            text: Search query string
        """
        try:
            if text.strip():
                results = self.repo.search(text)
            else:
                results = self.repo.get_all()
        except Exception as e:
            QMessageBox.warning(self, "Search Error", f"Search failed: {e}")
            results = []
        
        self._populate_table(results)

    # ══════════════════════════════════════════════════════════════════
    # CRUD OPERATIONS
    # ══════════════════════════════════════════════════════════════════

    def _add_client(self) -> None:
        """Open dialog to add a new client."""
        dialog = ClientDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.repo.add(**data)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Client '{data['name']}' added successfully!"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not add client: {e}")
                return
            self.refresh()

    def _edit_client(self) -> None:
        """Open dialog to edit selected client."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a client to edit."
            )
            return
        
        # Get client ID from first column
        item = self.table.item(row, 0)
        if item is None or not item.text().isdigit():
            return
        
        client_id = int(item.text())
        client = self.repo.get_by_id(client_id)
        
        if not client:
            QMessageBox.warning(self, "Error", "Client not found.")
            return
        
        # Open edit dialog
        dialog = ClientDialog(self, client)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.repo.update(client_id, **data)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Client '{data['name']}' updated successfully!"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not update client: {e}")
                return
            self.refresh()

    def _delete_client(self) -> None:
        """Delete selected client after confirmation."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a client to delete."
            )
            return
        
        # Get client info
        item = self.table.item(row, 0)
        if item is None or not item.text().isdigit():
            return
        
        client_id = int(item.text())
        client_name = self.table.item(row, 1).text()
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete client '{client_name}'?\n\n"
            "This will also delete all related projects, invoices, and time logs.\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.repo.delete(client_id)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Client '{client_name}' deleted successfully."
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete client: {e}")
                return
            self.refresh()


class ClientDialog(QDialog):
    """
    Dialog for adding or editing a client.
    Clean form layout with validation.
    """

    def __init__(self, parent=None, client=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Client" if client else "Add New Client")
        self.setMinimumWidth(500)
        
        # Apply modern styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BG_DARK};
            }}
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: 13px;
                font-weight: 500;
            }}
        """)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(24)

        # Dialog title
        title = QLabel("Edit Client Details" if client else "Add New Client")
        title.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.01em;
        """)
        layout.addWidget(title)

        # Form layout
        form = QFormLayout()
        form.setSpacing(16)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Input fields
        self.name_input = QLineEdit(client["name"] if client else "")
        self.name_input.setPlaceholderText("Enter client name")
        
        self.email_input = QLineEdit(client["email"] if client else "")
        self.email_input.setPlaceholderText("email@example.com")
        
        self.phone_input = QLineEdit(client["phone"] if client else "")
        self.phone_input.setPlaceholderText("+91 XXXXX XXXXX")
        
        self.address_input = QLineEdit(client["address"] if client else "")
        self.address_input.setPlaceholderText("Full address")
        
        self.company_input = QLineEdit(client["company"] if client else "")
        self.company_input.setPlaceholderText("Company or organization")

        # Add fields to form
        form.addRow("Name *", self.name_input)
        form.addRow("Email", self.email_input)
        form.addRow("Phone", self.phone_input)
        form.addRow("Address", self.address_input)
        form.addRow("Company", self.company_input)
        
        layout.addLayout(form)

        # Helper text
        helper = QLabel("* Required field")
        helper.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: 11px;
            font-style: italic;
        """)
        layout.addWidget(helper)

        layout.addStretch()

        # Button box
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Save Client")
        buttons.button(QDialogButtonBox.Cancel).setText("Cancel")
        
        # Style buttons
        buttons.button(QDialogButtonBox.Ok).setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_PRIMARY};
                color: {Colors.TEXT_INVERSE};
                border: none;
                border-radius: 10px;
                padding: 10px 24px;
                font-weight: 700;
                font-size: 13px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_PRIMARY_HOVER};
            }}
        """)
        
        buttons.button(QDialogButtonBox.Cancel).setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: 10px;
                padding: 10px 24px;
                font-weight: 600;
                font-size: 13px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_HOVER};
                border: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)
        
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self) -> None:
        """Validate form before accepting."""
        # Validate name
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self,
                "Validation Error",
                "Client name is required. Please enter a name."
            )
            self.name_input.setFocus()
            return
        
        # Validate email format (if provided)
        email = self.email_input.text().strip()
        if email and "@" not in email:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please enter a valid email address with '@' symbol."
            )
            self.email_input.setFocus()
            return
        
        super().accept()

    def get_data(self) -> dict:
        """
        Return form data as dictionary.
        
        Returns:
            Dictionary with client data fields
        """
        return {
            "name": self.name_input.text().strip(),
            "email": self.email_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "address": self.address_input.text().strip(),
            "company": self.company_input.text().strip(),
        }
