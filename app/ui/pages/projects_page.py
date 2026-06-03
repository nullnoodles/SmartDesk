"""
Projects Page — Modern project management with CRUD operations.

Features: Add/Edit/Delete projects, status tracking, stat cards overview,
and clean table interface following Studio Graphite design system.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.data.database import Database
from app.data.repositories.client_repo import ClientRepository
from app.data.repositories.project_repo import ProjectRepository
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedButton
from app.ui.widgets.page_header import PageHeader
from app.ui.widgets.stat_card import StatCard
from app.ui.widgets.status_pill import StatusPill


class ProjectsPage(QWidget):
    """
    Project management page with status tracking and CRUD operations.
    
    Layout Structure:
    ┌─────────────────────────────────────────────────────────────┐
    │ Page Header                        [+ New Project]          │
    │ ─────────────────────────────────────────────────────────── │
    │ [Active]  [Completed]  [On Hold]                           │
    │ ─────────────────────────────────────────────────────────── │
    │ Projects Table                                              │
    │ ─────────────────────────────────────────────────────────── │
    │                                    [Edit]  [Delete]         │
    └─────────────────────────────────────────────────────────────┘
    """

    STATUS_COLORS = {
        "In Progress": Colors.ACCENT_INFO,
        "Completed": Colors.ACCENT_SUCCESS,
        "On Hold": Colors.ACCENT_WARNING,
        "Not Started": Colors.TEXT_MUTED,
        "Cancelled": Colors.ACCENT_DANGER,
    }

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.repo = ProjectRepository(db)
        self.client_repo = ClientRepository(db)

        # Main page layout with scroll area
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create content widget
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        
        # Content layout - standardized spacing
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(36, 36, 36, 36)  # Standardized margins
        layout.setSpacing(28)  # Standardized spacing
        layout.setAlignment(Qt.AlignTop)

        # Build UI sections
        self._build_header(layout)
        self._build_stat_cards(layout)
        self._build_table(layout)
        self._build_action_buttons(layout)
        
        # Set up scroll area
        scroll.setWidget(content_widget)
        page_layout.addWidget(scroll)
        
        # Load initial data
        self.refresh()

    # ══════════════════════════════════════════════════════════════════
    # UI CONSTRUCTION METHODS
    # ══════════════════════════════════════════════════════════════════

    def _build_header(self, parent_layout: QVBoxLayout) -> None:
        """Build page header with title and add button."""
        self.header = PageHeader(
            title="Projects",
            subtitle="Manage and track your active production pipeline",
            count_text="0 total",
        )

        # Add project button
        add_btn = AnimatedButton("+ New Project", accent=Colors.ACCENT_PRIMARY)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(38)
        add_btn.clicked.connect(self._add_project)
        self.header.add_action(add_btn)
        
        parent_layout.addWidget(self.header)

    def _build_stat_cards(self, parent_layout: QVBoxLayout) -> None:
        """Build project status stat cards row."""
        stat_row = QHBoxLayout()
        stat_row.setSpacing(24)  # Standardized spacing

        # Active projects card
        self.card_active = StatCard(
            "Active",
            "0",
            icon="🚀",
            accent=Colors.ACCENT_INFO,
            sub_text="Currently in progress",
        )

        # Completed projects card
        self.card_completed = StatCard(
            "Completed",
            "0",
            icon="✅",
            accent=Colors.ACCENT_SUCCESS,
            sub_text="Delivered",
        )

        # On hold projects card
        self.card_on_hold = StatCard(
            "On Hold",
            "0",
            icon="⏸️",
            accent=Colors.ACCENT_WARNING,
            sub_text="Paused",
        )

        # Add all cards with equal stretch
        for card in (self.card_active, self.card_completed, self.card_on_hold):
            stat_row.addWidget(card, 1)
        
        parent_layout.addLayout(stat_row)

    def _build_table(self, parent_layout: QVBoxLayout) -> None:
        """Build the projects data table."""
        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID",
            "Project",
            "Client",
            "Type",
            "Status",
            "Deadline"
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
        self.table.doubleClicked.connect(self._edit_project)
        
        # Adjust column widths
        header = self.table.horizontalHeader()
        header.setDefaultSectionSize(150)
        self.table.setColumnWidth(0, 60)   # ID (narrow)
        self.table.setColumnWidth(1, 240)  # Project name (wider)
        self.table.setColumnWidth(2, 180)  # Client
        self.table.setColumnWidth(3, 140)  # Type
        
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
        edit_btn.clicked.connect(self._edit_project)
        btn_row.addWidget(edit_btn)

        # Delete button
        del_btn = AnimatedButton("🗑️  Delete", accent=Colors.ACCENT_DANGER)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setFixedHeight(38)
        del_btn.setMinimumWidth(100)
        del_btn.clicked.connect(self._delete_project)
        btn_row.addWidget(del_btn)
        
        parent_layout.addLayout(btn_row)

    # ══════════════════════════════════════════════════════════════════
    # DATA LOADING AND REFRESH
    # ══════════════════════════════════════════════════════════════════

    def refresh(self) -> None:
        """
        Refresh all project data from database.
        Updates stats and table with latest information.
        """
        try:
            projects = self.repo.get_all()
            counts = self.repo.count_all_statuses()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load projects: {e}")
            projects = []
            counts = {}
        
        # Update header count
        self.header.set_count(f"{len(projects)} total")
        
        # Update stat cards
        self.card_active.set_value(str(counts.get("In Progress", 0)))
        self.card_completed.set_value(str(counts.get("Completed", 0)))
        self.card_on_hold.set_value(str(counts.get("On Hold", 0)))

        # Populate table
        self._populate_table(projects)

    def _populate_table(self, projects: list) -> None:
        """
        Populate table with project data.
        
        Args:
            projects: List of project dictionaries from repository
        """
        # Empty state handling
        if not projects:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem(
                "No projects yet — click '+ New Project' to get started"
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
        self.table.setRowCount(len(projects))
        for i, p in enumerate(projects):
            # ID column
            id_item = QTableWidgetItem(str(p["id"]))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setForeground(QColor(Colors.TEXT_MUTED))
            self.table.setItem(i, 0, id_item)
            
            # Project name column (bold)
            name_item = QTableWidgetItem(p["name"])
            name_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            self.table.setItem(i, 1, name_item)
            
            # Client column
            client_item = QTableWidgetItem(p["client_name"])
            client_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 2, client_item)
            
            # Type column
            type_item = QTableWidgetItem(p["type"] or "—")
            type_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 3, type_item)

            # Status pill (custom widget)
            color = self.STATUS_COLORS.get(p["status"], Colors.TEXT_SECONDARY)
            pill = StatusPill(p["status"], color)
            self.table.setCellWidget(i, 4, pill)

            # Deadline column
            deadline_item = QTableWidgetItem(p["deadline"] or "—")
            deadline_item.setForeground(QColor(Colors.TEXT_MUTED))
            self.table.setItem(i, 5, deadline_item)

    # ══════════════════════════════════════════════════════════════════
    # CRUD OPERATIONS
    # ══════════════════════════════════════════════════════════════════

    def _add_project(self) -> None:
        """Open dialog to add a new project."""
        # Check if clients exist
        clients = self.client_repo.get_all()
        if not clients:
            QMessageBox.warning(
                self,
                "No Clients",
                "You need to add at least one client before creating a project.\n\n"
                "Go to the Clients page to add a client first."
            )
            return
        
        # Open add dialog
        dialog = ProjectDialog(self, clients=clients)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.repo.add(**data)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Project '{data['name']}' created successfully!"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create project: {e}")
                return
            self.refresh()

    def _edit_project(self) -> None:
        """Open dialog to edit selected project."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a project to edit."
            )
            return
        
        # Get project ID from first column
        item = self.table.item(row, 0)
        if item is None or not item.text().isdigit():
            return
        
        project_id = int(item.text())
        project = self.repo.get_by_id(project_id)
        
        if not project:
            QMessageBox.warning(self, "Error", "Project not found.")
            return
        
        # Get clients for dropdown
        clients = self.client_repo.get_all()
        
        # Open edit dialog
        dialog = ProjectDialog(self, clients=clients, project=project)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.repo.update(project_id, **data)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Project '{data['name']}' updated successfully!"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not update project: {e}")
                return
            self.refresh()

    def _delete_project(self) -> None:
        """Delete selected project after confirmation."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a project to delete."
            )
            return
        
        # Get project info
        item = self.table.item(row, 0)
        if item is None or not item.text().isdigit():
            return
        
        project_id = int(item.text())
        project_name = self.table.item(row, 1).text()
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete project '{project_name}'?\n\n"
            "This will also delete all related invoices and time logs.\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.repo.delete(project_id)
                QMessageBox.information(
                    self,
                    "Success",
                    f"Project '{project_name}' deleted successfully."
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete project: {e}")
                return
            self.refresh()


class ProjectDialog(QDialog):
    """
    Dialog for adding or editing a project.
    Clean form layout with all project fields.
    """

    STATUSES = ["Not Started", "In Progress", "On Hold", "Completed", "Cancelled"]
    TYPES = ["Design", "Video", "Writing", "Music", "Development", "General"]

    def __init__(self, parent=None, clients=None, project=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Project" if project else "New Project")
        self.setMinimumWidth(550)
        
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
        title = QLabel("Edit Project Details" if project else "Create New Project")
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

        # Client dropdown
        self.client_combo = QComboBox()
        for c in (clients or []):
            self.client_combo.addItem(c["name"], c["id"])
        if project:
            idx = self.client_combo.findData(project["client_id"])
            if idx >= 0:
                self.client_combo.setCurrentIndex(idx)

        # Project name
        self.name_input = QLineEdit(project["name"] if project else "")
        self.name_input.setPlaceholderText("Enter project name")

        # Project type
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.TYPES)
        if project and project["type"]:
            self.type_combo.setCurrentText(project["type"])

        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(90)
        self.desc_input.setPlaceholderText("Brief project description...")
        if project and project["description"]:
            self.desc_input.setPlainText(project["description"])

        # Deadline
        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDate(QDate.currentDate().addDays(30))
        if project and project["deadline"]:
            self.deadline_input.setDate(QDate.fromString(project["deadline"], "yyyy-MM-dd"))

        # Budget
        self.budget_input = QDoubleSpinBox()
        self.budget_input.setRange(0, 10_000_000)
        self.budget_input.setPrefix("₹ ")
        if project and project["budget"]:
            self.budget_input.setValue(project["budget"])

        # Status (only for edit mode)
        self.status_combo = QComboBox()
        self.status_combo.addItems(self.STATUSES)
        if project:
            self.status_combo.setCurrentText(project["status"])

        # Add fields to form
        form.addRow("Client *", self.client_combo)
        form.addRow("Project Name *", self.name_input)
        form.addRow("Type", self.type_combo)
        form.addRow("Description", self.desc_input)
        form.addRow("Deadline", self.deadline_input)
        form.addRow("Budget", self.budget_input)
        if project:
            form.addRow("Status", self.status_combo)
        
        layout.addLayout(form)

        # Helper text
        helper = QLabel("* Required fields")
        helper.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: 11px;
            font-style: italic;
        """)
        layout.addWidget(helper)

        layout.addStretch()

        # Button box
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Save Project")
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
                min-width: 120px;
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
                min-width: 120px;
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
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self,
                "Validation Error",
                "Project name is required. Please enter a name."
            )
            self.name_input.setFocus()
            return
        super().accept()

    def get_data(self) -> dict:
        """
        Return form data as dictionary.
        
        Returns:
            Dictionary with project data fields
        """
        data = {
            "client_id": self.client_combo.currentData(),
            "name": self.name_input.text().strip(),
            "project_type": self.type_combo.currentText(),
            "description": self.desc_input.toPlainText().strip(),
            "deadline": self.deadline_input.date().toString("yyyy-MM-dd"),
            "budget": self.budget_input.value(),
        }
        if self.status_combo.isVisible():
            data["status"] = self.status_combo.currentText()
        return data
