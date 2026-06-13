"""Rebuilt Contracts Page — Studio Graphite redesign matching the HTML design mockup.

Features:
- Sub-views managed by QStackedWidget: History View and Analyzer View.
- Top KPI stat cards (Total Contracts, Avg. Risk, Critical Risks) with live calculations and hover shadows.
- Search and Action row (+ Analyze New button).
- Contract history table with custom StatusPills and Action buttons (View/Delete).
- Pagination of 10 items per table with Prev/Next chevron buttons and dynamic page numbers.
- Dynamic project details dropdown loading from the database.
- Upload PDF / Paste text analyzer with custom circular progress score ring and 5 critical risk cards.
- Multi-colored sliding indicator progress bar representing overall risk.
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

from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QEvent, Property, Signal
from PySide6.QtGui import QColor, QIcon, QPixmap, QPainter, QBrush, QFont, QPen, QLinearGradient, QPainterPath
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
from app.ui.pages.dashboard_page import DashboardStatCard
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


class CircularRiskScore(QWidget):
    """Circular risk score visualization drawing an arc using QPainter."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(130, 130)
        self._score = 0
        self._animated_score = 0.0
        self._color = QColor(Colors.ACCENT_SUCCESS)

        self._anim = QPropertyAnimation(self, b"animatedScore")
        self._anim.setDuration(0 if is_reduced_motion() else 800)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def get_animated_score(self) -> float:
        return self._animated_score

    def set_animated_score(self, val: float) -> None:
        self._animated_score = val
        self.update()

    animatedScore = Property(float, get_animated_score, set_animated_score)

    def set_score(self, score: int, color_hex: str) -> None:
        self._score = score
        self._color = QColor(color_hex)

        self._anim.stop()
        self._anim.setStartValue(self._animated_score)
        self._anim.setEndValue(float(score))
        self._anim.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        cx = rect.width() / 2.0
        cy = rect.height() / 2.0
        radius = min(rect.width(), rect.height()) / 2.0 - 10.0

        # Draw background track
        pen_track = QPen(QColor("#2d2e42"))
        pen_track.setWidth(8)
        pen_track.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_track)
        painter.drawEllipse(cx - radius, cy - radius, radius * 2.0, radius * 2.0)

        # Draw active foreground arc
        max_value = 100
        ratio = min(self._animated_score / max_value, 1.0)
        span_angle = -int(ratio * 360 * 16)
        start_angle = 90 * 16

        pen_active = QPen(self._color)
        pen_active.setWidth(8)
        pen_active.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_active)
        painter.drawArc(cx - radius, cy - radius, radius * 2.0, radius * 2.0, start_angle, span_angle)

        # Draw text in center
        score_text = str(int(self._animated_score))
        painter.setPen(QColor(Colors.TEXT_PRIMARY))
        font_score = QFont("Inter", 28, QFont.Bold)
        painter.setFont(font_score)
        painter.drawText(rect.adjusted(0, -12, 0, -12), Qt.AlignCenter, score_text)

        painter.setPen(QColor(Colors.TEXT_MUTED))
        font_max = QFont("Inter", 10, QFont.Weight.Medium)
        painter.setFont(font_max)
        painter.drawText(rect.adjusted(0, 24, 0, 24), Qt.AlignCenter, "/ 100")

        painter.end()


class MultiColorGradientBar(QWidget):
    """
    Progress bar with a three-color gradient (Green -> Lavender -> Red)
    and a sliding indicator line showing the current score.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(12)
        self.setMinimumWidth(150)
        self._score = 0.0
        self._animated_score = 0.0

        self._anim = QPropertyAnimation(self, b"animatedScore")
        self._anim.setDuration(0 if is_reduced_motion() else 1200)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def get_animated_score(self) -> float:
        return self._animated_score

    def set_animated_score(self, val: float) -> None:
        self._animated_score = val
        self.update()

    animatedScore = Property(float, get_animated_score, set_animated_score)

    def set_score(self, score: float, animate: bool = True) -> None:
        self._score = score
        if animate:
            self._anim.stop()
            self._anim.setStartValue(self._animated_score)
            self._anim.setEndValue(score)
            self._anim.start()
        else:
            self._animated_score = score
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        radius = rect.height() / 2.0

        # Background track
        bg_path = QPainterPath()
        bg_path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), radius, radius)
        painter.fillPath(bg_path, QColor(Colors.BG_ELEVATED))

        # Filled portion
        max_value = 150
        ratio = min(self._animated_score / max_value, 1.0)
        fill_width = rect.width() * ratio

        if fill_width > 0:
            gradient = QLinearGradient(0, 0, rect.width(), 0)
            gradient.setColorAt(0.0, QColor("#82d8ac"))  # Green
            gradient.setColorAt(0.5, QColor("#7c8af4"))  # Lavender
            gradient.setColorAt(1.0, QColor("#e87c8a"))  # Red

            fill_path = QPainterPath()
            fill_path.addRoundedRect(rect.x(), rect.y(), fill_width, rect.height(), radius, radius)
            painter.fillPath(fill_path, gradient)

            # Draw white indicator line
            pen = QPen(QColor("#FFFFFF"))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(fill_width, rect.y(), fill_width, rect.y() + rect.height())

        painter.end()


class UploadDashedArea(QFrame):
    """Dashed area inside upload card supporting drag and drop of PDF files."""
    file_dropped = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("uploadDashedArea")
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QFrame#uploadDashedArea {
                border: 2px dashed #333440;
                border-radius: 12px;
                background-color: #1a1b26;
            }
            QFrame#uploadDashedArea:hover {
                border-color: #7c8af4;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        self.icon_label = QLabel("☁️")
        self.icon_label.setStyleSheet("font-size: 36px; background: transparent; border: none;")
        layout.addWidget(self.icon_label, 0, Qt.AlignCenter)

        self.text_label = QLabel("Drop contract PDF here or click to browse")
        self.text_label.setStyleSheet("color: #e2e4f0; font-size: 14px; font-weight: 500; background: transparent; border: none;")
        layout.addWidget(self.text_label, 0, Qt.AlignCenter)

        self.subtext_label = QLabel("Supports PDF (Max 10MB)")
        self.subtext_label.setStyleSheet("color: #6b6d85; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(self.subtext_label, 0, Qt.AlignCenter)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QFrame#uploadDashedArea {
                    border: 2px dashed #7c8af4;
                    border-radius: 12px;
                    background-color: #222336;
                }
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QFrame#uploadDashedArea {
                border: 2px dashed #333440;
                border-radius: 12px;
                background-color: #1a1b26;
            }
        """)

    def dropEvent(self, event):
        self.setStyleSheet("""
            QFrame#uploadDashedArea {
                border: 2px dashed #333440;
                border-radius: 12px;
                background-color: #1a1b26;
            }
        """)
        for url in event.mimeData().urls():
            filepath = url.toLocalFile()
            if filepath.lower().endswith('.pdf'):
                self.file_dropped.emit(filepath)
                break

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.file_dropped.emit("")


class RiskProgressBar(QWidget):
    """Simple progress bar styled with a single dynamic risk color."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(6)
        self._value = 0.0
        self._animated_value = 0.0
        self._color = QColor(Colors.ACCENT_SUCCESS)

        self._anim = QPropertyAnimation(self, b"animatedValue")
        self._anim.setDuration(0 if is_reduced_motion() else 600)
        self._anim.setEasingCurve(QEasingCurve.OutCubic)

    def get_animated_value(self) -> float:
        return self._animated_value

    def set_animated_value(self, v: float) -> None:
        self._animated_value = v
        self.update()

    animatedValue = Property(float, get_animated_value, set_animated_value)

    def set_value(self, value: float, color_hex: str, animate: bool = True) -> None:
        self._value = value
        self._color = QColor(color_hex)
        if animate:
            self._anim.stop()
            self._anim.setStartValue(self._animated_value)
            self._anim.setEndValue(value)
            self._anim.start()
        else:
            self._animated_value = value
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        radius = rect.height() / 2.0

        # Background track
        bg_path = QPainterPath()
        bg_path.addRoundedRect(rect, radius, radius)
        painter.fillPath(bg_path, QColor("#1e1f2a"))

        # Filled portion
        max_value = 40
        ratio = min(self._animated_value / max_value, 1.0)
        fill_width = rect.width() * ratio

        if fill_width > 0:
            fill_path = QPainterPath()
            fill_path.addRoundedRect(0, 0, fill_width, rect.height(), radius, radius)
            painter.fillPath(fill_path, self._color)

        painter.end()


class RiskCriteriaCard(QFrame):
    """Card showing individual risk criterion with icon, score badge, progress, and findings."""

    def __init__(self, title: str, icon: str, description: str, parent=None):
        super().__init__(parent)
        self.setObjectName("riskCard")
        self.setStyleSheet("""
            QFrame#riskCard {
                background-color: #1a1b26;
                border: 1px solid #333440;
                border-radius: 14px;
            }
        """)
        self.setMinimumHeight(140)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header Row
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        # Icon
        self.icon_label = QLabel(icon)
        self.icon_label.setStyleSheet("font-size: 28px; background: transparent; border: none;")
        header_layout.addWidget(self.icon_label)

        # Title Stack
        title_stack = QVBoxLayout()
        title_stack.setSpacing(2)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 15px; font-weight: 700; color: #e2e4f0; background: transparent; border: none;")
        title_stack.addWidget(self.title_label)

        self.desc_label = QLabel(description)
        self.desc_label.setStyleSheet("font-size: 11px; color: #6b6d85; background: transparent; border: none;")
        title_stack.addWidget(self.desc_label)

        header_layout.addLayout(title_stack, 1)

        # Score Badge
        self.score_badge = QLabel("—")
        self.score_badge.setAlignment(Qt.AlignCenter)
        self.score_badge.setFixedSize(44, 44)
        self.score_badge.setStyleSheet("""
            background-color: #1e1f2a;
            border: 2px solid #2d2e42;
            border-radius: 22px;
            font-size: 14px;
            font-weight: 700;
            color: #9a9cb8;
        """)
        header_layout.addWidget(self.score_badge)

        layout.addLayout(header_layout)

        # Progress bar
        self.progress_bar = RiskProgressBar()
        layout.addWidget(self.progress_bar)

        # Findings list (starts hidden)
        self.findings_widget = QWidget()
        self.findings_widget.setStyleSheet("background: transparent; border: none;")
        findings_layout = QVBoxLayout(self.findings_widget)
        findings_layout.setContentsMargins(0, 4, 0, 0)
        findings_layout.setSpacing(4)

        self.findings_container = QVBoxLayout()
        self.findings_container.setSpacing(4)
        findings_layout.addLayout(self.findings_container)

        layout.addWidget(self.findings_widget)
        self.findings_widget.hide()

    def set_result(self, score: int, risk_level: str, findings: list[str]):
        """Update card with dynamic score and findings."""
        self.score_badge.setText(str(score))

        risk_colors = {
            "CRITICAL": "#e87c8a",  # Red
            "HIGH": "#e87c8a",      # Red
            "MEDIUM": "#f0c878",    # Yellow
            "LOW": "#82d8ac",       # Green
        }
        color_hex = risk_colors.get(risk_level, "#9a9cb8")

        self.score_badge.setStyleSheet(f"""
            background-color: {color_hex};
            border: 2px solid {color_hex};
            border-radius: 22px;
            font-size: 14px;
            font-weight: 700;
            color: #FFFFFF;
        """)

        # Update progress bar
        self.progress_bar.set_value(min(score, 40), color_hex, animate=True)

        # Update findings
        while self.findings_container.count():
            item = self.findings_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if findings:
            self.findings_widget.show()
            for finding in findings:
                finding_lbl = QLabel(finding)
                finding_lbl.setWordWrap(True)
                finding_lbl.setStyleSheet("color: #9a9cb8; font-size: 12px; background: transparent; border: none; padding: 2px 0;")
                self.findings_container.addWidget(finding_lbl)
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
                background-color: #1a1b26;
                border: none;
                border-radius: 14px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        title = QLabel(title_text)
        title.setFont(QFont("Inter", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        layout.addWidget(title)

        question = "Are you sure you want to delete ALL contract analyses?" if is_clear_all else "Are you sure you want to delete this contract analysis?"
        question_label = QLabel(question)
        question_label.setWordWrap(True)
        question_label.setFont(QFont("Segoe UI", 12))
        question_label.setStyleSheet("color: #8B8FA8;")
        layout.addWidget(question_label)

        warning = "This action will permanently remove the saved analysis data. It cannot be undone."
        warning_label = QLabel(warning)
        warning_label.setWordWrap(True)
        warning_label.setFont(QFont("Segoe UI", 9))
        warning_label.setStyleSheet("color: #6B7280;")
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
                background-color: #2d2e42;
                color: #e2e4f0;
                border: 1px solid #454652;
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #383844;
            }
        """)
        self.no_btn.clicked.connect(self.reject)

        self.yes_btn = QPushButton("Yes, Delete")
        self.yes_btn.setCursor(Qt.PointingHandCursor)
        self.yes_btn.setFixedSize(110, 36)
        self.yes_btn.setStyleSheet("""
            QPushButton {
                background-color: #e87c8a;
                color: #3d0a12;
                border: none;
                border-radius: 10px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #ec8c98;
            }
            QPushButton:pressed {
                background-color: #d85c6b;
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
        self.setStyleSheet("QWidget#contracts_page { background-color: #12131d; }")
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
        scroll.setStyleSheet("""
            QScrollArea { background-color: #12131d; border: none; }
            QScrollBar:vertical {
                background-color: #12131d;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #333440;
                border-radius: 4px;
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #454652;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        content_widget = QWidget()
        content_widget.setObjectName("contracts_content")
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        content_widget.setStyleSheet("QWidget#contracts_content { background-color: #12131d; }")

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignTop)

        # 1. Header Section
        self.header = PageHeader(
            title="Contract Risk Analyzer",
            subtitle="AI-powered analysis of 55+ dangerous contract clauses",
        )
        badge = QLabel("🛡️ 5 CORE RISKS")
        badge.setStyleSheet(
            "background-color: #282935;"
            "color: #9a9cb8;"
            "border: 1px solid #383844;"
            "border-radius: 9999px;"
            "padding: 4px 14px;"
            "font-family: 'Inter';"
            "font-size: 11px;"
            "font-weight: 700;"
            "letter-spacing: 0.05em;"
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
        self.view_stack.setCurrentWidget(self.analyzer_view)  # Analyzer is the primary view

        scroll.setWidget(content_widget)
        page_layout.addWidget(scroll)

    def _build_history_view(self) -> None:
        self.history_view = QWidget()
        history_layout = QVBoxLayout(self.history_view)
        history_layout.setContentsMargins(0, 0, 0, 0)
        history_layout.setSpacing(24)

        # Search and Action Row
        search_row = QHBoxLayout()
        search_row.setSpacing(16)

        left_side = QHBoxLayout()
        left_side.setSpacing(12)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search contracts by project or text...")
        self.search_input.setFixedWidth(480)
        self.search_input.textChanged.connect(self._on_search)
        self.search_input.setFixedHeight(38)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1b26;
                border: 1px solid #333440;
                border-radius: 8px;
                padding: 8px 14px 8px 36px;
                color: #e2e4f0;
                font-family: 'Inter';
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #7c8af4;
                background-color: #1e1f2a;
            }
            QLineEdit::placeholder {
                color: #6b6d85;
            }
        """)

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
        self.filter_btn.setFixedHeight(38)
        filter_icon = _load_svg_icon("filter_list", size=16, color="#9a9cb8")
        self.filter_btn.setIcon(QIcon(filter_icon))
        self.filter_btn.clicked.connect(self._toggle_filter)

        self.filter_btn.setStyleSheet("""
            QPushButton#filter_btn {
                background-color: transparent;
                color: #9a9cb8;
                border: 1px solid #333440;
                border-radius: 8px;
                padding: 0px 16px;
                font-family: 'Inter';
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton#filter_btn:hover {
                border-color: #454652;
                color: #e2e4f0;
                background-color: #1a1b26;
            }
            QPushButton#filter_btn:checked {
                background-color: rgba(124, 138, 244, 0.10);
                color: #bcc2ff;
                border-color: #7c8af4;
            }
            QPushButton#filter_btn:pressed {
                background-color: rgba(124, 138, 244, 0.15);
            }
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
        self.clear_btn.setFixedHeight(38)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e87c8a;
                border: 1px solid rgba(232, 124, 138, 0.40);
                border-radius: 8px;
                padding: 0px 16px;
                font-family: 'Inter';
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(232, 124, 138, 0.10);
                border-color: #e87c8a;
            }
            QPushButton:pressed {
                background-color: rgba(232, 124, 138, 0.18);
            }
        """)
        self.clear_btn.clicked.connect(self._clear_all_analyses)
        right_side.addWidget(self.clear_btn)

        # "+ Analyze New" button
        self.add_btn = QPushButton("  Analyze Contract")
        self.add_btn.setObjectName("analyze_new_btn")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setFixedHeight(38)
        self.add_btn.setStyleSheet("""
            QPushButton#analyze_new_btn {
                background-color: #7c8af4;
                color: #061987;
                border-radius: 8px;
                padding: 0px 20px;
                font-family: 'Inter';
                font-weight: 700;
                font-size: 13px;
                border: none;
            }
            QPushButton#analyze_new_btn:hover {
                background-color: #8a96f6;
            }
            QPushButton#analyze_new_btn:pressed {
                background-color: #6d7be2;
            }
        """)
        add_icon = _load_svg_icon("add", size=16, color="#061987")
        self.add_btn.setIcon(QIcon(add_icon))
        self.add_btn.clicked.connect(self._show_analyzer_view)
        right_side.addWidget(self.add_btn)

        # Back to Analyzer button (from History view)
        self.back_to_analyzer_btn = QPushButton("  Back to Analyzer")
        self.back_to_analyzer_btn.setObjectName("back_to_analyzer_btn")
        self.back_to_analyzer_btn.setCursor(Qt.PointingHandCursor)
        self.back_to_analyzer_btn.setFixedHeight(38)
        self.back_to_analyzer_btn.setStyleSheet("""
            QPushButton#back_to_analyzer_btn {
                background-color: transparent;
                color: #9a9cb8;
                border: 1px solid #333440;
                border-radius: 8px;
                padding: 0px 16px;
                font-family: 'Inter';
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton#back_to_analyzer_btn:hover {
                color: #bcc2ff;
                border-color: #454652;
                background-color: #1a1b26;
            }
        """)
        back_icon = _load_svg_icon("chevron_left", size=16, color="#9a9cb8")
        self.back_to_analyzer_btn.setIcon(QIcon(back_icon))
        self.back_to_analyzer_btn.clicked.connect(self._show_analyzer_view)
        right_side.addWidget(self.back_to_analyzer_btn)

        search_row.addLayout(right_side)
        history_layout.addLayout(search_row)

        # Table Card QFrame
        self.table_card = QFrame()
        self.table_card.setObjectName("card")
        self.table_card.setStyleSheet("QFrame#card { background-color: #1a1b26; border: 1px solid #333440; border-radius: 14px; }")
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
        self.table.horizontalHeader().setVisible(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(52)  # Row height 52px
        self.table.setFrameShape(QFrame.NoFrame)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1b26;
                alternate-background-color: #1e1f2a;
                border: none;
                color: #e2e4f0;
                font-size: 13px;
                font-family: 'Inter';
                outline: none;
            }
            QHeaderView::section {
                background-color: #1a1b26;
                color: #9a9cb8;
                padding: 14px 24px;
                border: none;
                border-bottom: 1px solid #333440;
                font-family: 'Inter';
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            QHeaderView::section:first {
                border-top-left-radius: 14px;
            }
            QHeaderView::section:last {
                border-top-right-radius: 14px;
            }
            QTableWidget::item {
                border: none;
                padding: 10px 24px;
                border-bottom: 1px solid rgba(51, 52, 64, 0.60);
            }
            QTableWidget::item:selected {
                background-color: rgba(124, 138, 244, 0.12);
                border: none;
                color: #e2e4f0;
            }
            QTableWidget::item:hover {
                background-color: rgba(30, 31, 42, 0.80);
                border: none;
            }
            QScrollBar:vertical {
                background-color: #12131d;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #333440;
                border-radius: 4px;
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #454652;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #12131d;
                height: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:horizontal {
                background-color: #333440;
                border-radius: 4px;
                min-width: 24px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #454652;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                width: 0px;
            }
        """)

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
        self.footer_widget.setStyleSheet("QWidget#table_footer { background-color: #1e1f2a; border-top: 1px solid #333440; border-bottom-left-radius: 14px; border-bottom-right-radius: 14px; }")
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
                border-radius: 8px;
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
                border-radius: 8px;
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
                border-radius: 8px;
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

        # Back Row — now labeled "View History" since Analyzer is primary
        back_row = QHBoxLayout()
        back_row.setContentsMargins(0, 0, 0, 0)
        self.back_btn = QPushButton("  View History")
        self.back_btn.setObjectName("back_btn")
        self.back_btn.setCursor(Qt.PointingHandCursor)
        self.back_btn.clicked.connect(self._show_history_view)
        self.back_btn.setStyleSheet("""
            QPushButton#back_btn {
                background-color: transparent;
                color: #9a9cb8;
                font-family: 'Inter';
                font-size: 13px;
                font-weight: 500;
                border: 1px solid #333440;
                border-radius: 8px;
                padding: 6px 14px;
            }
            QPushButton#back_btn:hover {
                color: #bcc2ff;
                border-color: #454652;
                background-color: #1a1b26;
            }
            QPushButton#back_btn:pressed {
                background-color: #1e1f2a;
            }
        """)
        history_icon = _load_svg_icon("history", size=16, color="#9a9cb8")
        self.back_btn.setIcon(QIcon(history_icon))
        back_row.addWidget(self.back_btn)
        back_row.addStretch()
        analyzer_layout.addLayout(back_row)

        # Input Grid (Left: Upload PDF Card, Right: Parameters & Text Area)
        input_grid = QWidget()
        input_grid_layout = QHBoxLayout(input_grid)
        input_grid_layout.setContentsMargins(0, 0, 0, 0)
        input_grid_layout.setSpacing(24)

        # 1. Left Upload Card
        upload_card = QFrame()
        upload_card.setObjectName("glassCardUpload")
        upload_card.setStyleSheet("""
            QFrame#glassCardUpload {
                background-color: #222336;
                border: 1px solid #333440;
                border-radius: 14px;
            }
            QFrame#glassCardUpload:hover {
                background-color: #282935;
            }
        """)
        upload_card_layout = QVBoxLayout(upload_card)
        upload_card_layout.setContentsMargins(24, 24, 24, 24)
        upload_card_layout.setSpacing(16)

        upload_title = QLabel("📄 Contract Upload")
        upload_title.setStyleSheet("font-family: 'Inter'; font-size: 16px; font-weight: 700; color: #e2e4f0; background: transparent; border: none;")
        upload_card_layout.addWidget(upload_title)

        self.upload_area = UploadDashedArea()
        self.upload_area.file_dropped.connect(self._handle_file_drop)
        upload_card_layout.addWidget(self.upload_area, 1)

        self.file_label = QLabel("No file selected")
        self.file_label.setStyleSheet("color: #6b6d85; background: transparent; font-size: 13px; border: none;")
        upload_card_layout.addWidget(self.file_label, 0, Qt.AlignCenter)

        input_grid_layout.addWidget(upload_card, 1)

        # 2. Right Parameters Card
        params_card = QFrame()
        params_card.setObjectName("glassCardParams")
        params_card.setStyleSheet("""
            QFrame#glassCardParams {
                background-color: #222336;
                border: 1px solid #333440;
                border-radius: 14px;
            }
            QFrame#glassCardParams:hover {
                background-color: #282935;
            }
        """)
        params_card_layout = QVBoxLayout(params_card)
        params_card_layout.setContentsMargins(24, 24, 24, 24)
        params_card_layout.setSpacing(16)

        params_title = QLabel("⚙️ Project Details")
        params_title.setStyleSheet("font-family: 'Inter'; font-size: 16px; font-weight: 700; color: #e2e4f0; background: transparent; border: none;")
        params_card_layout.addWidget(params_title)

        # Form fields Grid layout
        form_layout = QGridLayout()
        form_layout.setSpacing(12)
        form_layout.setColumnStretch(1, 1)
        form_layout.setColumnStretch(3, 1)

        # Labels
        lbl_project = QLabel("PROJECT:")
        lbl_rate = QLabel("HOURLY RATE (₹):")
        lbl_revisions = QLabel("REVISIONS:")
        lbl_timeline = QLabel("TIMELINE:")
        lbl_type = QLabel("TYPE:")
        for lbl in (lbl_project, lbl_rate, lbl_revisions, lbl_timeline, lbl_type):
            lbl.setStyleSheet("color: #6b6d85; font-family: 'Inter'; font-size: 11px; font-weight: 700; letter-spacing: 0.05em; background: transparent; border: none;")

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

        # Style inputs
        input_style = """
            QComboBox, QAbstractSpinBox {
                background-color: #1a1b26;
                border: 1px solid #333440;
                border-radius: 6px;
                padding: 6px 12px;
                color: #e2e4f0;
                font-family: 'Inter';
                font-size: 13px;
                selection-background-color: rgba(124, 138, 244, 0.20);
            }
            QComboBox:hover, QAbstractSpinBox:hover {
                border-color: #454652;
            }
            QComboBox:focus, QAbstractSpinBox:focus {
                border-color: #7c8af4;
                background-color: #1e1f2a;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 8px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #6b6d85;
                margin-right: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1f2a;
                border: 1px solid #333440;
                border-radius: 6px;
                color: #e2e4f0;
                selection-background-color: rgba(124, 138, 244, 0.20);
                outline: none;
            }
            QAbstractSpinBox::up-button,
            QAbstractSpinBox::down-button {
                background-color: transparent;
                border: none;
                width: 16px;
            }
            QAbstractSpinBox::up-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid #6b6d85;
            }
            QAbstractSpinBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #6b6d85;
            }
        """
        for widget in (self.project_combo, self.rate_input, self.revisions_input, self.timeline_input, self.type_combo):
            widget.setStyleSheet(input_style)

        form_layout.addWidget(lbl_project, 0, 0)
        form_layout.addWidget(self.project_combo, 0, 1)
        form_layout.addWidget(lbl_rate, 0, 2)
        form_layout.addWidget(self.rate_input, 0, 3)

        form_layout.addWidget(lbl_revisions, 1, 0)
        form_layout.addWidget(self.revisions_input, 1, 1)
        form_layout.addWidget(lbl_timeline, 1, 2)
        form_layout.addWidget(self.timeline_input, 1, 3)

        form_layout.addWidget(lbl_type, 2, 0)
        form_layout.addWidget(self.type_combo, 2, 1, 1, 3)

        params_card_layout.addLayout(form_layout)

        # Text area label
        lbl_text = QLabel("PASTE CONTRACT TEXT")
        lbl_text.setStyleSheet("color: #6b6d85; font-family: 'Inter'; font-size: 11px; font-weight: 700; background: transparent; border: none; letter-spacing: 0.05em;")
        params_card_layout.addWidget(lbl_text)

        self.contract_text = QTextEdit()
        self.contract_text.setPlaceholderText("Paste contract text here...")
        self.contract_text.setMinimumHeight(120)
        self.contract_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1b26;
                border: 1px solid #333440;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e2e4f0;
                font-family: 'Inter';
                font-size: 13px;
            }
            QTextEdit:focus {
                border-color: #7c8af4;
                background-color: #1e1f2a;
            }
            QTextEdit:hover {
                border-color: #454652;
            }
        """)
        params_card_layout.addWidget(self.contract_text)

        # Analyze button
        self.analyze_btn = QPushButton("🔍  Analyze Contract")
        self.analyze_btn.setCursor(Qt.PointingHandCursor)
        self.analyze_btn.setFixedHeight(44)
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: #7c8af4;
                color: #061987;
                border: none;
                border-radius: 10px;
                font-family: 'Inter';
                font-size: 14px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #8a96f6;
            }
            QPushButton:pressed {
                background-color: #6d7be2;
            }
        """)
        self.analyze_btn.clicked.connect(lambda: self._analyze(save_db=True))
        params_card_layout.addWidget(self.analyze_btn)

        input_grid_layout.addWidget(params_card, 1.2)
        analyzer_layout.addWidget(input_grid)

        # Results Container (starts hidden)
        self.results_container = QWidget()
        self.results_container.setStyleSheet("background: transparent; border: none;")
        results_layout = QVBoxLayout(self.results_container)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(24)

        # Overall Assessment Card
        self.overall_card = QFrame()
        self.overall_card.setObjectName("overallCard")
        self.overall_card.setStyleSheet("""
            QFrame#overallCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #222336, stop:0.6 #1e1f2a, stop:1 #1a1b26);
                border: 1px solid #333440;
                border-radius: 14px;
            }
        """)
        overall_layout = QHBoxLayout(self.overall_card)
        overall_layout.setContentsMargins(28, 24, 28, 24)
        overall_layout.setSpacing(24)

        # Left: Circular progress score ring
        self.circular_score = CircularRiskScore()
        overall_layout.addWidget(self.circular_score)

        # Right: Risk level and recommendation details
        risk_info = QWidget()
        risk_info.setStyleSheet("background: transparent; border: none;")
        risk_info_layout = QVBoxLayout(risk_info)
        risk_info_layout.setContentsMargins(0, 0, 0, 0)
        risk_info_layout.setSpacing(8)

        self.risk_level_label = QLabel("Risk Level: Not Analyzed")
        self.risk_level_label.setStyleSheet("font-family: 'Inter'; font-size: 22px; font-weight: 700; color: #e2e4f0; background: transparent; border: none; letter-spacing: -0.01em;")
        risk_info_layout.addWidget(self.risk_level_label)

        self.recommendation_label = QLabel("Upload a contract to begin analysis")
        self.recommendation_label.setWordWrap(True)
        self.recommendation_label.setStyleSheet("font-family: 'Inter'; font-size: 13px; color: #9a9cb8; background: transparent; border: none;")
        risk_info_layout.addWidget(self.recommendation_label)

        # Sliding white indicator line on multi-colored progress bar
        self.multi_progress = MultiColorGradientBar()
        risk_info_layout.addWidget(self.multi_progress)

        # Legend row
        legend_row = QHBoxLayout()
        legend_row.setSpacing(16)
        
        def make_legend_item(text, color):
            item = QWidget()
            item.setStyleSheet("background: transparent; border: none;")
            item_layout = QHBoxLayout(item)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(6)
            
            dot = QLabel()
            dot.setFixedSize(8, 8)
            dot.setStyleSheet(f"background-color: {color}; border-radius: 4px; border: none;")
            item_layout.addWidget(dot)
            
            label = QLabel(text)
            label.setStyleSheet("color: #6b6d85; font-size: 11px; font-weight: 500; background: transparent; border: none;")
            item_layout.addWidget(label)
            return item

        legend_row.addWidget(make_legend_item("LOW RISK", "#82d8ac"))
        legend_row.addWidget(make_legend_item("MEDIUM", "#7c8af4"))
        legend_row.addWidget(make_legend_item("CRITICAL", "#e87c8a"))
        legend_row.addStretch()
        risk_info_layout.addLayout(legend_row)

        overall_layout.addWidget(risk_info, 1)
        results_layout.addWidget(self.overall_card)

        # 5 Critical Areas Grid
        self.criteria_title = QLabel("🎯  5 Critical Risk Areas")
        self.criteria_title.setStyleSheet("font-family: 'Inter'; font-size: 18px; font-weight: 700; color: #e2e4f0; background: transparent; border: none; letter-spacing: -0.01em;")
        results_layout.addWidget(self.criteria_title)

        criteria_grid = QGridLayout()
        criteria_grid.setSpacing(20)

        criteria_defs = [
            ("ip_transfer", "🎨", "Intellectual Property", "Loss of ownership rights"),
            ("payment_terms", "💰", "Payment Terms", "Extended payment delays"),
            ("revision_scope", "🔄", "Scope Creep Control", "Unlimited work requirements"),
            ("termination", "🚫", "Termination Rights", "Cancellation without payment"),
            ("indemnity", "🛡️", "Liability Caps", "Unlimited liability exposure"),
        ]

        for idx, (key, icon, title, desc) in enumerate(criteria_defs):
            card = RiskCriteriaCard(title, icon, desc)
            self.risk_cards[key] = card
            row = idx // 2
            col = idx % 2
            if idx == 4:
                # Span 5th card across both columns
                criteria_grid.addWidget(card, row, col, 1, 2)
            else:
                criteria_grid.addWidget(card, row, col)

        results_layout.addLayout(criteria_grid)

        # Detailed Findings Table Card
        self.findings_title = QLabel("📋  Detailed Findings")
        self.findings_title.setStyleSheet("font-family: 'Inter'; font-size: 18px; font-weight: 700; color: #e2e4f0; background: transparent; border: none; letter-spacing: -0.01em;")
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
                background-color: #1a1b26;
                alternate-background-color: #1e1f2a;
                border: 1px solid #333440;
                border-radius: 14px;
                gridline-color: transparent;
                color: #e2e4f0;
                font-family: 'Inter';
                font-size: 13px;
                outline: none;
            }
            QTableWidget::item {
                border-bottom: 1px solid rgba(51, 52, 64, 0.60);
                padding: 10px 16px;
            }
            QTableWidget::item:selected {
                background-color: rgba(124, 138, 244, 0.12);
                color: #e2e4f0;
            }
            QHeaderView::section {
                background-color: #1a1b26;
                color: #9a9cb8;
                font-family: 'Inter';
                font-size: 11px;
                font-weight: 700;
                letter-spacing: 0.05em;
                text-transform: uppercase;
                border: none;
                border-bottom: 1px solid #333440;
                padding: 10px 16px;
            }
            QScrollBar:vertical {
                background-color: #12131d;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #333440;
                border-radius: 4px;
                min-height: 24px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #454652;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        results_layout.addWidget(self.findings_table)

        # Action Buttons at the bottom
        actions_row = QHBoxLayout()
        actions_row.setSpacing(12)

        self.export_btn = QPushButton("Export PDF")
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setFixedHeight(40)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e2e4f0;
                border: 1px solid #333440;
                border-radius: 10px;
                font-family: 'Inter';
                font-weight: 600;
                font-size: 13px;
                padding: 0px 20px;
            }
            QPushButton:hover {
                background-color: #1a1b26;
                border-color: #454652;
                color: #bcc2ff;
            }
            QPushButton:pressed {
                background-color: #1e1f2a;
            }
        """)

        self.share_btn = QPushButton("Share with Client")
        self.share_btn.setCursor(Qt.PointingHandCursor)
        self.share_btn.setFixedHeight(40)
        self.share_btn.setStyleSheet("""
            QPushButton {
                background-color: #7c8af4;
                color: #061987;
                border: none;
                border-radius: 10px;
                font-family: 'Inter';
                font-weight: 700;
                font-size: 13px;
                padding: 0px 20px;
            }
            QPushButton:hover {
                background-color: #8a96f6;
            }
            QPushButton:pressed {
                background-color: #6d7be2;
            }
        """)

        actions_row.addWidget(self.export_btn)
        actions_row.addWidget(self.share_btn)
        results_layout.addLayout(actions_row)

        analyzer_layout.addWidget(self.results_container)
        self.results_container.hide()

    def eventFilter(self, obj, event) -> bool:
        """Handle hover events for custom buttons."""
        from PySide6.QtCore import QEvent
        if obj == self.filter_btn:
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
        """Reload project dropdowns, retrieve contracts from DB, and populate table."""
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

        # Re-apply filter rules & search
        self._on_search(self.search_input.text())

    def _show_history_view(self) -> None:
        self.view_stack.setCurrentWidget(self.history_view)
        self.refresh()

    def _show_analyzer_view(self) -> None:
        # Only reset inputs if switching FROM history, not if already on analyzer
        if self.view_stack.currentWidget() != self.analyzer_view:
            self.contract_text.clear()
            self.file_label.setText("No file selected")
            self.file_label.setStyleSheet("color: #6b6d85; background: transparent; font-size: 13px; border: none;")
            self.project_combo.setCurrentIndex(0)
            self.rate_input.setValue(500)
            self.revisions_input.setValue(2)
            self.timeline_input.setValue(14)
            self.type_combo.setCurrentIndex(0)
            self.results_container.hide()
        self.view_stack.setCurrentWidget(self.analyzer_view)

    def _toggle_filter(self) -> None:
        pass

    def _upload_pdf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Contract PDF", "", "PDF Files (*.pdf)")
        if not path:
            return
        self._handle_file_drop(path)

    def _handle_file_drop(self, filepath: str) -> None:
        if not filepath:
            filepath, _ = QFileDialog.getOpenFileName(self, "Select Contract PDF", "", "PDF Files (*.pdf)")
            if not filepath:
                return

        filename = filepath.replace("\\", "/").split("/")[-1]
        self.file_label.setText(f"✅ {filename}")
        self.file_label.setStyleSheet(
            "color: #82d8ac; background: transparent; font-size: 13px; font-weight: 600; border: none;"
        )
        try:
            text = self.contract_parser.extract_text(filepath)
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

        level_colors = {
            "LOW": "#82d8ac",       # Green
            "MEDIUM": "#7c8af4",    # Lavender
            "HIGH": "#e87c8a",      # Red
            "CRITICAL": "#e87c8a",  # Red
        }
        color_hex = level_colors.get(level, "#9a9cb8")

        self.circular_score.set_score(total_score, color_hex)
        self.multi_progress.set_score(total_score, animate=True)

        self.risk_level_label.setText(f"Risk Level: {level}")
        self.risk_level_label.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {color_hex}; background: transparent; border: none; letter-spacing: -0.01em;")

        recommendations = {
            "LOW": "✅ Acceptable risk - proceed with standard caution",
            "MEDIUM": "⚠️ Review carefully and negotiate weak points",
            "HIGH": "🚨 Serious concerns - negotiate heavily or walk away",
            "CRITICAL": "❌ DO NOT SIGN - extremely dangerous contract",
        }
        self.recommendation_label.setText(recommendations.get(level, ""))

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
                score_item.setForeground(QColor("#e87c8a"))
            elif f["score"] >= 15:
                score_item.setForeground(QColor("#f0c878"))
            elif f["score"] >= 8:
                score_item.setForeground(QColor("#7c8af4"))
            else:
                score_item.setForeground(QColor("#82d8ac"))
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
            empty_label.setStyleSheet("color: #6b6d85; font-size: 13px; background: transparent; border: none;")
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
                name_lbl.setStyleSheet(f"font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent; border: none;")
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
                if level in ("CRITICAL", "HIGH"):
                    text_color = "#e87c8a"
                    bg_color = "rgba(232, 124, 138, 0.20)"
                elif level == "MEDIUM":
                    text_color = "#f0c878"
                    bg_color = "rgba(240, 200, 120, 0.10)"
                elif level == "LOW":
                    text_color = "#82d8ac"
                    bg_color = "rgba(0, 106, 71, 0.20)"
                else:
                    text_color = "#9a9cb8"
                    bg_color = "rgba(154, 156, 184, 0.12)"

                pill = StatusPill(level, color=text_color, bg_color=bg_color)
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

        _action_btn_style = """
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(188, 194, 255, 0.08);
                border: 1px solid #454652;
            }
            QPushButton:pressed {
                background-color: rgba(124, 138, 244, 0.15);
            }
        """

        view_btn = QPushButton()
        view_btn.setObjectName("table_action_icon_btn")
        view_btn.setCursor(Qt.PointingHandCursor)
        view_btn.setToolTip("View Analysis")
        view_btn.setFixedSize(32, 32)
        view_btn.setIcon(QIcon(_load_svg_icon("edit", size=18, color="#bcc2ff")))
        view_btn.setIconSize(QSize(18, 18))
        view_btn.setStyleSheet(_action_btn_style)
        view_btn.clicked.connect(lambda: self._view_analysis(contract_id))

        del_btn = QPushButton()
        del_btn.setObjectName("table_action_icon_btn_danger")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Delete Analysis")
        del_btn.setFixedSize(32, 32)
        del_btn.setIcon(QIcon(_load_svg_icon("delete", size=18, color="#e87c8a")))
        del_btn.setIconSize(QSize(18, 18))
        del_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: rgba(232, 124, 138, 0.12);
                border: 1px solid rgba(232, 124, 138, 0.30);
            }
            QPushButton:pressed {
                background-color: rgba(232, 124, 138, 0.20);
            }
        """)
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
                        border-radius: 8px;
                        font-weight: 700;
                        font-size: 13px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: transparent;
                        border: 1px solid #2d2e42;
                        border-radius: 8px;
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
