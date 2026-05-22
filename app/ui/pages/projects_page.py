"""Projects management page — list, add, edit, status tracking with soft UI."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QDialog, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QDoubleSpinBox,
    QDialogButtonBox, QTextEdit, QMessageBox,
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor

from app.data.database import Database
from app.data.repositories.project_repo import ProjectRepository
from app.data.repositories.client_repo import ClientRepository
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedButton


class ProjectsPage(QWidget):
    """Project list with CRUD and status management — redesigned."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.repo = ProjectRepository(db)
        self.client_repo = ClientRepository(db)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        # Header
        header_row = QHBoxLayout()
        title = QLabel("Projects")
        title.setObjectName("heading")
        header_row.addWidget(title)

        self._count_label = QLabel("")
        self._count_label.setObjectName("subheading")
        header_row.addWidget(self._count_label)
        header_row.addStretch()

        add_btn = AnimatedButton("+ New Project", accent=Colors.ACCENT_PRIMARY)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_project)
        header_row.addWidget(add_btn)
        layout.addLayout(header_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Project", "Client", "Type", "Status", "Deadline"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.doubleClicked.connect(self._edit_project)
        layout.addWidget(self.table)

        # Actions
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        edit_btn = AnimatedButton("Edit", accent=Colors.ACCENT_INFO)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(self._edit_project)
        btn_row.addWidget(edit_btn)

        del_btn = AnimatedButton("Delete", accent=Colors.ACCENT_DANGER)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(self._delete_project)
        btn_row.addWidget(del_btn)
        layout.addLayout(btn_row)

        self.refresh()

    def refresh(self) -> None:
        projects = self.repo.get_all()
        self._count_label.setText(f"({len(projects)} total)")
        self.table.setRowCount(len(projects))
        for i, p in enumerate(projects):
            self.table.setItem(i, 0, QTableWidgetItem(str(p["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(p["name"]))
            self.table.setItem(i, 2, QTableWidgetItem(p["client_name"]))
            self.table.setItem(i, 3, QTableWidgetItem(p["type"] or "—"))

            # Color-coded status
            status_item = QTableWidgetItem(p["status"])
            status_colors = {
                "In Progress": Colors.ACCENT_INFO,
                "Completed": Colors.ACCENT_SUCCESS,
                "On Hold": Colors.ACCENT_WARNING,
                "Not Started": Colors.TEXT_MUTED,
                "Cancelled": Colors.ACCENT_DANGER,
            }
            color = status_colors.get(p["status"], Colors.TEXT_SECONDARY)
            status_item.setForeground(QColor(color))
            self.table.setItem(i, 4, status_item)

            self.table.setItem(i, 5, QTableWidgetItem(p["deadline"] or "—"))

    def _add_project(self) -> None:
        clients = self.client_repo.get_all()
        if not clients:
            QMessageBox.warning(self, "No Clients", "Add a client first before creating a project.")
            return
        dialog = ProjectDialog(self, clients=clients)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.repo.add(**data)
            self.refresh()

    def _edit_project(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        project_id = int(self.table.item(row, 0).text())
        project = self.repo.get_by_id(project_id)
        if not project:
            return
        clients = self.client_repo.get_all()
        dialog = ProjectDialog(self, clients=clients, project=project)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.repo.update(project_id, **data)
            self.refresh()

    def _delete_project(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        project_id = int(self.table.item(row, 0).text())
        reply = QMessageBox.question(self, "Delete", "Delete this project and all related data?")
        if reply == QMessageBox.Yes:
            self.repo.delete(project_id)
            self.refresh()


class ProjectDialog(QDialog):
    """Add/Edit project dialog — soft styled."""

    STATUSES = ["Not Started", "In Progress", "On Hold", "Completed", "Cancelled"]
    TYPES = ["Design", "Video", "Writing", "Music", "Development", "General"]

    def __init__(self, parent=None, clients=None, project=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Project" if project else "New Project")
        self.setMinimumWidth(460)

        layout = QFormLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)

        self.client_combo = QComboBox()
        for c in (clients or []):
            self.client_combo.addItem(c["name"], c["id"])
        if project:
            idx = self.client_combo.findData(project["client_id"])
            if idx >= 0:
                self.client_combo.setCurrentIndex(idx)

        self.name_input = QLineEdit(project["name"] if project else "")
        self.name_input.setPlaceholderText("Project name")
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.TYPES)
        if project and project["type"]:
            self.type_combo.setCurrentText(project["type"])

        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.desc_input.setPlaceholderText("Brief project description...")
        if project and project["description"]:
            self.desc_input.setPlainText(project["description"])

        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDate(QDate.currentDate().addDays(30))

        self.budget_input = QDoubleSpinBox()
        self.budget_input.setRange(0, 10_000_000)
        self.budget_input.setPrefix("₹ ")
        if project and project["budget"]:
            self.budget_input.setValue(project["budget"])

        self.status_combo = QComboBox()
        self.status_combo.addItems(self.STATUSES)
        if project:
            self.status_combo.setCurrentText(project["status"])

        layout.addRow("Client", self.client_combo)
        layout.addRow("Project Name *", self.name_input)
        layout.addRow("Type", self.type_combo)
        layout.addRow("Description", self.desc_input)
        layout.addRow("Deadline", self.deadline_input)
        layout.addRow("Budget", self.budget_input)
        if project:
            layout.addRow("Status", self.status_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_data(self) -> dict:
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

    def accept(self) -> None:
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Validation", "Project name is required.")
            self.name_input.setFocus()
            return
        super().accept()
