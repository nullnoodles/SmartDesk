"""Time tracking page — Studio Graphite redesign."""
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.time_tracker import TimeTracker
from app.data.database import Database
from app.data.repositories.project_repo import ProjectRepository
from app.data.repositories.time_log_repo import TimeLogRepository
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedButton, AnimatedCard
from app.ui.widgets.page_header import PageHeader
from app.ui.widgets.stat_card import StatCard


class TimePage(QWidget):
    """Time tracking with live timer, manual entry, and recent logs."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.time_repo = TimeLogRepository(db)
        self.tracker = TimeTracker(db)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # ─── Header ───────────────────────────────────────────────────────
        self.header = PageHeader(
            title="Time Tracking",
            subtitle="Run a timer or log hours manually for any project",
        )
        layout.addWidget(self.header)

        # ─── Stat row ─────────────────────────────────────────────────────
        self.card_today = StatCard("Today", "0.0 h", icon="🕐", accent=Colors.ACCENT_INFO)
        self.card_week = StatCard("This Week", "0.0 h", icon="📅", accent=Colors.ACCENT_PRIMARY_LIGHT)
        self.card_total = StatCard("Total Logged", "0.0 h", icon="🎯", accent=Colors.ACCENT_SUCCESS)

        stat_row = QHBoxLayout()
        stat_row.setSpacing(20)
        for c in (self.card_today, self.card_week, self.card_total):
            stat_row.addWidget(c, 1)
        layout.addLayout(stat_row)

        # ─── Timer card ───────────────────────────────────────────────────
        timer_card = AnimatedCard()
        timer_layout = QVBoxLayout(timer_card)
        timer_layout.setContentsMargins(28, 24, 28, 24)
        timer_layout.setSpacing(18)

        self.timer_label = QLabel("00:00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet(
            f"""
            font-size: 56px;
            font-weight: 700;
            color: {Colors.ACCENT_SUCCESS};
            background: transparent;
            letter-spacing: 4px;
            """
        )
        timer_layout.addWidget(self.timer_label)

        # Project + description row
        input_row = QHBoxLayout()
        input_row.setSpacing(12)

        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(220)
        input_row.addWidget(self.project_combo)

        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("What are you working on?")
        input_row.addWidget(self.desc_input, 1)
        timer_layout.addLayout(input_row)

        # Start/stop
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.start_btn = AnimatedButton("▶  Start Timer", accent=Colors.ACCENT_SUCCESS)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setFixedWidth(200)
        self.start_btn.clicked.connect(self._toggle_timer)
        btn_row.addWidget(self.start_btn)
        btn_row.addStretch()
        timer_layout.addLayout(btn_row)

        layout.addWidget(timer_card)

        # ─── Quick add manual entry ───────────────────────────────────────
        manual_card = AnimatedCard()
        manual_layout = QHBoxLayout(manual_card)
        manual_layout.setContentsMargins(20, 16, 20, 16)
        manual_layout.setSpacing(14)

        manual_label = QLabel("⏱️  Quick Add")
        manual_label.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 13px; font-weight: 700;"
        )
        manual_layout.addWidget(manual_label)

        self.manual_hours = QDoubleSpinBox()
        self.manual_hours.setRange(0.1, 24)
        self.manual_hours.setSingleStep(0.5)
        self.manual_hours.setValue(1.0)
        self.manual_hours.setSuffix(" hrs")
        manual_layout.addWidget(self.manual_hours)

        add_btn = AnimatedButton("+ Add Entry", accent=Colors.ACCENT_INFO)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self._add_manual)
        manual_layout.addWidget(add_btn)
        manual_layout.addStretch()

        layout.addWidget(manual_card)

        # ─── Logs table ──────────────────────────────────────────────────
        log_header = QLabel("Recent Time Logs")
        log_header.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 16px; font-weight: 700;"
        )
        layout.addWidget(log_header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Project", "Start", "End", "Hours", "Description"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

        # Timer ticker
        self._elapsed = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        self.refresh()

    # ------------------------------------------------------------------
    def refresh(self) -> None:
        # Reload projects
        try:
            self.project_combo.clear()
            for p in self.project_repo.get_all():
                self.project_combo.addItem(p["name"], p["id"])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load projects: {e}")

        # Reload logs
        try:
            logs = self.time_repo.get_recent(60)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load time logs: {e}")
            logs = []

        # Stat cards (today / this week / total)
        from datetime import date, timedelta

        today_str = date.today().isoformat()
        week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()

        today_total = sum(
            float(l["duration_hours"] or 0)
            for l in logs
            if (l["start_time"] or "").startswith(today_str)
        )
        week_total = sum(
            float(l["duration_hours"] or 0)
            for l in logs
            if (l["start_time"] or "")[:10] >= week_start
        )
        total = sum(float(l["duration_hours"] or 0) for l in logs)

        self.card_today.set_value(f"{today_total:.1f} h")
        self.card_week.set_value(f"{week_total:.1f} h")
        self.card_total.set_value(f"{total:.1f} h")

        if not logs:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("No time logs yet — start the timer or add a manual entry")
            empty_item.setFlags(Qt.ItemIsEnabled)
            empty_item.setForeground(QColor(Colors.TEXT_MUTED))
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 5)
            return

        self.table.clearSpans()
        self.table.setRowCount(len(logs))
        for i, log in enumerate(logs):
            self.table.setItem(i, 0, QTableWidgetItem(log["project_name"]))
            self.table.setItem(i, 1, QTableWidgetItem(log["start_time"][:16]))
            self.table.setItem(i, 2, QTableWidgetItem((log["end_time"] or "")[:16]))

            hours_item = QTableWidgetItem(f"{log['duration_hours']:.2f}")
            if log["duration_hours"] >= 4:
                hours_item.setForeground(QColor(Colors.ACCENT_SUCCESS))
            elif log["duration_hours"] >= 2:
                hours_item.setForeground(QColor(Colors.ACCENT_INFO))
            self.table.setItem(i, 3, hours_item)

            self.table.setItem(i, 4, QTableWidgetItem(log["description"] or "—"))

    def _toggle_timer(self) -> None:
        if self.tracker.is_running:
            try:
                hours = self.tracker.stop()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not stop timer: {e}")
                return
            self._timer.stop()
            self._elapsed = 0
            self.timer_label.setText("00:00:00")
            self.timer_label.setStyleSheet(
                f"font-size: 56px; font-weight: 700; color: {Colors.ACCENT_SUCCESS}; "
                f"background: transparent; letter-spacing: 4px;"
            )
            self.start_btn.setText("▶  Start Timer")
            self.refresh()
            QMessageBox.information(self, "Logged", f"Logged {hours:.2f} hours.")
        else:
            project_id = self.project_combo.currentData()
            if not project_id:
                QMessageBox.warning(self, "No Project", "Select a project first.")
                return
            try:
                self.tracker.start(project_id, self.desc_input.text())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not start timer: {e}")
                return
            self._elapsed = 0
            self._timer.start(1000)
            self.start_btn.setText("⏹  Stop Timer")
            self.timer_label.setStyleSheet(
                f"font-size: 56px; font-weight: 700; color: {Colors.ACCENT_DANGER}; "
                f"background: transparent; letter-spacing: 4px;"
            )

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
        if self.manual_hours.value() <= 0:
            QMessageBox.warning(self, "Validation", "Hours must be greater than 0.")
            return
        try:
            self.tracker.add_manual(project_id, self.manual_hours.value(), self.desc_input.text())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not add entry: {e}")
            return
        self.refresh()
