"""Time tracking page — start/stop timer, manual entry, log view — soft UI."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QDoubleSpinBox,
    QLineEdit, QMessageBox, QFrame,
)
from PySide6.QtCore import Qt, QTimer

from app.data.database import Database
from app.data.repositories.project_repo import ProjectRepository
from app.data.repositories.time_log_repo import TimeLogRepository
from app.core.time_tracker import TimeTracker
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedButton, AnimatedCard


class TimePage(QWidget):
    """Time tracking with live timer and manual entry — redesigned."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.time_repo = TimeLogRepository(db)
        self.tracker = TimeTracker(db)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(20)

        title = QLabel("Time Tracking")
        title.setObjectName("heading")
        layout.addWidget(title)

        # ─── Timer Card ───────────────────────────────────────────────────
        timer_card = AnimatedCard()
        timer_layout = QVBoxLayout(timer_card)
        timer_layout.setContentsMargins(24, 20, 24, 20)
        timer_layout.setSpacing(16)

        # Timer display
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet(f"""
            font-size: 48px;
            font-weight: 700;
            color: {Colors.ACCENT_SUCCESS};
            background: transparent;
            letter-spacing: 2px;
        """)
        timer_layout.addWidget(self.timer_label)

        # Project + description row
        input_row = QHBoxLayout()
        input_row.setSpacing(12)

        proj_label = QLabel("Project")
        proj_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 12px; background: transparent;")
        input_row.addWidget(proj_label)

        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(200)
        input_row.addWidget(self.project_combo)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("What are you working on?")
        input_row.addWidget(self.desc_input, stretch=1)
        timer_layout.addLayout(input_row)

        # Start/Stop button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.start_btn = AnimatedButton("▶  Start Timer", accent=Colors.ACCENT_SUCCESS)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setFixedWidth(180)
        self.start_btn.clicked.connect(self._toggle_timer)
        btn_row.addWidget(self.start_btn)
        btn_row.addStretch()
        timer_layout.addLayout(btn_row)

        layout.addWidget(timer_card)

        # ─── Manual Entry Row ─────────────────────────────────────────────
        manual_card = AnimatedCard()
        manual_layout = QHBoxLayout(manual_card)
        manual_layout.setContentsMargins(20, 16, 20, 16)
        manual_layout.setSpacing(12)

        manual_label = QLabel("⏱️  Quick Add")
        manual_label.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        manual_layout.addWidget(manual_label)

        self.manual_hours = QDoubleSpinBox()
        self.manual_hours.setRange(0.1, 24)
        self.manual_hours.setValue(1.0)
        self.manual_hours.setSuffix(" hrs")
        manual_layout.addWidget(self.manual_hours)

        add_btn = AnimatedButton("+ Add Entry", accent=Colors.ACCENT_INFO)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_manual)
        manual_layout.addWidget(add_btn)
        manual_layout.addStretch()

        layout.addWidget(manual_card)

        # ─── Log Table ────────────────────────────────────────────────────
        table_header = QLabel("Recent Time Logs")
        table_header.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(table_header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Project", "Start", "End", "Hours", "Description"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

        # Timer tick
        self._elapsed = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        self.refresh()

    def refresh(self) -> None:
        # Reload projects
        self.project_combo.clear()
        for p in self.project_repo.get_all():
            self.project_combo.addItem(p["name"], p["id"])

        # Reload logs
        logs = self.time_repo.get_recent(30)
        self.table.setRowCount(len(logs))
        for i, log in enumerate(logs):
            self.table.setItem(i, 0, QTableWidgetItem(log["project_name"]))
            self.table.setItem(i, 1, QTableWidgetItem(log["start_time"][:16]))
            self.table.setItem(i, 2, QTableWidgetItem((log["end_time"] or "")[:16]))

            # Color hours based on duration
            hours_item = QTableWidgetItem(f"{log['duration_hours']:.2f}")
            if log["duration_hours"] >= 4:
                hours_item.setForeground(QColor(Colors.ACCENT_SUCCESS))
            elif log["duration_hours"] >= 2:
                hours_item.setForeground(QColor(Colors.ACCENT_INFO))
            self.table.setItem(i, 3, hours_item)

            self.table.setItem(i, 4, QTableWidgetItem(log["description"] or "—"))

    def _toggle_timer(self) -> None:
        if self.tracker.is_running:
            hours = self.tracker.stop()
            self._timer.stop()
            self._elapsed = 0
            self.timer_label.setText("00:00:00")
            self.timer_label.setStyleSheet(f"""
                font-size: 48px; font-weight: 700;
                color: {Colors.ACCENT_SUCCESS};
                background: transparent; letter-spacing: 2px;
            """)
            self.start_btn.setText("▶  Start Timer")
            self.refresh()
            QMessageBox.information(self, "Logged", f"Logged {hours:.2f} hours.")
        else:
            project_id = self.project_combo.currentData()
            if not project_id:
                QMessageBox.warning(self, "No Project", "Select a project first.")
                return
            self.tracker.start(project_id, self.desc_input.text())
            self._elapsed = 0
            self._timer.start(1000)
            self.start_btn.setText("⏹  Stop Timer")
            self.timer_label.setStyleSheet(f"""
                font-size: 48px; font-weight: 700;
                color: {Colors.ACCENT_DANGER};
                background: transparent; letter-spacing: 2px;
            """)

    def _tick(self) -> None:
        self._elapsed += 1
        h = self._elapsed // 3600
        m = (self._elapsed % 3600) // 60
        s = self._elapsed % 60
        self.timer_label.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def _add_manual(self) -> None:
        project_id = self.project_combo.currentData()
        if not project_id:
            QMessageBox.warning(self, "No Project", "Select a project first.")
            return
        self.tracker.add_manual(project_id, self.manual_hours.value(), self.desc_input.text())
        self.refresh()
