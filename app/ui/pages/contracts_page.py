"""Rebuilt Contracts Page — Studio Graphite redesign matching the Stitch design system.

Features:
- Sub-views managed by QStackedWidget: History View and Analyzer View.
- Top KPI stat cards (Total Contracts, Avg. Risk, Critical Risks) with live calculations and hover shadows.
- Search and Action row (+ Analyze New button).
- Contract history table with custom StatusPills and Action buttons (View/Delete).
- Pagination of 10 items per table with Prev/Next chevron buttons and dynamic page numbers.
- Dynamic project details dropdown loading from the database.
- Upload PDF / Paste text analyzer with overall Score Circle (100x100px) and 5 criteria cards (Indemnity, Payment, IP, Termination, Revisions).
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import sys

# Add project root to sys.path if run directly
_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QEvent, Property
from PySide6.QtGui import QColor, QIcon, QPixmap, QPainter, QBrush, QFont
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QGraphicsDropShadowEffect,
    QDialog,
    QHeaderView,
)

from app.config import ASSETS_DIR
from app.data.database import Database
from app.data.repositories.contract_repo import ContractRepository
from app.data.repositories.project_repo import ProjectRepository
from app.ui.styles.theme import Colors
from app.ui.widgets.stat_card import StatCard
from app.ui.widgets.animated import AnimatedButton, AnimatedCard, GradientBar
from app.ui.widgets.page_header import PageHeader
from app.ui.widgets.status_pill import StatusPill
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


def _create_avatar_pixmap(initials: str, size: int = 28) -> QPixmap:
    """Create a circular avatar image containing initials."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Circle background (10% opacity primary color)
    painter.setBrush(QBrush(QColor(124, 138, 244, 25)))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, size, size)

    # Initials text
    painter.setPen(QColor("#bcc2ff"))
    font = QFont("Inter", 10)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, initials)

    painter.end()
    return pixmap


class RiskCriteriaCard(AnimatedCard):
    """Card showing individual risk criterion with icon and score."""

    def __init__(self, title: str, icon: str, description: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.score = 0
        self.risk_level = "LOW"
        self.findings = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        # Header row
        header_row = QHBoxLayout()
        header_row.setSpacing(12)

        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(
            "font-size: 32px; background: transparent;"
        )
        header_row.addWidget(icon_label)

        # Title column
        title_col = QVBoxLayout()
        title_col.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            f"font-size: 15px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; "
            "background: transparent;"
        )
        title_col.addWidget(self.title_label)

        self.desc_label = QLabel(description)
        self.desc_label.setWordWrap(True)
        self.desc_label.setStyleSheet(
            f"font-size: 11px; color: {Colors.TEXT_MUTED}; background: transparent;"
        )
        title_col.addWidget(self.desc_label)

        header_row.addLayout(title_col, 1)
        header_row.addStretch()

        # Score badge - perfect circle (50x50)
        self.score_badge = QLabel("—")
        self.score_badge.setAlignment(Qt.AlignCenter)
        self.score_badge.setFixedSize(50, 50)
        self.score_badge.setStyleSheet(
            f"background-color: {Colors.BG_ELEVATED}; "
            f"border: 2px solid {Colors.BORDER_SUBTLE}; "
            "border-radius: 25px; "
            "font-size: 16px; font-weight: 700; "
            f"color: {Colors.TEXT_SECONDARY};"
        )
        header_row.addWidget(self.score_badge)

        layout.addLayout(header_row)

        # Progress bar
        self.progress_bar = GradientBar(
            value=0,
            max_value=40,
            color_start=Colors.ACCENT_SUCCESS,
            color_end=Colors.ACCENT_DANGER,
            height=6,
        )
        layout.addWidget(self.progress_bar)

        # Findings list (hidden initially)
        self.findings_widget = QWidget()
        findings_layout = QVBoxLayout(self.findings_widget)
        findings_layout.setContentsMargins(0, 8, 0, 0)
        findings_layout.setSpacing(6)

        self.findings_container = QVBoxLayout()
        findings_layout.addLayout(self.findings_container)

        layout.addWidget(self.findings_widget)
        self.findings_widget.hide()

        self.setMinimumHeight(120)

    def set_result(self, score: int, risk_level: str, findings: list[str]):
        """Update card with analysis results."""
        self.score = score
        self.risk_level = risk_level
        self.findings = findings

        self.score_badge.setText(str(score))

        risk_colors = {
            "CRITICAL": Colors.ACCENT_DANGER,
            "HIGH": Colors.ACCENT_WARNING,
            "MEDIUM": Colors.ACCENT_INFO,
            "LOW": Colors.ACCENT_SUCCESS,
        }
        color = risk_colors.get(risk_level, Colors.TEXT_SECONDARY)

        self.score_badge.setStyleSheet(
            f"background-color: {color}; "
            f"border: 2px solid {color}; "
            "border-radius: 25px; "
            "font-size: 16px; font-weight: 700; "
            "color: #FFFFFF;"
        )

        self.progress_bar.set_value(min(score, 40), animate=True)

        if findings:
            self.findings_widget.show()
            # Clear old findings
            while self.findings_container.count():
                item = self.findings_container.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            # Add new findings
            for finding in findings:
                finding_label = QLabel(finding)
                finding_label.setWordWrap(True)
                finding_label.setStyleSheet(
                    f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; "
                    "background: transparent; padding: 2px 0;"
                )
                self.findings_container.addWidget(finding_label)
        else:
            self.findings_widget.hide()


class ContractDeleteConfirmDialog(QDialog):
    """Custom confirmation dialog for deleting a contract analysis."""

    def __init__(self, parent=None, is_clear_all: bool = False):
        super().__init__(parent)
        title_text = "Clear All Analyses" if is_clear_all else "Confirm Delete"
        self.setWindowTitle(title_text)
        self.setFixedSize(550, 180)
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
        layout.setSpacing(12)

        title = QLabel(title_text)
        title.setFont(QFont("Inter", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFFFFF; background: transparent;")
        layout.addWidget(title)

        question = "Are you sure you want to delete ALL contract analyses?" if is_clear_all else "Are you sure you want to delete this contract analysis?"
        question_label = QLabel(question)
        question_label.setWordWrap(True)
        question_label.setFont(QFont("Segoe UI", 12))
        question_label.setStyleSheet("color: #8B8FA8; background: transparent;")
        layout.addWidget(question_label)

        warning = "This action will permanently remove the saved analysis data. It cannot be undone."
        warning_label = QLabel(warning)
        warning_label.setWordWrap(True)
        warning_label.setFont(QFont("Segoe UI", 9))
        warning_label.setStyleSheet("color: #6B7280; background: transparent;")
        layout.addWidget(warning_label)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.setSpacing(8)

        self.no_btn = QPushButton("Cancel")
        self.no_btn.setCursor(Qt.PointingHandCursor)
        self.no_btn.setFixedSize(110, 36)
        self.no_btn.setStyleSheet("""
            QPushButton {
                background-color: #2D2F45;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #3d405c;
            }
        """)
        self.no_btn.clicked.connect(self.reject)

        self.yes_btn = QPushButton("Yes, Delete")
        self.yes_btn.setCursor(Qt.PointingHandCursor)
        self.yes_btn.setFixedSize(110, 36)
        self.yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #E53E5A;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #f0546f;
            }
        """)
        self.yes_btn.clicked.connect(self.accept)

        btn_row.addWidget(self.no_btn)
        btn_row.addWidget(self.yes_btn)
        layout.addLayout(btn_row)


class PaginationTableWidget(QTableWidget):
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


class ContractsPage(QWidget):
    """Rebuilt Contracts Page with visual risk analyzer and history list."""

    def __init__(self, db: Database):
        super().__init__()
        self.setObjectName("contracts_page")
        self.db = db
        self.project_repo = ProjectRepository(db)
        self.contract_repo = ContractRepository(db)
        self._risk_analyzer = None
        self._contract_parser = None

        self.all_contracts_raw = []
        self.filtered_contracts = []
        self.project_map = {}

        self.current_page = 0
        self.page_size = 10

        self.risk_cards = {}

        self._build_ui()
        self.refresh()

    @property
    def risk_analyzer(self):
        if self._risk_analyzer is None:
            from app.ml.risk_analyzer import RiskAnalyzer
            self._risk_analyzer = RiskAnalyzer()
        return self._risk_analyzer

    @property
    def contract_parser(self):
        if self._contract_parser is None:
            from app.ml.contract_parser import ContractParser
            self._contract_parser = ContractParser()
        return self._contract_parser

    def _build_ui(self) -> None:
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

        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignTop)

        # 1. Header Section
        self.header = PageHeader(
            title="Contract Risk Analyzer",
            subtitle="AI-powered analysis of 55+ dangerous contract clauses",
        )
        badge = QLabel("🛡️ 5 Core Risks")
        badge.setStyleSheet(
            f"background-color: rgba(130, 216, 172, 0.15); "
            f"color: {Colors.ACCENT_SUCCESS}; "
            f"border: 1px solid {Colors.ACCENT_SUCCESS}; "
            "border-radius: 999px; padding: 6px 14px; "
            "font-size: 12px; font-weight: 700;"
        )
        self.header.add_action(badge)
        layout.addWidget(self.header)

        # 2. Setup QStackedWidget for switching between History View and Analyzer View
        self.view_stack = QStackedWidget()
        layout.addWidget(self.view_stack)

        self._build_history_view()
        self._build_analyzer_view()

        self.view_stack.addWidget(self.history_view)
        self.view_stack.addWidget(self.analyzer_view)
        self.view_stack.setCurrentWidget(self.history_view)

        scroll.setWidget(content_widget)
        page_layout.addWidget(scroll)

    def _build_history_view(self) -> None:
        self.history_view = QWidget()
        history_layout = QVBoxLayout(self.history_view)
        history_layout.setContentsMargins(0, 0, 0, 0)
        history_layout.setSpacing(24)

        # Top KPI Cards row
        stat_row = QHBoxLayout()
        stat_row.setContentsMargins(0, 0, 0, 0)
        stat_row.setSpacing(16)

        self.card_total = StatCard(
            "Total Contracts", "0",
            icon="description",
            accent=Colors.ACCENT_PRIMARY_LIGHT,
            sub_text="Analyzed history"
        )
        self.card_avg = StatCard(
            "Avg. Risk Score", "0.0",
            icon="analytics",
            accent=Colors.ACCENT_INFO,
            sub_text="Score index"
        )
        self.card_critical = StatCard(
            "Critical Risks", "0",
            icon="warning",
            accent=Colors.ACCENT_DANGER,
            sub_text="High alert contracts"
        )

        tints = {
            Colors.ACCENT_PRIMARY_LIGHT: "rgba(188, 194, 255, 0.10)",
            Colors.ACCENT_INFO: "rgba(125, 211, 227, 0.10)",
            Colors.ACCENT_DANGER: "rgba(232, 124, 138, 0.10)",
        }
        card_configs = [
            (self.card_total, Colors.ACCENT_PRIMARY_LIGHT, "description"),
            (self.card_avg, Colors.ACCENT_INFO, "analytics"),
            (self.card_critical, Colors.ACCENT_DANGER, "warning"),
        ]

        for card, accent, icon_name in card_configs:
            card.setAttribute(Qt.WA_Hover, True)
            card.setMouseTracking(True)

            card_shadow = QGraphicsDropShadowEffect(card)
            card_shadow.setBlurRadius(0)
            card_shadow.setColor(QColor(124, 138, 244, 180))
            card_shadow.setOffset(0, 0)
            card.setGraphicsEffect(card_shadow)

            shadow_animation = QPropertyAnimation(card_shadow, b"blurRadius")
            shadow_animation.setDuration(200 if not is_reduced_motion() else 0)
            shadow_animation.setEasingCurve(QEasingCurve.OutCubic)

            card._shadow = card_shadow
            card._shadow_animation = shadow_animation
            card._original_stylesheet = "QFrame#dashboard_stat_card { background-color: #222336; border-radius: 12px; border: none; padding: 0px; }"
            card._hover_stylesheet = "QFrame#dashboard_stat_card { background-color: #2a2c3e; border-radius: 12px; border: none; padding: 0px; }"

            card.setMinimumHeight(140)
            card.setMaximumHeight(140)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            card.setStyleSheet(card._original_stylesheet)
            card.setContentsMargins(4, 4, 4, 4)

            card._icon_bubble.setAttribute(Qt.WA_TranslucentBackground, False)
            card._icon_bubble.setMinimumSize(24, 24)
            card._icon_bubble.setMaximumSize(24, 24)

            card_layout = card.layout()
            if card_layout:
                card_layout.setContentsMargins(20, 16, 20, 16)
                card_layout.setSpacing(4)

            rgba_color = tints.get(accent, "rgba(124, 138, 244, 0.10)")
            card._icon_bubble.setFixedSize(24, 24)
            if icon_name and (_ICONS_DIR / f"{icon_name}.svg").exists():
                icon_pixmap = _load_svg_icon(icon_name, size=16, color=accent)
                card._icon_bubble.setPixmap(icon_pixmap)
            card._icon_bubble.setStyleSheet(
                f"background-color: {rgba_color}; border-radius: 4px; border: none; min-width: 24px; max-width: 24px; min-height: 24px; max-height: 24px;"
            )

            card.installEventFilter(self)
            stat_row.addWidget(card)

        history_layout.addLayout(stat_row)

        # Search and Action Row
        search_row = QHBoxLayout()
        search_row.setSpacing(16)

        left_side = QHBoxLayout()
        left_side.setSpacing(12)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search contracts by project or text...")
        self.search_input.setFixedWidth(500)
        self.search_input.textChanged.connect(self._on_search)

        search_icon = QLabel()
        search_icon.setPixmap(_load_svg_icon("search", size=16, color="#6b6d85"))
        search_icon.setStyleSheet("background: transparent; border: none; padding-left: 8px;")

        search_layout = QHBoxLayout(self.search_input)
        search_layout.addWidget(search_icon, 0, Qt.AlignLeft | Qt.AlignVCenter)
        search_layout.addStretch()
        search_layout.setContentsMargins(0, 0, 0, 0)
        self.search_input.setTextMargins(28, 0, 0, 0)

        left_side.addWidget(self.search_input)

        # Filter button
        self.filter_btn = QPushButton("  Filter")
        self.filter_btn.setObjectName("filter_btn")
        self.filter_btn.setCursor(Qt.PointingHandCursor)
        self.filter_btn.setFixedHeight(36)
        filter_icon = _load_svg_icon("filter_list", size=16, color=Colors.TEXT_PRIMARY)
        self.filter_btn.setIcon(QIcon(filter_icon))
        self.filter_btn.clicked.connect(self._toggle_filter)

        self.filter_btn.setStyleSheet(f"""
            QPushButton#filter_btn {{
                background-color: #222336;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 0px 16px;
                color: {Colors.TEXT_PRIMARY};
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton#filter_btn:hover {{
                background-color: #2a2c3e;
                border-color: rgba(124, 138, 244, 0.3);
            }}
        """)
        self.filter_btn.setAttribute(Qt.WA_Hover, True)
        filter_shadow = QGraphicsDropShadowEffect(self.filter_btn)
        filter_shadow.setBlurRadius(0)
        filter_shadow.setColor(QColor(124, 138, 244, 180))
        filter_shadow.setOffset(0, 0)
        self.filter_btn.setGraphicsEffect(filter_shadow)

        self._filter_btn_shadow_animation = QPropertyAnimation(filter_shadow, b"blurRadius")
        self._filter_btn_shadow_animation.setDuration(200 if not is_reduced_motion() else 0)
        self._filter_btn_shadow_animation.setEasingCurve(QEasingCurve.OutCubic)

        self.filter_btn.installEventFilter(self)
        left_side.addWidget(self.filter_btn)

        search_row.addLayout(left_side)
        search_row.addStretch()

        right_side = QHBoxLayout()
        right_side.setSpacing(8)

        # Clear All button
        self.clear_btn = QPushButton(" Clear All")
        self.clear_btn.setCursor(Qt.PointingHandCursor)
        self.clear_btn.setFixedHeight(36)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #E53E5A;
                color: white;
                border-radius: 8px;
                padding: 0px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #FF4D6A;
            }
        """)
        self.clear_btn.clicked.connect(self._clear_all_analyses)
        right_side.addWidget(self.clear_btn)

        # "+ Analyze New" button
        self.add_btn = QPushButton("Analyze Contract")
        self.add_btn.setObjectName("analyze_new_btn")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setFixedHeight(36)
        self.add_btn.setStyleSheet(f"""
            QPushButton#analyze_new_btn {{
                background-color: {Colors.ACCENT_PRIMARY};
                color: #ffffff;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
            }}
            QPushButton#analyze_new_btn:hover {{
                background-color: {Colors.ACCENT_PRIMARY_HOVER};
            }}
        """)
        add_icon = _load_svg_icon("add", size=16, color="#ffffff")
        self.add_btn.setIcon(QIcon(add_icon))
        self.add_btn.clicked.connect(self._show_analyzer_view)
        right_side.addWidget(self.add_btn)

        search_row.addLayout(right_side)
        history_layout.addLayout(search_row)

        # Table Card QFrame
        self.table_card = QFrame()
        self.table_card.setObjectName("dashboard_table_card")
        self.table_card.setStyleSheet("QFrame#dashboard_table_card { background-color: #222336; border-radius: 12px; border: 1px solid #2d2e42; }")
        table_card_layout = QVBoxLayout(self.table_card)
        table_card_layout.setContentsMargins(0, 0, 0, 0)
        table_card_layout.setSpacing(0)

        # Contracts History Table
        self.table = PaginationTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "PROJECT", "DATE", "RISK SCORE", "RISK LEVEL", "HOURLY RATE", "ACTIONS"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setFrameShape(QFrame.NoFrame)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)

        self.table.setColumnWidth(1, 140)
        self.table.setColumnWidth(2, 110)
        self.table.setColumnWidth(3, 140)
        self.table.setColumnWidth(4, 130)
        self.table.setColumnWidth(5, 100)

        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        table_card_layout.addWidget(self.table)

        # Pagination Footer
        self.footer_widget = QWidget()
        self.footer_widget.setObjectName("table_footer")
        self.footer_widget.setStyleSheet("QWidget#table_footer { background-color: transparent; border-top: 1px solid #2d2e42; }")
        footer_layout = QHBoxLayout(self.footer_widget)
        footer_layout.setContentsMargins(24, 16, 24, 16)

        self.info_label = QLabel()
        self.info_label.setStyleSheet("color: #9a9cb8; font-size: 13px;")
        footer_layout.addWidget(self.info_label, 0, Qt.AlignLeft | Qt.AlignVCenter)
        footer_layout.addStretch()

        # Previous and Next buttons
        self.controls_widget = QWidget()
        self.controls_widget.setStyleSheet("background: transparent; border: none;")
        self.controls_layout = QHBoxLayout(self.controls_widget)
        self.controls_layout.setContentsMargins(0, 0, 0, 0)
        self.controls_layout.setSpacing(6)

        self.prev_btn = QPushButton()
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
                border: 1px solid #1e1f2a;
            }
        """)
        self.prev_btn.clicked.connect(self._prev_page)
        self.controls_layout.addWidget(self.prev_btn)

        self.page_buttons_widget = QWidget()
        self.page_buttons_widget.setStyleSheet("background: transparent; border: none;")
        self.page_buttons_layout = QHBoxLayout(self.page_buttons_widget)
        self.page_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.page_buttons_layout.setSpacing(6)
        self.controls_layout.addWidget(self.page_buttons_widget)

        self.next_btn = QPushButton()
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
                border: 1px solid #1e1f2a;
            }
        """)
        self.next_btn.clicked.connect(self._next_page)
        self.controls_layout.addWidget(self.next_btn)

        footer_layout.addWidget(self.controls_widget, 0, Qt.AlignCenter | Qt.AlignVCenter)
        footer_layout.addStretch()

        self.page_size_combo = QComboBox()
        self.page_size_combo.addItems(["10 per page"])
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

        table_card_layout.addWidget(self.footer_widget)
        history_layout.addWidget(self.table_card)

    def _build_analyzer_view(self) -> None:
        self.analyzer_view = QWidget()
        analyzer_layout = QVBoxLayout(self.analyzer_view)
        analyzer_layout.setContentsMargins(0, 0, 0, 0)
        analyzer_layout.setSpacing(24)

        # Back Row
        back_row = QHBoxLayout()
        back_row.setContentsMargins(0, 0, 0, 0)
        self.back_btn = QPushButton("← Back to History")
        self.back_btn.setObjectName("back_btn")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self._show_history_view)
        self.back_btn.setStyleSheet(f"""
            QPushButton#back_btn {{
                background-color: transparent;
                color: {Colors.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: 600;
                border: none;
                padding: 8px 12px;
            }}
            QPushButton#back_btn:hover {{
                color: {Colors.ACCENT_PRIMARY};
            }}
        """)
        back_row.addWidget(self.back_btn)
        back_row.addStretch()
        analyzer_layout.addLayout(back_row)

        # Input card
        input_card = AnimatedCard()
        input_layout = QVBoxLayout(input_card)
        input_layout.setContentsMargins(28, 24, 28, 24)
        input_layout.setSpacing(20)

        upload_title = QLabel("📄 Contract Upload")
        upload_title.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; "
            "background: transparent;"
        )
        input_layout.addWidget(upload_title)

        file_row = QHBoxLayout()
        file_row.setSpacing(16)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; font-size: 13px;"
        )
        file_row.addWidget(self.file_label, 1)

        upload_btn = AnimatedButton("📤 Upload PDF", accent=Colors.ACCENT_INFO)
        upload_btn.setCursor(Qt.PointingHandCursor)
        upload_btn.clicked.connect(self._upload_pdf)
        upload_btn.setFixedHeight(42)
        file_row.addWidget(upload_btn)
        input_layout.addLayout(file_row)

        text_label = QLabel("Or paste contract text:")
        text_label.setStyleSheet(
            f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; background: transparent;"
        )
        input_layout.addWidget(text_label)

        self.contract_text = QTextEdit()
        self.contract_text.setPlaceholderText(
            "Paste your contract here...\n\n"
            "The analyzer will scan for:\n"
            "• Unlimited liability clauses\n"
            "• Extended payment terms (Net-60/90)\n"
            "• IP transfer before payment\n"
            "• Termination without compensation\n"
            "• Unlimited revision requirements"
        )
        self.contract_text.setMinimumHeight(160)
        self.contract_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1f2a;
                border: 1px solid #2d2e42;
                border-radius: 10px;
                padding: 10px 14px;
                color: #e2e4f0;
                font-size: 14px;
            }
        """)
        input_layout.addWidget(self.contract_text)

        params_title = QLabel("⚙️ Project Details (Optional)")
        params_title.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; "
            "background: transparent; margin-top: 12px;"
        )
        input_layout.addWidget(params_title)

        params_grid = QGridLayout()
        params_grid.setSpacing(16)
        params_grid.setColumnStretch(1, 1)
        params_grid.setColumnStretch(3, 1)

        self.project_combo = QComboBox()
        self.rate_input = QDoubleSpinBox()
        self.rate_input.setRange(0, 100000)
        self.rate_input.setPrefix("₹ ")
        self.rate_input.setValue(500)

        self.revisions_input = QSpinBox()
        self.revisions_input.setRange(0, 20)
        self.revisions_input.setValue(2)

        self.timeline_input = QSpinBox()
        self.timeline_input.setRange(1, 365)
        self.timeline_input.setValue(14)
        self.timeline_input.setSuffix(" days")

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Design", "Video", "Writing", "Music", "Development", "General"])

        params_grid.addWidget(QLabel("Project:"), 0, 0)
        params_grid.addWidget(self.project_combo, 0, 1)
        params_grid.addWidget(QLabel("Hourly Rate:"), 0, 2)
        params_grid.addWidget(self.rate_input, 0, 3)

        params_grid.addWidget(QLabel("Revision Rounds:"), 1, 0)
        params_grid.addWidget(self.revisions_input, 1, 1)
        params_grid.addWidget(QLabel("Timeline:"), 1, 2)
        params_grid.addWidget(self.timeline_input, 1, 3)

        params_grid.addWidget(QLabel("Project Type:"), 2, 0)
        params_grid.addWidget(self.type_combo, 2, 1, 1, 3)

        for combo in (self.project_combo, self.type_combo):
            combo.setStyleSheet("""
                QComboBox {
                    background-color: #1e1f2a;
                    border: 1px solid #2d2e42;
                    border-radius: 6px;
                    padding: 4px 10px;
                    color: #e2e4f0;
                    font-size: 13px;
                }
            """)
        for spin in (self.rate_input, self.revisions_input, self.timeline_input):
            spin.setStyleSheet("""
                QAbstractSpinBox {
                    background-color: #1e1f2a;
                    border: 1px solid #2d2e42;
                    border-radius: 6px;
                    padding: 4px 10px;
                    color: #e2e4f0;
                    font-size: 13px;
                }
            """)

        input_layout.addLayout(params_grid)

        # Analyze button
        self.analyze_btn = AnimatedButton("🔍 Analyze Contract Risk", accent=Colors.ACCENT_PRIMARY)
        self.analyze_btn.setCursor(Qt.PointingHandCursor)
        self.analyze_btn.clicked.connect(lambda: self._analyze(save_db=True))
        self.analyze_btn.setFixedHeight(48)
        font = QFont()
        font.setPointSize(14)
        font.setWeight(QFont.Bold)
        self.analyze_btn.setFont(font)
        input_layout.addWidget(self.analyze_btn)

        analyzer_layout.addWidget(input_card)

        # Results Container (starts hidden)
        self.results_container = QWidget()
        results_layout = QVBoxLayout(self.results_container)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(24)

        # Overall Assessment Card
        self.overall_card = AnimatedCard()
        overall_layout = QVBoxLayout(self.overall_card)
        overall_layout.setContentsMargins(32, 28, 32, 28)
        overall_layout.setSpacing(16)

        overall_title = QLabel("📊 Overall Risk Assessment")
        overall_title.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; "
            "background: transparent;"
        )
        overall_layout.addWidget(overall_title)

        risk_display = QHBoxLayout()
        risk_display.setSpacing(24)

        score_container = QVBoxLayout()
        score_container.setAlignment(Qt.AlignCenter)

        self.score_circle = QLabel("—")
        self.score_circle.setAlignment(Qt.AlignCenter)
        self.score_circle.setFixedSize(100, 100)
        self.score_circle.setStyleSheet(
            f"background-color: {Colors.BG_ELEVATED}; "
            f"border: 4px solid {Colors.BORDER_SUBTLE}; "
            "border-radius: 50px; "
            "font-size: 32px; font-weight: 700; "
            f"color: {Colors.TEXT_PRIMARY};"
        )
        score_container.addWidget(self.score_circle)

        score_label = QLabel("Risk Score")
        score_label.setAlignment(Qt.AlignCenter)
        score_label.setStyleSheet(
            f"font-size: 12px; color: {Colors.TEXT_MUTED}; background: transparent;"
        )
        score_container.addWidget(score_label)
        risk_display.addLayout(score_container)

        level_container = QVBoxLayout()
        level_container.setAlignment(Qt.AlignLeft)
        level_container.setSpacing(8)

        self.risk_level_label = QLabel("Risk Level: Not Analyzed")
        self.risk_level_label.setStyleSheet(
            f"font-size: 24px; font-weight: 700; color: {Colors.TEXT_SECONDARY}; "
            "background: transparent;"
        )
        level_container.addWidget(self.risk_level_label)

        self.recommendation_label = QLabel("Upload a contract to begin analysis")
        self.recommendation_label.setWordWrap(True)
        self.recommendation_label.setStyleSheet(
            f"font-size: 14px; color: {Colors.TEXT_MUTED}; background: transparent;"
        )
        level_container.addWidget(self.recommendation_label)
        risk_display.addLayout(level_container, 1)

        overall_layout.addLayout(risk_display)

        self.overall_progress = GradientBar(
            value=0,
            max_value=150,
            color_start=Colors.ACCENT_SUCCESS,
            color_end=Colors.ACCENT_DANGER,
            height=12,
        )
        overall_layout.addWidget(self.overall_progress)
        results_layout.addWidget(self.overall_card)

        # 5 Critical Areas Grid
        self.criteria_title = QLabel("🎯 5 Critical Risk Areas")
        self.criteria_title.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; "
            "background: transparent;"
        )
        results_layout.addWidget(self.criteria_title)

        criteria_grid = QGridLayout()
        criteria_grid.setSpacing(24)

        criteria_defs = [
            ("indemnity", "⚖️", "Indemnity Clause", "Unlimited liability exposure"),
            ("payment_terms", "💰", "Payment Terms", "Extended payment delays"),
            ("ip_transfer", "🎨", "IP Transfer", "Loss of ownership rights"),
            ("termination", "🚫", "Termination", "Cancellation without payment"),
            ("revision_scope", "🔄", "Revision Scope", "Unlimited work requirements"),
        ]

        for idx, (key, icon, title, desc) in enumerate(criteria_defs):
            card = RiskCriteriaCard(title, icon, desc)
            self.risk_cards[key] = card
            row = idx // 2
            col = idx % 2
            if idx == 4:
                # Span revision scope card across both columns for visual balance
                criteria_grid.addWidget(card, row, col, 1, 2)
            else:
                criteria_grid.addWidget(card, row, col)

        results_layout.addLayout(criteria_grid)

        # Detailed Findings Table
        self.findings_title = QLabel("📋 Detailed Findings")
        self.findings_title.setStyleSheet(
            f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_PRIMARY}; "
            "background: transparent;"
        )
        results_layout.addWidget(self.findings_title)

        self.findings_table = QTableWidget()
        self.findings_table.setColumnCount(3)
        self.findings_table.setHorizontalHeaderLabels(["Category", "Finding", "Score"])
        self.findings_table.horizontalHeader().setStretchLastSection(True)
        self.findings_table.verticalHeader().setVisible(False)
        self.findings_table.setShowGrid(False)
        self.findings_table.setAlternatingRowColors(True)
        self.findings_table.setMinimumHeight(200)
        self.findings_table.setStyleSheet("""
            QTableWidget {
                background-color: #222336;
                border: 1px solid #2d2e42;
                border-radius: 10px;
            }
        """)
        results_layout.addWidget(self.findings_table)

        analyzer_layout.addWidget(self.results_container)
        self.results_container.hide()

    def eventFilter(self, obj, event) -> bool:
        """Handle hover events for stat cards to trigger shadow animation."""
        if obj in (self.card_total, self.card_avg, self.card_critical):
            if hasattr(obj, "_shadow") and hasattr(obj, "_shadow_animation"):
                event_type = event.type()
                if event_type == QEvent.Enter:
                    obj._shadow_animation.stop()
                    obj._shadow_animation.setStartValue(obj._shadow.blurRadius())
                    obj._shadow_animation.setEndValue(20 if not is_reduced_motion() else 0)
                    obj._shadow_animation.start()
                    obj.setStyleSheet(obj._hover_stylesheet)
                elif event_type == QEvent.Leave:
                    obj._shadow_animation.stop()
                    obj._shadow_animation.setStartValue(obj._shadow.blurRadius())
                    obj._shadow_animation.setEndValue(0)
                    obj._shadow_animation.start()
                    obj.setStyleSheet(obj._original_stylesheet)
        elif obj == self.filter_btn:
            shadow = self.filter_btn.graphicsEffect()
            if shadow and hasattr(self, "_filter_btn_shadow_animation"):
                event_type = event.type()
                if event_type == QEvent.Enter:
                    self._filter_btn_shadow_animation.stop()
                    self._filter_btn_shadow_animation.setStartValue(shadow.blurRadius())
                    self._filter_btn_shadow_animation.setEndValue(15 if not is_reduced_motion() else 0)
                    self._filter_btn_shadow_animation.start()
                elif event_type == QEvent.Leave:
                    self._filter_btn_shadow_animation.stop()
                    self._filter_btn_shadow_animation.setStartValue(shadow.blurRadius())
                    self._filter_btn_shadow_animation.setEndValue(0)
                    self._filter_btn_shadow_animation.start()
        return super().eventFilter(obj, event)

    def refresh(self) -> None:
        """Reload project dropdowns, retrieve contracts from DB, recalculate KPIs, and populate table."""
        try:
            contracts = self.contract_repo.get_all()
        except Exception:
            contracts = []

        self.all_contracts_raw = [dict(c) for c in contracts]

        # Load projects mapping
        try:
            projects = self.project_repo.get_all()
            self.project_map = {p["id"]: p["name"] for p in projects}
        except Exception:
            self.project_map = {}

        # Populate projects dropdown
        self.project_combo.clear()
        self.project_combo.addItem("Select Project", None)
        for p in projects:
            self.project_combo.addItem(p["name"], p["id"])

        # Recalculate KPIs
        total_count = len(self.all_contracts_raw)
        avg_score = 0.0
        critical_count = 0

        if total_count > 0:
            avg_score = sum(c["risk_score"] for c in self.all_contracts_raw) / total_count
            critical_count = sum(1 for c in self.all_contracts_raw if c["risk_level"] == "CRITICAL" or c["risk_score"] >= 100)

        self.card_total.set_value(str(total_count))
        self.card_avg.set_value(f"{avg_score:.1f}")
        self.card_critical.set_value(str(critical_count))

        # Re-apply filter rules & search
        self._on_search(self.search_input.text())

    def _show_history_view(self) -> None:
        self.view_stack.setCurrentWidget(self.history_view)
        self.refresh()

    def _show_analyzer_view(self) -> None:
        # Reset inputs
        self.contract_text.clear()
        self.file_label.setText("No file selected")
        self.file_label.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; font-size: 13px;"
        )
        self.project_combo.setCurrentIndex(0)
        self.rate_input.setValue(500)
        self.revisions_input.setValue(2)
        self.timeline_input.setValue(14)
        self.type_combo.setCurrentIndex(0)

        self.results_container.hide()
        self.view_stack.setCurrentWidget(self.analyzer_view)

    def _toggle_filter(self) -> None:
        pass  # Filter dropdown details omitted for simplicity

    def _upload_pdf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Contract PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        filename = path.replace("\\", "/").split("/")[-1]
        self.file_label.setText(f"✅ {filename}")
        self.file_label.setStyleSheet(
            f"color: {Colors.ACCENT_SUCCESS}; background: transparent; font-size: 13px; font-weight: 600;"
        )
        try:
            text = self.contract_parser.extract_text(path)
            self.contract_text.setPlainText(text)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not read PDF: {e}")

    def _analyze(self, save_db: bool = True) -> None:
        contract_content = self.contract_text.toPlainText().strip()
        if not contract_content:
            QMessageBox.warning(
                self,
                "Missing Contract",
                "Please paste contract text or upload a PDF before analyzing.",
            )
            return

        self.results_container.show()

        try:
            # Run full analysis
            result = self.risk_analyzer.full_analysis(
                hourly_rate=self.rate_input.value(),
                revisions=self.revisions_input.value(),
                timeline_days=self.timeline_input.value(),
                project_type=self.type_combo.currentText(),
                contract_text=contract_content,
            )

            # Run critical clause analysis
            critical = self.risk_analyzer.analyze_critical_clauses(contract_content)

        except Exception as e:
            QMessageBox.critical(self, "Analysis Failed", f"Error: {e}")
            return

        # Update overall score
        total_score = result["total_score"]
        level = result["risk_level"]

        self.score_circle.setText(str(total_score))

        level_colors = {
            "LOW": Colors.ACCENT_SUCCESS,
            "MEDIUM": Colors.ACCENT_INFO,
            "HIGH": Colors.ACCENT_WARNING,
            "CRITICAL": Colors.ACCENT_DANGER,
        }
        color = level_colors.get(level, Colors.TEXT_SECONDARY)

        self.score_circle.setStyleSheet(
            f"background-color: {color}; "
            f"border: 4px solid {color}; "
            "border-radius: 50px; "
            "font-size: 32px; font-weight: 700; "
            "color: #FFFFFF;"
        )

        self.risk_level_label.setText(f"Risk Level: {level}")
        self.risk_level_label.setStyleSheet(
            f"font-size: 24px; font-weight: 700; color: {color}; background: transparent;"
        )

        recommendations = {
            "LOW": "✅ Acceptable risk - proceed with standard caution",
            "MEDIUM": "⚠️ Review carefully and negotiate weak points",
            "HIGH": "🚨 Serious concerns - negotiate heavily or walk away",
            "CRITICAL": "❌ DO NOT SIGN - extremely dangerous contract",
        }
        self.recommendation_label.setText(recommendations.get(level, ""))

        self.overall_progress.set_value(min(total_score, 150), animate=True)

        # Update 5 critical area cards
        for key, card in self.risk_cards.items():
            if key in critical:
                data = critical[key]
                card.set_result(
                    score=data["score"],
                    risk_level=data["risk"],
                    findings=data["findings"]
                )

        # Update findings table
        findings = result["findings"]
        self.findings_table.setRowCount(len(findings))
        for i, f in enumerate(findings):
            # Category
            cat_item = QTableWidgetItem(f["check"])
            cat_item.setFont(QFont("Inter", 11, QFont.Bold))
            self.findings_table.setItem(i, 0, cat_item)

            # Finding
            self.findings_table.setItem(i, 1, QTableWidgetItem(f["result"]))

            # Score
            score_item = QTableWidgetItem(str(f["score"]))
            score_item.setFont(QFont("Inter", 11, QFont.Bold))
            if f["score"] >= 25:
                score_item.setForeground(QColor(Colors.ACCENT_DANGER))
            elif f["score"] >= 15:
                score_item.setForeground(QColor(Colors.ACCENT_WARNING))
            elif f["score"] >= 8:
                score_item.setForeground(QColor(Colors.ACCENT_INFO))
            else:
                score_item.setForeground(QColor(Colors.ACCENT_SUCCESS))
            self.findings_table.setItem(i, 2, score_item)

        # Save to database if requested
        if save_db:
            project_id = self.project_combo.currentData()
            if project_id:
                try:
                    self.contract_repo.add(
                        project_id=project_id,
                        contract_text=contract_content[:5000],
                        hourly_rate=self.rate_input.value(),
                        revision_rounds=self.revisions_input.value(),
                        timeline_days=self.timeline_input.value(),
                        risk_score=result["total_score"],
                        risk_level=level,
                        findings=json.dumps(findings),
                    )
                    emit_data_changed()
                except Exception:
                    pass

    def _on_search(self, text: str) -> None:
        self.filtered_contracts = []
        search_term = text.strip().lower()

        for c in self.all_contracts_raw:
            proj_name = self.project_map.get(c["project_id"], "General Contract").lower()
            text_match = c["contract_text"].lower()
            if not search_term or (search_term in proj_name or search_term in text_match):
                self.filtered_contracts.append(c)

        self.current_page = 0
        self._populate_table_current_page()

    def _populate_table_current_page(self) -> None:
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_contracts = self.filtered_contracts[start_idx:end_idx]

        self.table.clearSpans()
        if not page_contracts:
            self.table.setRowCount(1)
            self.table.setRowHeight(0, 120)
            self.table.setSpan(0, 0, 1, 6)
            empty_label = QLabel("No analyzed contracts found. Upload one to start.")
            empty_label.setStyleSheet("color: #6B7280; font-size: 13px;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(0, 0, empty_label)
        else:
            self.table.setRowCount(len(page_contracts))
            self.table.verticalHeader().setDefaultSectionSize(48)

            for i, c in enumerate(page_contracts):
                contract_id = c["id"]

                # 1. Project name with custom circular avatar
                proj_name = self.project_map.get(c["project_id"], "General Contract")
                initials = "".join([p[0] for p in proj_name.split() if p])[:2].upper()

                project_widget = QFrame()
                project_layout = QHBoxLayout(project_widget)
                project_layout.setContentsMargins(8, 0, 8, 0)
                project_layout.setSpacing(8)

                avatar_lbl = QLabel()
                avatar_lbl.setPixmap(_create_avatar_pixmap(initials, size=28))
                project_layout.addWidget(avatar_lbl)

                name_lbl = QLabel(proj_name)
                name_lbl.setStyleSheet(f"font-weight: 600; color: {Colors.TEXT_PRIMARY};")
                project_layout.addWidget(name_lbl)
                project_layout.addStretch()

                self.table.setCellWidget(i, 0, project_widget)

                # 2. Date
                raw_date = c.get("analyzed_date") or ""
                formatted_date = "—"
                if raw_date:
                    try:
                        dt = datetime.fromisoformat(raw_date.replace(" ", "T"))
                        formatted_date = dt.strftime("%d %b, %Y")
                    except Exception:
                        formatted_date = raw_date
                date_item = QTableWidgetItem(formatted_date)
                date_item.setForeground(QColor(Colors.TEXT_SECONDARY))
                self.table.setItem(i, 1, date_item)

                # 3. Risk Score
                score_item = QTableWidgetItem(str(c["risk_score"]))
                score_item.setFont(QFont("Inter", 11, QFont.Bold))
                score_item.setTextAlignment(Qt.AlignCenter)
                score_item.setForeground(QColor(Colors.TEXT_PRIMARY))
                self.table.setItem(i, 2, score_item)

                # 4. Risk Level (StatusPill)
                level = c["risk_level"]
                level_colors = {
                    "LOW": Colors.ACCENT_SUCCESS,
                    "MEDIUM": Colors.ACCENT_INFO,
                    "HIGH": Colors.ACCENT_WARNING,
                    "CRITICAL": Colors.ACCENT_DANGER,
                }
                pill = StatusPill(level, level_colors.get(level, Colors.TEXT_SECONDARY))
                pill_container = QWidget()
                pill_layout = QHBoxLayout(pill_container)
                pill_layout.setContentsMargins(0, 0, 0, 0)
                pill_layout.setAlignment(Qt.AlignCenter)
                pill_layout.addWidget(pill)
                self.table.setCellWidget(i, 3, pill_container)

                # 5. Hourly Rate
                rate = c["hourly_rate"]
                rate_str = f"₹ {rate:,.0f}/hr" if rate > 0 else "—"
                rate_item = QTableWidgetItem(rate_str)
                rate_item.setForeground(QColor(Colors.TEXT_SECONDARY))
                self.table.setItem(i, 4, rate_item)

                # 6. Actions
                actions_widget = self._create_actions_cell(contract_id)
                self.table.setCellWidget(i, 5, actions_widget)

        self.table.updateGeometry()
        self._update_pagination_ui()

    def _create_actions_cell(self, contract_id: int) -> QWidget:
        container = QFrame()
        container.setObjectName("table_actions_container")
        container.setFrameShape(QFrame.NoFrame)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 16, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        view_btn = QPushButton()
        view_btn.setObjectName("table_action_icon_btn")
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.setToolTip("View Analysis")
        view_btn.setIcon(QIcon(_load_svg_icon("edit", size=18, color="#6b6d85")))
        view_btn.setIconSize(QSize(18, 18))
        view_btn.clicked.connect(lambda: self._view_analysis(contract_id))

        del_btn = QPushButton()
        del_btn.setObjectName("table_action_icon_btn")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Delete Analysis")
        del_btn.setIcon(QIcon(_load_svg_icon("delete", size=18, color="#6b6d85")))
        del_btn.setIconSize(QSize(18, 18))
        del_btn.clicked.connect(lambda: self._delete_analysis(contract_id))

        layout.addWidget(view_btn)
        layout.addWidget(del_btn)
        return container

    def _view_analysis(self, contract_id: int) -> None:
        contract = next((c for c in self.all_contracts_raw if c["id"] == contract_id), None)
        if not contract:
            return

        self.view_stack.setCurrentWidget(self.analyzer_view)

        # Populate inputs
        self.contract_text.setPlainText(contract["contract_text"])
        self.rate_input.setValue(contract["hourly_rate"])
        self.revisions_input.setValue(contract["revision_rounds"])
        self.timeline_input.setValue(contract["timeline_days"])

        proj_idx = self.project_combo.findData(contract["project_id"])
        if proj_idx >= 0:
            self.project_combo.setCurrentIndex(proj_idx)
        else:
            self.project_combo.setCurrentIndex(0)

        # Re-run analysis UI without saving duplicate row
        self._analyze(save_db=False)

    def _delete_analysis(self, contract_id: int) -> None:
        dialog = ContractDeleteConfirmDialog(self)
        if dialog.exec() == QDialog.Accepted:
            try:
                self.db.execute("DELETE FROM contracts WHERE id = ?", (contract_id,))
                emit_data_changed()
                self.refresh()
                from app.ui.pages.clients_page import SuccessDialog
                SuccessDialog.show_success("Analysis deleted successfully.", self)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete: {e}")

    def _clear_all_analyses(self) -> None:
        dialog = ContractDeleteConfirmDialog(self, is_clear_all=True)
        if dialog.exec() == QDialog.Accepted:
            try:
                self.db.execute("DELETE FROM contracts")
                emit_data_changed()
                self.refresh()
                from app.ui.pages.clients_page import SuccessDialog
                SuccessDialog.show_success("All analyses cleared.", self)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not clear: {e}")

    def _update_pagination_ui(self) -> None:
        total_items = len(self.filtered_contracts)
        total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)

        if self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)

        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, total_items)

        if total_items == 0:
            self.info_label.setText("Showing 0 to 0 of 0 contracts")
        else:
            self.info_label.setText(f"Showing {start_idx + 1} to {end_idx} of {total_items} contracts")

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
        total_items = len(self.filtered_contracts)
        total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages - 1:
            self._go_to_page(self.current_page + 1)
