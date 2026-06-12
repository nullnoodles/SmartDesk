"""Time log page — Studio Graphite redesign matching the Stitch design system.

Features:
- Page header (title and subtitle).
- 3 stat cards (Total Hours Logged, This Week, Entries) with hover shadow animations.
- Dynamic trend percentage calculation for "This Week" vs last week.
- Live Timer card (inline project select, transparent description input, timer on left, start/stop button on right).
- Manual Entry card (project select, hours input, description input, + Add Entry button).
- Hours by Project vertical bar chart for top 4 projects.
- Styled logs table (project, date, hours pill, description, edit/delete actions).
- Edit Dialog with project, start time, duration, and description fields.
"""
from __future__ import annotations

import datetime
from pathlib import Path
import sys

from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, Property, QDateTime
from PySide6.QtGui import QColor, QIcon, QPixmap, QPainter, QBrush, QFont, QPainterPath, QLinearGradient
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.config import ASSETS_DIR
from app.data.database import Database
from app.data.repositories.project_repo import ProjectRepository
from app.data.repositories.time_log_repo import TimeLogRepository
from app.core.time_tracker import TimeTracker
from app.ui.styles.theme import Colors
from app.ui.widgets.stat_card import StatCard
from app.ui.widgets.page_header import PageHeader
from app.core.signals import emit_data_changed
from app.ui.pages.dashboard_page import is_reduced_motion

_ICONS_DIR = ASSETS_DIR / "icons"


def _load_svg_icon(name: str, size: int = 16, color: str = "#bcc2ff") -> QPixmap:
    """Load an SVG icon, render at size, and tint it."""
    svg_path = _ICONS_DIR / f"{name}.svg"
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    if not svg_path.exists():
        return pixmap

    renderer = QSvgRenderer(str(svg_path))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return pixmap


class HoursPill(QWidget):
    """Pill-shaped tag showing hours with colored background."""

    def __init__(self, hours: float, parent=None):
        super().__init__(parent)
        
        # Color coding based on duration
        if hours >= 4.0:
            color = Colors.ACCENT_SUCCESS      # Mint
            bg_color = "rgba(125, 211, 168, 0.15)"
        elif hours >= 2.0:
            color = Colors.ACCENT_PRIMARY_LIGHT # Lavender-blue
            bg_color = "rgba(188, 194, 255, 0.15)"
        else:
            color = Colors.ACCENT_INFO         # Teal
            bg_color = "rgba(110, 197, 212, 0.15)"
            
        self.setStyleSheet(
            f"background-color: {bg_color}; border-radius: 999px;"
        )
        self.setFixedHeight(22)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 2, 10, 2)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        text = QLabel(f"{hours:.2f}h")
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet(
            f"background: transparent; color: {color}; "
            f"font-size: 11px; font-weight: 700; font-family: 'Inter';"
        )
        layout.addWidget(text)


class VerticalGradientBar(QWidget):
    """
    A vertical bar chart segment with gradient fill.
    Used for vertical bar chart visualization.
    """

    def __init__(
        self,
        value: float = 0.0,
        max_value: float = 100.0,
        color_start: str = Colors.ACCENT_PRIMARY,
        color_end: str = Colors.ACCENT_PRIMARY_LIGHT,
        width: int = 32,
        parent=None,
    ):
        super().__init__(parent)
        self._value = value
        self._max_value = max_value
        self._color_start = QColor(color_start)
        self._color_end = QColor(color_end)
        self.setFixedWidth(width)
        self.setMinimumHeight(40)

        # Animate value changes
        self._animated_value = 0.0
        self._value_anim = QPropertyAnimation(self, b"animatedValue")
        self._value_anim.setDuration(1000 if not is_reduced_motion() else 0)
        self._value_anim.setEasingCurve(QEasingCurve.OutCubic)

    def get_animated_value(self) -> float:
        return self._animated_value

    def set_animated_value(self, v: float) -> None:
        self._animated_value = v
        self.update()

    animatedValue = Property(float, get_animated_value, set_animated_value)

    def set_value(self, value: float, animate: bool = True) -> None:
        self._value = value
        if animate:
            self._value_anim.stop()
            self._value_anim.setStartValue(self._animated_value)
            self._value_anim.setEndValue(value)
            self._value_anim.start()
        else:
            self._animated_value = value
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background track
        bg_path = QPainterPath()
        bg_path.addRoundedRect(0, 0, self.width(), self.height(), 6, 6)
        painter.fillPath(bg_path, QColor(Colors.BG_ELEVATED))

        # Filled portion (bottom-anchored)
        if self._max_value > 0 and self._animated_value > 0:
            ratio = min(self._animated_value / self._max_value, 1.0)
            fill_height = self.height() * ratio
            y_start = self.height() - fill_height

            gradient = QLinearGradient(0, self.height(), 0, y_start)
            gradient.setColorAt(0, self._color_start)
            gradient.setColorAt(1, self._color_end)

            fill_path = QPainterPath()
            fill_path.addRoundedRect(0, y_start, self.width(), fill_height, 6, 6)
            painter.fillPath(fill_path, gradient)

        painter.end()


class TimeLogsTableWidget(QTableWidget):
    """QTableWidget subclass that dynamically sizes its height to fit its contents."""

    def sizeHint(self) -> QSize:
        sh = super().sizeHint()
        hh = self.horizontalHeader().height()
        if hh <= 0:
            hh = 38
        total_rows_height = 0
        for r in range(self.rowCount()):
            total_rows_height += self.rowHeight(r)
        sh.setHeight(hh + total_rows_height + 4)
        return sh

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()


class TimePage(QWidget):
    """Time tracking page rebuilt with Studio Graphite design tokens."""

    def __init__(self, db: Database):
        super().__init__()
        self.setObjectName("time_page")
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.time_repo = TimeLogRepository(db)
        self.tracker = TimeTracker(db)

        # Pagination state
        self.current_page = 0
        self.page_size = 10
        self.all_logs = []

        # Main page layout with scroll area
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)
        self.setStyleSheet("QWidget#time_page { background-color: #12131d; }")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { background-color: #12131d; border: none; }")

        content_widget = QWidget()
        content_widget.setObjectName("time_content")
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        content_widget.setStyleSheet("QWidget#time_content { background-color: #12131d; }")

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignTop)

        # 1. Header
        self.header = PageHeader(
            title="Time Log",
            subtitle="Run a timer or log hours manually for any project",
        )
        layout.addWidget(self.header)

        # 2. KPI Cards row
        self._build_stat_cards(layout)

        # 3. Middle Row: Live Timer & Manual Entry
        self._build_controls_row(layout)

        # 4. Chart Section
        self._build_chart(layout)

        # 5. Table Section
        self._build_table(layout)

        scroll.setWidget(content_widget)
        page_layout.addWidget(scroll)

        # Timer ticker
        self._elapsed = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)

        # Load initial data
        self.refresh()

    def _build_stat_cards(self, parent_layout: QVBoxLayout) -> None:
        stat_row = QHBoxLayout()
        stat_row.setContentsMargins(0, 0, 0, 0)
        stat_row.setSpacing(16)

        # Total Hours Card
        self.card_total = StatCard(
            "Total Hours Logged", "0.0h",
            icon="timer",
            accent=Colors.ACCENT_PRIMARY_LIGHT,
            sub_text="Lifetime tracking"
        )

        # This Week Card
        self.card_week = StatCard(
            "This Week", "0.0h",
            icon="schedule",
            accent=Colors.ACCENT_SUCCESS,
            sub_text="No previous data"
        )

        # Entries Card
        self.card_entries = StatCard(
            "Entries", "0",
            icon="description",
            accent=Colors.ACCENT_INFO,
            sub_text="Total logs recorded"
        )

        tints = {
            Colors.ACCENT_PRIMARY_LIGHT: "rgba(188, 194, 255, 0.10)",
            Colors.ACCENT_SUCCESS: "rgba(125, 211, 168, 0.10)",
            Colors.ACCENT_INFO: "rgba(110, 197, 212, 0.10)",
        }

        card_configs = [
            (self.card_total, Colors.ACCENT_PRIMARY_LIGHT, "timer"),
            (self.card_week, Colors.ACCENT_SUCCESS, "schedule"),
            (self.card_entries, Colors.ACCENT_INFO, "description"),
        ]

        for card, accent, icon_name in card_configs:
            card.setAttribute(Qt.WA_Hover, True)
            card.setMouseTracking(True)

            card_shadow = QGraphicsDropShadowEffect(card)
            card_shadow.setBlurRadius(0)
            card_shadow.setColor(QColor(124, 138, 244, 180))  # Purple glow
            card_shadow.setOffset(0, 0)
            card.setGraphicsEffect(card_shadow)

            shadow_animation = QPropertyAnimation(card_shadow, b"blurRadius")
            shadow_animation.setDuration(200 if not is_reduced_motion() else 0)
            shadow_animation.setEasingCurve(QEasingCurve.OutCubic)

            card._shadow = card_shadow
            card._shadow_animation = shadow_animation
            card.setObjectName("statCard")
            card._original_stylesheet = "QFrame#statCard { background-color: #1a1b26; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; }"
            card._hover_stylesheet = "QFrame#statCard { background-color: #383844; border: 1px solid rgba(255,255,255,0.12); border-radius: 12px; }"

            card.setMinimumHeight(140)
            card.setMaximumHeight(140)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            card.setStyleSheet(card._original_stylesheet)
            card.setContentsMargins(4, 4, 4, 4)

            card._icon_bubble.setAttribute(Qt.WA_TranslucentBackground, False)
            card._icon_bubble.setFixedSize(24, 24)
            card._icon_bubble.setScaledContents(False)

            rgba_color = tints.get(accent, "rgba(124, 138, 244, 0.10)")
            if icon_name and (_ICONS_DIR / f"{icon_name}.svg").exists():
                icon_pixmap = _load_svg_icon(icon_name, size=16, color=accent)
                card._icon_bubble.setPixmap(icon_pixmap)
            card._icon_bubble.setStyleSheet(f"background-color: {rgba_color}; border-radius: 4px; border: none; min-width: 24px; max-width: 24px; min-height: 24px; max-height: 24px;")

            layout = card.layout()
            if layout:
                layout.setAlignment(Qt.Alignment())
                layout.setContentsMargins(20, 16, 20, 16)
                layout.setSpacing(4)

            card.installEventFilter(self)
            stat_row.addWidget(card, 1)

        parent_layout.addLayout(stat_row)

    def _build_controls_row(self, parent_layout: QVBoxLayout) -> None:
        controls_row = QHBoxLayout()
        controls_row.setContentsMargins(0, 0, 0, 0)
        controls_row.setSpacing(24)

        # ─── Live Timer Card ──────────────────────────────────────────────
        timer_card = QFrame()
        timer_card.setObjectName("card")
        timer_card.setStyleSheet("QFrame#card { background-color: #1a1b26; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; }")
        timer_card_layout = QVBoxLayout(timer_card)
        timer_card_layout.setContentsMargins(24, 24, 24, 24)
        timer_card_layout.setSpacing(16)

        timer_header = QHBoxLayout()
        timer_title = QLabel("Live Timer")
        timer_title.setStyleSheet("color: #e2e1f1; font-size: 16px; font-weight: 500;")
        timer_header.addWidget(timer_title)
        timer_header.addStretch()
        
        self.timer_project_combo = QComboBox()
        self.timer_project_combo.setMinimumWidth(180)
        self.timer_project_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1b26;
                border: 1px solid #2d2e42;
                border-radius: 6px;
                padding: 4px 10px;
                color: #9a9cb8;
                font-size: 13px;
            }
            QComboBox:hover {
                border: 1px solid #7c8af4;
            }
        """)
        timer_header.addWidget(self.timer_project_combo)
        timer_card_layout.addLayout(timer_header)

        self.timer_desc_input = QLineEdit()
        self.timer_desc_input.setPlaceholderText("What are you working on?")
        self.timer_desc_input.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                padding: 0px;
                color: #e2e1f1;
                font-size: 16px;
                font-weight: 500;
            }
            QLineEdit:focus {
                border: none;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #6b6d85;
            }
        """)
        timer_card_layout.addWidget(self.timer_desc_input)
        timer_card_layout.addStretch()

        timer_bottom = QHBoxLayout()
        self.timer_lbl = QLabel("00:00:00")
        self.timer_lbl.setStyleSheet("""
            color: #7c8af4;
            font-size: 48px;
            font-weight: 700;
            font-family: 'Inter';
            letter-spacing: -0.02em;
        """)
        timer_bottom.addWidget(self.timer_lbl)
        timer_bottom.addStretch()

        self.timer_btn = QPushButton("Start")
        self.timer_btn.setCursor(Qt.PointingHandCursor)
        self.timer_btn.setFixedSize(120, 40)
        self._update_timer_button_style(False)
        self.timer_btn.clicked.connect(self._toggle_timer)
        timer_bottom.addWidget(self.timer_btn)
        timer_card_layout.addLayout(timer_bottom)

        controls_row.addWidget(timer_card, 1)

        # ─── Manual Entry Card ────────────────────────────────────────────
        manual_card = QFrame()
        manual_card.setObjectName("card")
        manual_card.setStyleSheet("QFrame#card { background-color: #1a1b26; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; }")
        manual_card_layout = QVBoxLayout(manual_card)
        manual_card_layout.setContentsMargins(24, 24, 24, 24)
        manual_card_layout.setSpacing(16)

        manual_header = QHBoxLayout()
        manual_title = QLabel("Manual Entry")
        manual_title.setStyleSheet("color: #e2e1f1; font-size: 16px; font-weight: 500;")
        manual_header.addWidget(manual_title)
        manual_header.addStretch()

        self.manual_project_combo = QComboBox()
        self.manual_project_combo.setMinimumWidth(180)
        self.manual_project_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1b26;
                border: 1px solid #2d2e42;
                border-radius: 6px;
                padding: 4px 10px;
                color: #9a9cb8;
                font-size: 13px;
            }
            QComboBox:hover {
                border: 1px solid #7c8af4;
            }
        """)
        manual_header.addWidget(self.manual_project_combo)
        manual_card_layout.addLayout(manual_header)

        inputs_row = QHBoxLayout()
        inputs_row.setSpacing(12)

        self.manual_hours_input = QDoubleSpinBox()
        self.manual_hours_input.setRange(0.1, 24.0)
        self.manual_hours_input.setSingleStep(0.5)
        self.manual_hours_input.setValue(1.0)
        self.manual_hours_input.setSuffix(" hrs")
        self.manual_hours_input.setFixedWidth(120)
        self.manual_hours_input.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #1a1b26;
                border: 1px solid #2d2e42;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e2e1f1;
                font-size: 14px;
            }
            QDoubleSpinBox:focus {
                border: 1px solid #7c8af4;
            }
        """)
        inputs_row.addWidget(self.manual_hours_input)

        self.manual_desc_input = QLineEdit()
        self.manual_desc_input.setPlaceholderText("Description")
        self.manual_desc_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1b26;
                border: 1px solid #2d2e42;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e2e1f1;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #7c8af4;
            }
            QLineEdit::placeholder {
                color: #6b6d85;
            }
        """)
        inputs_row.addWidget(self.manual_desc_input)
        manual_card_layout.addLayout(inputs_row)
        manual_card_layout.addStretch()

        self.manual_add_btn = QPushButton("+ Add Entry")
        self.manual_add_btn.setCursor(Qt.PointingHandCursor)
        self.manual_add_btn.setFixedHeight(40)
        self.manual_add_btn.setStyleSheet("""
            QPushButton {
                background-color: #7c8af4;
                color: #e2e4f0;
                border: none;
                border-radius: 8px;
                font-weight: 700;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #383844;
                color: #e2e4f0;
            }
            QPushButton:pressed {
                background-color: #252840;
            }
        """)
        self.manual_add_btn.clicked.connect(self._add_manual)
        manual_card_layout.addWidget(self.manual_add_btn)

        controls_row.addWidget(manual_card, 1)

        parent_layout.addLayout(controls_row)

    def _update_timer_button_style(self, running: bool) -> None:
        if running:
            self.timer_btn.setText("Stop")
            self.timer_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e87c8a;
                    color: #12131d;
                    border: none;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background-color: #383844;
                    color: #e2e4f0;
                }
                QPushButton:pressed {
                    background-color: #252840;
                }
            """)
            self.timer_lbl.setStyleSheet("""
                color: #e87c8a;
                font-size: 48px;
                font-weight: 700;
                font-family: 'Inter';
                letter-spacing: -0.02em;
            """)
        else:
            self.timer_btn.setText("Start")
            self.timer_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7dd3a8;
                    color: #12131d;
                    border: none;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background-color: #383844;
                    color: #e2e4f0;
                }
                QPushButton:pressed {
                    background-color: #252840;
                }
            """)
            self.timer_lbl.setStyleSheet("""
                color: #7c8af4;
                font-size: 48px;
                font-weight: 700;
                font-family: 'Inter';
                letter-spacing: -0.02em;
            """)

    def _build_chart(self, parent_layout: QVBoxLayout) -> None:
        self.chart_card = QFrame()
        self.chart_card.setObjectName("card")
        self.chart_card.setStyleSheet("QFrame#card { background-color: #1a1b26; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; }")
        self.chart_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        chart_layout = QVBoxLayout(self.chart_card)
        chart_layout.setContentsMargins(24, 24, 24, 24)
        chart_layout.setSpacing(16)

        title = QLabel("Hours by Project")
        title.setStyleSheet("color: #e2e4f0; font-size: 16px; font-weight: 500;")
        chart_layout.addWidget(title)

        # Container for vertical bars
        self.chart_bars_container = QWidget()
        self.chart_bars_container.setObjectName("chart_bars_container")
        self.chart_bars_layout = QHBoxLayout(self.chart_bars_container)
        self.chart_bars_layout.setContentsMargins(16, 0, 16, 0)
        self.chart_bars_layout.setSpacing(24)
        self.chart_bars_layout.setAlignment(Qt.AlignBottom)

        chart_layout.addWidget(self.chart_bars_container)
        parent_layout.addWidget(self.chart_card)

    def _build_table(self, parent_layout: QVBoxLayout) -> None:
        self.table_card = QFrame()
        self.table_card.setObjectName("card")
        self.table_card.setStyleSheet("QFrame#card { background-color: #1a1b26; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; }")
        self.table_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        table_layout = QVBoxLayout(self.table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # Card header
        header_widget = QWidget()
        header_widget.setStyleSheet("background: transparent; border: none;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(24, 16, 24, 16)
        header_title = QLabel("Time Entries")
        header_title.setStyleSheet("color: #e2e1f1; font-size: 16px; font-weight: 500;")
        header_layout.addWidget(header_title)
        header_layout.addStretch()

        self.table_count_lbl = QLabel("0 Total Records")
        self.table_count_lbl.setStyleSheet("color: #6b6d85; font-size: 13px; font-weight: 500;")
        header_layout.addWidget(self.table_count_lbl)
        table_layout.addWidget(header_widget)

        # Table widget
        self.table = TimeLogsTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "PROJECT", "DATE", "HOURS", "DESCRIPTION", "ACTIONS"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setFrameShape(QFrame.NoFrame)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1b26;
                border: none;
                color: #e2e1f1;
                font-size: 14px;
                outline: none;
            }
            QTableWidget::item {
                border: none;
                padding: 10px 20px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            }
            QTableWidget::item:selected {
                background-color: rgba(124, 138, 244, 0.10);
                border: none;
                color: #e2e1f1;
            }
            QTableWidget::item:hover {
                background-color: rgba(124, 138, 244, 0.06);
                border: none;
            }
            QHeaderView::section {
                background-color: #1a1b26;
                color: #9a9cb8;
                padding: 10px 20px;
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.06);
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }
        """)

        # Column sizing
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        for col in range(5):
            header.setSectionResizeMode(col, QHeaderView.Fixed)

        self.table.setColumnWidth(1, 140)  # DATE
        self.table.setColumnWidth(2, 100)  # HOURS
        self.table.setColumnWidth(4, 90)   # ACTIONS

        header.setSectionResizeMode(0, QHeaderView.Stretch)  # PROJECT
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # DESCRIPTION

        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        table_layout.addWidget(self.table)

        # ─── Pagination Footer (matching clients_page) ──────────────────────
        self.footer_widget = QWidget()
        self.footer_widget.setObjectName("table_footer")
        self.footer_widget.setStyleSheet("""
            QWidget#table_footer {
                background-color: transparent;
                border-top: 1px solid #2d2e42;
            }
        """)
        footer_layout = QHBoxLayout(self.footer_widget)
        footer_layout.setContentsMargins(24, 16, 24, 16)
        footer_layout.setSpacing(16)

        # Left: info text
        self.info_label = QLabel()
        self.info_label.setObjectName("table_footer_info")
        self.info_label.setStyleSheet("color: #9a9cb8; font-size: 13px; font-weight: 400; background: transparent; border: none;")
        footer_layout.addWidget(self.info_label, 0, Qt.AlignLeft | Qt.AlignVCenter)

        # Center spacer
        footer_layout.addStretch()

        # Center pagination controls
        self.controls_widget = QWidget()
        self.controls_widget.setStyleSheet("background: transparent; border: none;")
        self.controls_layout = QHBoxLayout(self.controls_widget)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_layout.setSpacing(6)

        # Previous button
        self.prev_btn = QPushButton()
        self.prev_btn.setObjectName("prev_page_btn")
        self.prev_btn.setCursor(Qt.PointingHandCursor)
        self.prev_btn.setFixedSize(32, 32)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #2d2e42;
                border-radius: 6px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: rgba(124, 138, 244, 0.05);
                border: 1px solid #454652;
            }
            QPushButton:disabled {
                background-color: transparent;
                border: 1px solid #1e1f2a;
            }
        """)
        prev_icon = _load_svg_icon("chevron_left", size=16, color="#e2e4f0")
        self.prev_btn.setIcon(QIcon(prev_icon))
        self.prev_btn.setIconSize(QSize(16, 16))
        self.prev_btn.clicked.connect(self._prev_page)
        self.controls_layout.addWidget(self.prev_btn)

        # Dynamic Page buttons layout
        self.page_buttons_widget = QWidget()
        self.page_buttons_widget.setStyleSheet("background: transparent; border: none;")
        self.page_buttons_layout = QHBoxLayout(self.page_buttons_widget)
        self.page_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.page_buttons_layout.setSpacing(6)
        self.controls_layout.addWidget(self.page_buttons_widget)

        # Next button
        self.next_btn = QPushButton()
        self.next_btn.setObjectName("next_page_btn")
        self.next_btn.setCursor(Qt.PointingHandCursor)
        self.next_btn.setFixedSize(32, 32)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #2d2e42;
                border-radius: 6px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: rgba(124, 138, 244, 0.05);
                border: 1px solid #454652;
            }
            QPushButton:disabled {
                background-color: transparent;
                border: 1px solid #1e1f2a;
            }
        """)
        next_icon = _load_svg_icon("chevron_right", size=16, color="#e2e4f0")
        self.next_btn.setIcon(QIcon(next_icon))
        self.next_btn.setIconSize(QSize(16, 16))
        self.next_btn.clicked.connect(self._next_page)
        self.controls_layout.addWidget(self.next_btn)

        footer_layout.addWidget(self.controls_widget, 0, Qt.AlignCenter | Qt.AlignVCenter)

        # Right spacer
        footer_layout.addStretch()

        # Right: Page size dropdown
        self.page_size_combo = QComboBox()
        self.page_size_combo.setObjectName("page_size_combo")
        self.page_size_combo.addItems(["10 per page"])
        self.page_size_combo.setCurrentText("10 per page")
        self.page_size_combo.setFixedWidth(120)
        self.page_size_combo.setStyleSheet("""
            QComboBox {
                background-color: #1e1f2a;
                border: 1px solid #2d2e42;
                border-radius: 6px;
                padding: 4px 10px;
                color: #9a9cb8;
                font-size: 13px;
            }
            QComboBox:hover {
                border: 1px solid #7c8af4;
            }
        """)
        footer_layout.addWidget(self.page_size_combo, 0, Qt.AlignRight | Qt.AlignVCenter)

        table_layout.addWidget(self.footer_widget)
        parent_layout.addWidget(self.table_card)

    def eventFilter(self, obj, event):
        """Handle hover events for stat cards to trigger shadow animation."""
        from PySide6.QtCore import QEvent
        if obj in (self.card_total, self.card_week, self.card_entries):
            if hasattr(obj, '_shadow') and hasattr(obj, '_shadow_animation'):
                event_type = event.type()
                if event_type == QEvent.Enter:
                    obj._shadow_animation.stop()
                    obj._shadow_animation.setStartValue(obj._shadow.blurRadius())
                    obj._shadow_animation.setEndValue(20 if not is_reduced_motion() else 0)
                    obj._shadow_animation.start()
                    if hasattr(obj, '_hover_stylesheet'):
                        obj.setStyleSheet(obj._hover_stylesheet)
                elif event_type == QEvent.Leave:
                    obj._shadow_animation.stop()
                    obj._shadow_animation.setStartValue(obj._shadow.blurRadius())
                    obj._shadow_animation.setEndValue(0)
                    obj._shadow_animation.start()
                    if hasattr(obj, '_original_stylesheet'):
                        obj.setStyleSheet(obj._original_stylesheet)
        return super().eventFilter(obj, event)

    def refresh(self) -> None:
        # 1. Reload Projects Combos
        try:
            self.timer_project_combo.clear()
            self.manual_project_combo.clear()
            for p in self.project_repo.get_all():
                self.timer_project_combo.addItem(p["name"], p["id"])
                self.manual_project_combo.addItem(p["name"], p["id"])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load projects: {e}")

        # 2. Query logs
        try:
            logs = self.time_repo.get_recent(100)
            logs = [dict(l) for l in logs]
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load logs: {e}")
            logs = []

        # 3. Dynamic Stats Calculations
        # Total Hours
        total_hours = sum(float(l["duration_hours"] or 0) for l in logs)
        self.card_total.set_value(f"{total_hours:.1f}h")

        # Week Hours & Trend
        from datetime import date, timedelta
        today = date.today()
        this_week_start = today - timedelta(days=today.weekday())  # Monday
        last_week_start = this_week_start - timedelta(days=7)

        this_week_total = 0.0
        last_week_total = 0.0

        for l in logs:
            if l["start_time"]:
                try:
                    log_date = date.fromisoformat(l["start_time"][:10])
                    if log_date >= this_week_start:
                        this_week_total += float(l["duration_hours"] or 0)
                    elif last_week_start <= log_date < this_week_start:
                        last_week_total += float(l["duration_hours"] or 0)
                except Exception:
                    pass

        self.card_week.set_value(f"{this_week_total:.1f}h")

        if last_week_total > 0:
            diff_pct = ((this_week_total - last_week_total) / last_week_total) * 100
            if diff_pct >= 0:
                trend_text = f'<span style="color: #82d8ac;">▲ {diff_pct:.0f}% vs last week</span>'
            else:
                trend_text = f'<span style="color: #e87c8a;">▼ {abs(diff_pct):.0f}% vs last week</span>'
        else:
            trend_text = "No previous data"
        self.card_week.set_sub_text(trend_text)

        # Entries Count
        self.card_entries.set_value(str(len(logs)))
        self.card_entries.set_sub_text("Total logs recorded")

        # 4. Populate Chart
        self._populate_chart()

        # 5. Populate Table
        self.all_logs = logs
        # Clamp current page to valid range
        total_items = len(self.all_logs)
        total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)
        if self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)
        self._populate_table_current_page()

    def _populate_chart(self) -> None:
        # Clear existing bars
        while self.chart_bars_layout.count():
            item = self.chart_bars_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Query Top 4 projects by duration hours
        query = """
            SELECT p.id, p.name, COALESCE(SUM(t.duration_hours), 0) as total_hours
            FROM projects p
            JOIN time_logs t ON t.project_id = p.id
            GROUP BY p.id
            ORDER BY total_hours DESC
            LIMIT 4
        """
        try:
            rows = [dict(r) for r in self.db.execute(query)]
        except Exception:
            rows = []

        # Fallback mockup data if empty
        if not rows or sum(r["total_hours"] for r in rows) == 0:
            rows = [
                {"name": "Neon Branding", "total_hours": 12.5},
                {"name": "Skyline App UI", "total_hours": 8.0},
                {"name": "Logo Design", "total_hours": 6.2},
                {"name": "Internal", "total_hours": 4.5},
            ]

        max_hours = max(float(r["total_hours"]) for r in rows) if rows else 1.0

        color_pairs = [
            ("#7c8af4", "#bcc2ff"),  # Lavender
            ("#3a8e9e", "#7dd3e3"),  # Teal
            ("#56b582", "#82d8ac"),  # Mint
            ("#d66874", "#e87c8a"),  # Rose
        ]

        for idx, row in enumerate(rows):
            col_widget = QWidget()
            col_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            col_layout = QVBoxLayout(col_widget)
            col_layout.setContentsMargins(0, 0, 0, 0)
            col_layout.setSpacing(8)
            col_layout.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)

            # Hours Label
            hours_val = float(row["total_hours"])
            hours_lbl = QLabel(f"{hours_val:.1f}h")
            hours_lbl.setAlignment(Qt.AlignCenter)
            hours_lbl.setStyleSheet("color: #e2e4f0; font-size: 12px; font-weight: 600; font-family: 'Inter'; background: transparent; border: none;")
            col_layout.addWidget(hours_lbl)

            # Vertical Bar widget
            color_start, color_end = color_pairs[idx % len(color_pairs)]
            bar = VerticalGradientBar(
                value=0.0,
                max_value=100.0,
                color_start=color_start,
                color_end=color_end,
                width=32,
                parent=self
            )
            bar.setFixedHeight(120)
            col_layout.addWidget(bar, 0, Qt.AlignHCenter)

            # Project Title Label
            proj_name = row["name"]
            name_lbl = QLabel(proj_name)
            name_lbl.setAlignment(Qt.AlignCenter)
            name_lbl.setStyleSheet("""
                QLabel {
                    color: #6b6d85;
                    font-size: 10px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.05em;
                    background: transparent;
                    border: none;
                }
            """)
            col_layout.addWidget(name_lbl)

            self.chart_bars_layout.addWidget(col_widget)

            # Animate the bar
            pct = int((hours_val / max_hours) * 100) if max_hours > 0 else 0
            bar.set_value(pct, animate=True)

    def _populate_table(self, logs: list) -> None:
        self.table.clearSpans()
        self.table_count_lbl.setText(f"{len(self.all_logs)} Total Records")

        if not logs:
            self.table.setRowCount(1)
            self.table.setRowHeight(0, 100)
            self.table.setSpan(0, 0, 1, 5)
            empty_item = QLabel("No time logs yet — start the timer or add a manual entry")
            empty_item.setAlignment(Qt.AlignCenter)
            empty_item.setStyleSheet("color: #6b6d85; font-size: 14px; background: transparent; border: none;")
            self.table.setCellWidget(0, 0, empty_item)
            return

        self.table.setRowCount(len(logs))
        for i, log in enumerate(logs):
            # 0. Project Name
            proj_item = QTableWidgetItem(log.get("project_name") or "No Project")
            proj_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            font = proj_item.font()
            font.setWeight(QFont.DemiBold)
            proj_item.setFont(font)
            proj_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 0, proj_item)

            # 1. Date
            start_time = log.get("start_time") or ""
            formatted_date = "—"
            if start_time:
                try:
                    dt = datetime.datetime.fromisoformat(start_time)
                    formatted_date = dt.strftime("%b %d, %Y")
                except Exception:
                    formatted_date = start_time[:10]
            date_item = QTableWidgetItem(formatted_date)
            date_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            date_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 1, date_item)

            # 2. Hours Pill
            duration = float(log.get("duration_hours") or 0.0)
            self.table.setCellWidget(i, 2, HoursPill(duration))

            # 3. Description
            desc = log.get("description") or "—"
            desc_item = QTableWidgetItem(desc)
            desc_item.setForeground(QColor(Colors.TEXT_MUTED))
            desc_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 3, desc_item)

            # 4. Actions
            self.table.setCellWidget(i, 4, self._create_actions_cell(log["id"]))

        self.table.updateGeometry()

    def _populate_table_current_page(self) -> None:
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_logs = self.all_logs[start_idx:end_idx]
        
        self._populate_table(page_logs)
        self._update_pagination_ui()

    def _update_pagination_ui(self) -> None:
        total_items = len(self.all_logs)
        total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)
        
        if self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)
            
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, total_items)
        
        if total_items == 0:
            self.info_label.setText("Showing 0 to 0 of 0 entries")
        else:
            self.info_label.setText(f"Showing {start_idx + 1} to {end_idx} of {total_items} entries")
            
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)
        
        prev_color = "#e2e4f0" if self.current_page > 0 else "#454652"
        next_color = "#e2e4f0" if self.current_page < total_pages - 1 else "#454652"
        self.prev_btn.setIcon(QIcon(_load_svg_icon("chevron_left", size=16, color=prev_color)))
        self.next_btn.setIcon(QIcon(_load_svg_icon("chevron_right", size=16, color=next_color)))
        
        while self.page_buttons_layout.count():
            item = self.page_buttons_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for page in range(total_pages):
            btn = QPushButton(str(page + 1))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedSize(32, 32)
            
            if page == self.current_page:
                btn.setProperty("active", True)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #7c8af4;
                        color: #0f208b;
                        border: none;
                        border-radius: 6px;
                        font-weight: 700;
                        font-size: 13px;
                    }
                """)
            else:
                btn.setProperty("active", False)
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: 1px solid #2d2e42;
                        border-radius: 6px;
                        color: #9a9cb8;
                        font-weight: 600;
                        font-size: 13px;
                    }
                    QPushButton:hover {
                        background-color: rgba(124, 138, 244, 0.05);
                        border: 1px solid #454652;
                        color: #e2e4f0;
                    }
                """)
            btn.clicked.connect(lambda _, p=page: self._go_to_page(p))
            self.page_buttons_layout.addWidget(btn)

    def _go_to_page(self, page_index: int) -> None:
        self.current_page = page_index
        self._populate_table_current_page()

    def _prev_page(self) -> None:
        if self.current_page > 0:
            self._go_to_page(self.current_page - 1)

    def _next_page(self) -> None:
        total_items = len(self.all_logs)
        total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages - 1:
            self._go_to_page(self.current_page + 1)

    def _create_actions_cell(self, log_id: int) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        edit_btn = QPushButton()
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setToolTip("Edit Log")
        edit_btn.setIcon(QIcon(_load_svg_icon("edit", size=16, color="#7c8af4")))
        edit_btn.setIconSize(QSize(16, 16))
        edit_btn.setFixedSize(32, 32)
        edit_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: rgba(124, 138, 244, 0.15);
            }
            QPushButton:pressed {
                background: rgba(124, 138, 244, 0.25);
            }
        """)
        edit_btn.clicked.connect(lambda: self._edit_log_by_id(log_id))

        del_btn = QPushButton()
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Delete Log")
        del_btn.setIcon(QIcon(_load_svg_icon("delete", size=16, color="#e87c8a")))
        del_btn.setIconSize(QSize(16, 16))
        del_btn.setFixedSize(32, 32)
        del_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: rgba(232, 124, 138, 0.20);
            }
            QPushButton:pressed {
                background: rgba(232, 124, 138, 0.30);
            }
        """)
        del_btn.clicked.connect(lambda: self._delete_log_by_id(log_id))

        layout.addWidget(edit_btn)
        layout.addWidget(del_btn)
        layout.addStretch()
        return container

    def _toggle_timer(self) -> None:
        if self.tracker.is_running:
            try:
                hours = self.tracker.stop()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not stop timer: {e}")
                return
            self._timer.stop()
            self._elapsed = 0
            self.timer_lbl.setText("00:00:00")
            self._update_timer_button_style(False)
            self.refresh()
            emit_data_changed()
            QMessageBox.information(self, "Logged", f"Logged {hours:.2f} hours successfully.")
        else:
            project_id = self.timer_project_combo.currentData()
            if not project_id:
                QMessageBox.warning(self, "No Project", "Select a project first.")
                return
            try:
                self.tracker.start(project_id, self.timer_desc_input.text())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not start timer: {e}")
                return
            self._elapsed = 0
            self._timer.start(1000)
            self._update_timer_button_style(True)

    def _tick(self) -> None:
        self._elapsed += 1
        h = self._elapsed // 3600
        m = (self._elapsed % 3600) // 60
        s = self._elapsed % 60
        self.timer_lbl.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def _add_manual(self) -> None:
        project_id = self.manual_project_combo.currentData()
        if not project_id:
            QMessageBox.warning(self, "No Project", "Select a project first.")
            return
        hours = self.manual_hours_input.value()
        if hours <= 0:
            QMessageBox.warning(self, "Validation", "Hours must be greater than 0.")
            return
        try:
            self.tracker.add_manual(project_id, hours, self.manual_desc_input.text())
            emit_data_changed()
            self.refresh()
            # Clear input fields
            self.manual_hours_input.setValue(1.0)
            self.manual_desc_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not add entry: {e}")

    def _edit_log_by_id(self, log_id: int) -> None:
        rows = self.db.execute("SELECT * FROM time_logs WHERE id = ?", (log_id,))
        if not rows:
            QMessageBox.warning(self, "Error", "Time log not found.")
            return
        log = dict(rows[0])

        dialog = TimeLogDialog(self, log=log)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.db.execute(
                    """UPDATE time_logs 
                       SET project_id = ?, start_time = ?, end_time = ?, duration_hours = ?, description = ? 
                       WHERE id = ?""",
                    (data["project_id"], data["start_time"], data["end_time"], data["duration_hours"], data["description"], log_id),
                )
                emit_data_changed()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not update time log: {e}")

    def _delete_log_by_id(self, log_id: int) -> None:
        rows = self.db.execute(
            """SELECT t.*, p.name as project_name 
               FROM time_logs t 
               JOIN projects p ON t.project_id = p.id 
               WHERE t.id = ?""",
            (log_id,),
        )
        if not rows:
            return
        log = rows[0]

        dialog = DeleteConfirmDialog(log["project_name"], float(log["duration_hours"]), self)
        if dialog.exec() == QDialog.Accepted:
            try:
                self.db.execute("DELETE FROM time_logs WHERE id = ?", (log_id,))
                emit_data_changed()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete time log: {e}")


class TimeLogDialog(QDialog):
    """Dialog for creating or editing a time log entry."""

    def __init__(self, parent: TimePage, log: dict | None = None):
        super().__init__(parent)
        self.parent_page = parent
        self.log = log
        self.db = parent.db
        self.project_repo = parent.project_repo

        self.setWindowTitle("Edit Time Entry" if log else "Log Time")
        self.setMinimumWidth(450)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {Colors.BG_DARK};
            }}
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: 13px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
            QLineEdit, QComboBox, QDateTimeEdit, QDoubleSpinBox {{
                background-color: {Colors.BG_ELEVATED};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 8px;
                padding: 8px 12px;
                color: {Colors.TEXT_PRIMARY};
                font-family: 'Inter';
                font-size: 14px;
            }}
            QLineEdit:focus, QComboBox:focus, QDateTimeEdit:focus, QDoubleSpinBox:focus {{
                border: 1px solid {Colors.ACCENT_PRIMARY_LIGHT};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(24)

        # Title
        title_text = "Edit Time Entry Details" if log else "Add Time Log"
        title = QLabel(title_text)
        title.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.01em;
        """)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Project dropdown
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(250)
        try:
            for p in self.project_repo.get_all():
                self.project_combo.addItem(p["name"], p["id"])
        except Exception:
            pass

        if log:
            idx = self.project_combo.findData(log["project_id"])
            if idx >= 0:
                self.project_combo.setCurrentIndex(idx)
        form.addRow("Project *", self.project_combo)

        # Start Date/Time
        self.start_dt_input = QDateTimeEdit()
        self.start_dt_input.setCalendarPopup(True)
        if log and log["start_time"]:
            try:
                dt = datetime.datetime.fromisoformat(log["start_time"])
                self.start_dt_input.setDateTime(QDateTime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second))
            except Exception:
                self.start_dt_input.setDateTime(QDateTime.currentDateTime())
        else:
            self.start_dt_input.setDateTime(QDateTime.currentDateTime())
        form.addRow("Start Time *", self.start_dt_input)

        # Hours
        self.hours_input = QDoubleSpinBox()
        self.hours_input.setRange(0.1, 24.0)
        self.hours_input.setSingleStep(0.5)
        self.hours_input.setSuffix(" hrs")
        if log:
            self.hours_input.setValue(log["duration_hours"])
        else:
            self.hours_input.setValue(1.0)
        form.addRow("Hours *", self.hours_input)

        # Description
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Describe the work done...")
        if log and log["description"]:
            self.desc_input.setText(log["description"])
        form.addRow("Description", self.desc_input)

        layout.addLayout(form)

        # Helper
        helper = QLabel("* Required field")
        helper.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px; font-style: italic;")
        layout.addWidget(helper)

        # Actions
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Save Entry")
        buttons.button(QDialogButtonBox.Cancel).setText("Cancel")

        buttons.button(QDialogButtonBox.Ok).setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_PRIMARY};
                color: {Colors.TEXT_INVERSE};
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 700;
                font-size: 13px;
                min-width: 100px;
                min-height: 36px;
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
                border-radius: 8px;
                padding: 8px 20px;
                font-weight: 600;
                font-size: 13px;
                min-width: 100px;
                min-height: 36px;
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_HOVER};
                border: 1px solid {Colors.BORDER_DEFAULT};
            }}
        """)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self) -> dict:
        start_dt = self.start_dt_input.dateTime().toPython()
        duration = self.hours_input.value()
        end_dt = start_dt + datetime.timedelta(hours=duration)
        return {
            "project_id": self.project_combo.currentData(),
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "duration_hours": duration,
            "description": self.desc_input.text(),
        }


class DeleteConfirmDialog(QDialog):
    """Dialog for confirming time log deletion, styled with custom colors and layout."""

    def __init__(self, project_name: str, duration: float, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm Delete")
        self.setFixedSize(500, 180)
        self.setObjectName("delete_confirm_dialog")

        self.setStyleSheet("""
            QDialog#delete_confirm_dialog {
                background-color: #252840;
                border: none;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)
        
        title = QLabel("Confirm Delete")
        title.setFont(QFont("Inter", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        layout.addWidget(title)
        
        layout.addSpacing(8)
        
        question_label = QLabel(f"Are you sure you want to delete the time log of {duration:.2f}h for project '{project_name}'?")
        question_label.setWordWrap(True)
        question_label.setFont(QFont("Segoe UI", 12))
        question_label.setStyleSheet("color: #8B8FA8; background: transparent; border: none;")
        layout.addWidget(question_label)
        
        layout.addSpacing(4)
        
        warning_label = QLabel("This action cannot be undone.")
        warning_label.setFont(QFont("Segoe UI", 9))
        warning_label.setStyleSheet("color: #6B7280; background: transparent; border: none;")
        layout.addWidget(warning_label)
        
        layout.addStretch()
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.setSpacing(8)
        btn_row.setContentsMargins(0, 0, 0, 0)
        
        self.no_btn = QPushButton("No, Cancel")
        self.no_btn.setCursor(Qt.PointingHandCursor)
        self.no_btn.setFixedSize(120, 36)
        self.no_btn.setStyleSheet("""
            QPushButton {
                background-color: #2D2F45;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 600;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #3d405c;
            }
        """)
        self.no_btn.clicked.connect(self.reject)
        
        self.yes_btn = QPushButton("Yes, Delete")
        self.yes_btn.setCursor(Qt.PointingHandCursor)
        self.yes_btn.setFixedSize(120, 36)
        self.yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #E53E5A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 600;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #f0546f;
            }
        """)
        self.yes_btn.clicked.connect(self.accept)
        
        btn_row.addWidget(self.no_btn)
        btn_row.addWidget(self.yes_btn)
        
        layout.addLayout(btn_row)
