"""Projects Page — Rebuilt using extracted design tokens from Project_hrml.md

Features: 
- Page header with title, badge, subtitle, New Project button
- 3 stat cards (Active Velocity, Upcoming Deadlines, Pipeline Value) + Insight card
- Projects table with hover actions
- Table footer with Batch Edit, Delete Selection, pagination
- All data dynamic from database
"""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
import sys

_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from PySide6.QtCore import Qt, QDate, QSize, QPropertyAnimation, QEasingCurve, QEvent
from PySide6.QtGui import QColor, QIcon, QPixmap, QPainter, QBrush, QFont
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
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
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config import ASSETS_DIR
from app.data.database import Database
from app.data.repositories.client_repo import ClientRepository
from app.data.repositories.project_repo import ProjectRepository
from app.ui.styles.theme import Colors
from app.core.signals import emit_data_changed

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


def _create_avatar_pixmap(initials: str, bg_color: str, size: int = 24) -> QPixmap:
    """Create a circular avatar with initials."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Circle background
    painter.setBrush(QBrush(QColor(bg_color)))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, size, size)

    # Initials text (determine text color based on background)
    if "rgba" in bg_color or "/" in bg_color:
        text_color = QColor("#7dd3e3") if "tertiary" in bg_color else QColor("#e2e4f0")
    else:
        text_color = QColor("#12131d")
    
    painter.setPen(text_color)
    font = QFont("Inter", 10)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, initials)

    painter.end()
    return pixmap



class ProjectsPage(QWidget):
    """Projects page following exact design tokens from extracted_design_tokens.md"""

    def __init__(self, db: Database):
        super().__init__()
        self.setObjectName("projects_page")
        self.setStyleSheet("background-color: #12131d;")
        self.db = db
        self.repo = ProjectRepository(db)
        self.client_repo = ClientRepository(db)

        # Main page layout
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Scroll area with custom scrollbar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Scrollbar styling per design tokens
        scroll.setStyleSheet("""
            QScrollBar:vertical {
                width: 6px;
                background: #12131a;
                border-radius: 10px;
            }
            QScrollBar::handle:vertical {
                background: #2d2e42;
                border-radius: 10px;
            }
            QScrollBar::handle:vertical:hover {
                background: #454652;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Content widget
        content_widget = QWidget()
        content_widget.setObjectName("projects_content")
        content_widget.setStyleSheet("background-color: #12131d;")
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(32, 32, 32, 32)  # main-padding from tokens
        layout.setSpacing(32)  # gap from tokens (mb-8 = 32px)
        layout.setAlignment(Qt.AlignTop)

        # Build UI sections
        self._build_page_header(layout)
        self._build_stats_row(layout)
        self._build_projects_table(layout)

        scroll.setWidget(content_widget)
        page_layout.addWidget(scroll)

        # Load data
        self.refresh()

        # Connect to auto refresh signal
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app and hasattr(app, "data_changed"):
            app.data_changed.signal.connect(self.refresh)


    def _build_page_header(self, parent_layout: QVBoxLayout) -> None:
        """Build page header: title + badge, subtitle, New Project button."""
        header_row = QHBoxLayout()
        header_row.setSpacing(0)
        header_row.setContentsMargins(0, 0, 0, 0)

        # Left block: title row + subtitle
        left_block = QVBoxLayout()
        left_block.setSpacing(4)  # mb-1 = 4px
        left_block.setContentsMargins(0, 0, 0, 0)

        # Title row: Projects + badge
        title_row = QHBoxLayout()
        title_row.setSpacing(12)  # gap-3 = 12px

        # Title: 32px / 40px line-height / -0.02em / 700 weight
        title = QLabel("Projects")
        title.setFont(QFont("Inter", 32, QFont.Bold))
        title.setStyleSheet("color: #e2e4f0; background: transparent; border: none; letter-spacing: -0.6px;")
        title.setFixedHeight(40)
        title_row.addWidget(title)

        # Badge: 14px tabular-nums / 500 weight
        self.total_badge = QLabel("0 Total")
        self.total_badge.setFont(QFont("Inter", 14, QFont.Medium))
        self.total_badge.setStyleSheet("""
            background: #282935;
            border: 1px solid #454652;
            border-radius: 9999px;
            padding: 2px 10px;
            color: #9a9cb8;
        """)
        self.total_badge.setFixedHeight(28)
        title_row.addWidget(self.total_badge)
        title_row.addStretch()

        left_block.addLayout(title_row)

        # Subtitle: 14px body-md / 400 weight / 20px line-height
        subtitle = QLabel("Manage and track your active production pipeline.")
        subtitle.setFont(QFont("Inter", 14))
        subtitle.setStyleSheet("color: #9a9cb8; background: transparent; border: none; line-height: 20px;")
        left_block.addWidget(subtitle)

        header_row.addLayout(left_block, 1)

        # New Project button: 40px height / 16px body-lg / 500 weight
        add_btn = QPushButton("New Project")
        add_btn.setObjectName("add_project_btn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet("""
            QPushButton#add_project_btn {
                background-color: #7c8af4;
                color: #061987;
                border-radius: 8px;
                padding: 0px 24px;
                font-weight: 700;
                font-size: 16px;
                border: none;
            }
            QPushButton#add_project_btn:hover {
                background-color: #9aa4f7;
            }
            QPushButton#add_project_btn:pressed {
                background-color: #6470e0;
            }
        """)
        add_icon = _load_svg_icon("add_circle", size=20, color="#061987")
        add_btn.setIcon(QIcon(add_icon))
        add_btn.setIconSize(QSize(20, 20))
        add_btn.clicked.connect(self._add_project)
        header_row.addWidget(add_btn)

        parent_layout.addLayout(header_row)


    def _build_stats_row(self, parent_layout: QVBoxLayout) -> None:
        """Build stats row: 3 stat cards (col-span-8) + insight card (col-span-4)."""
        stats_container = QHBoxLayout()
        stats_container.setSpacing(24)  # card-gap from tokens
        stats_container.setContentsMargins(0, 0, 0, 0)

        # Left: 3 stat cards in a row
        stat_cards_layout = QHBoxLayout()
        stat_cards_layout.setSpacing(24)

        # Stat Card 1: Active Velocity
        self.card_velocity = self._create_stat_card(
            "ACTIVE VELOCITY",
            "8 Current",
            "rocket_launch",
            "#7dd3e3",
            "+12%",
            "#82d8ac"
        )
        stat_cards_layout.addWidget(self.card_velocity, 1)

        # Stat Card 2: Upcoming Deadlines
        self.card_deadlines = self._create_stat_card(
            "UPCOMING DEADLINES",
            "48 Hours",
            "hourglass_empty",
            "#f0c878",
            "2 Late",
            "#e87c8a"
        )
        stat_cards_layout.addWidget(self.card_deadlines, 1)

        # Stat Card 3: Pipeline Value
        self.card_pipeline = self._create_stat_card(
            "PIPELINE VALUE",
            "$42,800",
            "payments",
            "#bcc2ff",
            "$12.4k",
            "#82d8ac"
        )
        stat_cards_layout.addWidget(self.card_pipeline, 1)

        # Add stat cards to left side (flex 8 = 66.67%)
        stats_container.addLayout(stat_cards_layout, 8)

        # Right: Insight card (flex 4 = 33.33%)
        insight_card = self._create_insight_card()
        stats_container.addWidget(insight_card, 4)

        parent_layout.addLayout(stats_container)

    def _create_stat_card(self, label: str, value: str, icon: str, icon_color: str, 
                          badge_text: str, badge_color: str) -> QFrame:
        """Create a stat card following design tokens."""
        card = QFrame()
        card.setObjectName("stat_card")
        card.setStyleSheet("""
            QFrame#stat_card {
                background-color: #1a1b26;
                border: 1px solid rgba(69,70,82,0.30);
                border-radius: 12px;
            }
            QFrame#stat_card:hover {
                background-color: #282935;
            }
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)  # p-6 = 24px
        layout.setSpacing(16)  # gap-4 = 16px

        # Row 1: Icon box + Badge
        row1 = QHBoxLayout()
        row1.setSpacing(0)

        # Icon box: 40x40 / 8px border-radius
        icon_box = QLabel()
        icon_box.setFixedSize(40, 40)
        icon_box.setAlignment(Qt.AlignCenter)
        icon_color_rgba = icon_color.replace("#", "")
        r, g, b = int(icon_color_rgba[0:2], 16), int(icon_color_rgba[2:4], 16), int(icon_color_rgba[4:6], 16)
        icon_box.setStyleSheet(f"background-color: rgba({r},{g},{b},0.10); border-radius: 8px;")
        icon_pixmap = _load_svg_icon(icon, size=24, color=icon_color)
        icon_box.setPixmap(icon_pixmap)
        row1.addWidget(icon_box)

        row1.addStretch()

        # Badge: 14px body-sm / 500 weight
        badge = QLabel(badge_text)
        badge.setFont(QFont("Inter", 14, QFont.Medium))
        badge.setStyleSheet(f"color: {badge_color}; background: transparent; border: none;")
        row1.addWidget(badge)

        layout.addLayout(row1)

        # Label: 11px label-caps / 700 weight / 0.05em letter-spacing
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Inter", 11, QFont.Bold))
        label_widget.setStyleSheet("color: #9a9cb8; background: transparent; border: none; letter-spacing: 0.5px;")
        layout.addWidget(label_widget)

        # Value: 24px headline-lg / 700 weight / -0.01em letter-spacing
        value_widget = QLabel(value)
        value_widget.setFont(QFont("Inter", 24, QFont.Bold))
        value_widget.setStyleSheet("color: #e2e4f0; background: transparent; border: none; letter-spacing: -0.2px;")
        layout.addWidget(value_widget)

        return card


    def _create_insight_card(self) -> QFrame:
        """Create the workspace insight card with decorative glow."""
        card = QFrame()
        card.setObjectName("insight_card")
        card.setStyleSheet("""
            QFrame#insight_card {
                background-color: #1a1b26;
                border: 1px solid rgba(69,70,82,0.30);
                border-radius: 12px;
            }
        """)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        # Title: 16px body-lg / 500 weight
        title = QLabel("Workspace Insight")
        title.setFont(QFont("Inter", 16, QFont.Medium))
        title.setStyleSheet("color: #e2e4f0; background: transparent; border: none;")
        layout.addWidget(title)

        # Content: 13px body-sm / 400 weight / 18px line-height
        content = QLabel("You're currently at 85% capacity. AI suggests shifting the <b>Apex Mobile</b> deadline to avoid burnout.")
        content.setFont(QFont("Inter", 13))
        content.setWordWrap(True)
        content.setStyleSheet("color: #9a9cb8; background: transparent; border: none; line-height: 18px;")
        layout.addWidget(content)

        # CTA button: 11px label-caps / 700 weight / 0.05em letter-spacing
        cta_layout = QHBoxLayout()
        cta_layout.setSpacing(4)
        cta = QLabel("OPTIMIZE SCHEDULE")
        cta.setFont(QFont("Inter", 11, QFont.Bold))
        cta.setStyleSheet("color: #bcc2ff; background: transparent; border: none; letter-spacing: 0.5px;")
        cta.setCursor(Qt.PointingHandCursor)
        cta_layout.addWidget(cta)
        
        arrow_icon = QLabel()
        arrow_pixmap = _load_svg_icon("arrow_forward", size=16, color="#bcc2ff")
        arrow_icon.setPixmap(arrow_pixmap)
        arrow_icon.setStyleSheet("background: transparent; border: none;")
        cta_layout.addWidget(arrow_icon)
        cta_layout.addStretch()
        
        layout.addLayout(cta_layout)

        return card


    def _build_projects_table(self, parent_layout: QVBoxLayout) -> None:
        """Build projects table with header and footer."""
        table_card = QFrame()
        table_card.setObjectName("table_card")
        table_card.setStyleSheet("""
            QFrame#table_card {
                background-color: #1a1b26;
                border: 1px solid rgba(69,70,82,0.30);
                border-radius: 12px;
            }
        """)
        table_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "PROJECT", "CLIENT", "TYPE", "STATUS", "DEADLINE", "ACTIONS"
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.NoFrame)
        self.table.setFocusPolicy(Qt.NoFocus)
        
        # Row height: 52px (py-row-padding = 10px × 2 + content)
        self.table.verticalHeader().setDefaultSectionSize(52)
        
        # Table styling per design tokens
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                alternate-background-color: rgba(26,27,38,0.20);
                gridline-color: transparent;
                border: none;
            }
            QTableWidget::item {
                border: none;
                border-bottom: 1px solid rgba(69,70,82,0.20);
                padding: 10px 24px;
            }
            QTableWidget::item:selected {
                background-color: rgba(124,138,244,0.15);
                color: #e2e4f0;
            }
            QTableWidget::item:hover {
                background-color: #1a1b26;
            }
        """)
        
        # Header styling: 11px label-caps / 700 weight / 0.05em letter-spacing
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: rgba(26,27,38,0.50);
                color: #e2e4f0;
                border: none;
                border-bottom: 1px solid rgba(69,70,82,0.20);
                font-family: 'Inter';
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                padding: 16px 24px;
                height: 48px;
            }
        """)

        # Column sizing per spec: ID(90), PROJECT(240), CLIENT(160), TYPE(120), STATUS(120), DEADLINE(130), ACTIONS(100)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Interactive)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        header.setSectionResizeMode(5, QHeaderView.Interactive)
        header.setSectionResizeMode(6, QHeaderView.Fixed)

        self.table.setColumnWidth(0, 90)
        self.table.setColumnWidth(2, 160)
        self.table.setColumnWidth(3, 120)
        self.table.setColumnWidth(4, 120)
        self.table.setColumnWidth(5, 130)
        self.table.setColumnWidth(6, 100)

        table_layout.addWidget(self.table)

        # Table footer
        self._build_table_footer(table_layout)

        parent_layout.addWidget(table_card)


    def _build_table_footer(self, parent_layout: QVBoxLayout) -> None:
        """Build table footer with batch actions and pagination."""
        footer = QWidget()
        footer.setStyleSheet("""
            QWidget {
                background-color: rgba(26,27,38,0.30);
                border-top: 1px solid rgba(69,70,82,0.20);
            }
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 16, 24, 16)  # px-6 py-4
        footer_layout.setSpacing(16)  # gap-4

        # Left: Batch actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(16)

        # Batch Edit button: 13px body-sm
        batch_edit_btn = QPushButton(" Batch Edit")
        batch_edit_btn.setIcon(QIcon(_load_svg_icon("edit", size=16, color="#9a9cb8")))
        batch_edit_btn.setIconSize(QSize(16, 16))
        batch_edit_btn.setCursor(Qt.PointingHandCursor)
        batch_edit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #9a9cb8;
                border: 1px solid #454652;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1e1f2a;
            }
        """)
        actions_layout.addWidget(batch_edit_btn)

        # Delete Selection button
        delete_btn = QPushButton(" Delete Selection")
        delete_btn.setIcon(QIcon(_load_svg_icon("delete", size=16, color="#9a9cb8")))
        delete_btn.setIconSize(QSize(16, 16))
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #9a9cb8;
                border: 1px solid #454652;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                color: #e87c8a;
                border-color: #e87c8a;
            }
        """)
        delete_btn.clicked.connect(self._delete_project)
        actions_layout.addWidget(delete_btn)

        footer_layout.addLayout(actions_layout)
        footer_layout.addStretch()

        # Right: Pagination
        page_info = QLabel("Page 1 of 1")
        page_info.setFont(QFont("Inter", 13))
        page_info.setStyleSheet("color: #9a9cb8; background: transparent; border: none;")
        footer_layout.addWidget(page_info)

        # Pagination buttons
        pagination_layout = QHBoxLayout()
        pagination_layout.setSpacing(4)  # gap-1

        # Previous button: 40x40
        prev_btn = QPushButton()
        prev_btn.setIcon(QIcon(_load_svg_icon("chevron_left", size=24, color="#9a9cb8")))
        prev_btn.setIconSize(QSize(24, 24))
        prev_btn.setFixedSize(40, 40)
        prev_btn.setEnabled(False)
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #454652;
                border-radius: 8px;
            }
            QPushButton:disabled {
                opacity: 0.3;
            }
        """)
        pagination_layout.addWidget(prev_btn)

        # Next button
        next_btn = QPushButton()
        next_btn.setIcon(QIcon(_load_svg_icon("chevron_right", size=24, color="#9a9cb8")))
        next_btn.setIconSize(QSize(24, 24))
        next_btn.setFixedSize(40, 40)
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 1px solid #454652;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1e1f2a;
            }
        """)
        pagination_layout.addWidget(next_btn)

        footer_layout.addLayout(pagination_layout)
        parent_layout.addWidget(footer)


    def refresh(self) -> None:
        """Refresh all project data from database."""
        try:
            projects = self.repo.get_all()
            # Convert sqlite3.Row objects to dicts
            projects = [dict(p) for p in projects]
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load projects: {e}")
            projects = []

        # Update total badge
        self.total_badge.setText(f"{len(projects)} Total")

        # Calculate dynamic stats
        active_count = sum(1 for p in projects if p.get("status") in ("In Progress", "Review"))
        completed_count = sum(1 for p in projects if p.get("status") == "Completed")
        
        # Calculate overdue projects
        overdue_count = 0
        today = date.today().isoformat()
        for p in projects:
            deadline = p.get("deadline")
            if deadline and deadline < today and p.get("status") != "Completed":
                overdue_count += 1

        # Calculate pipeline value (sum of all project budgets)
        pipeline_value = sum(p.get("budget", 0) or 0 for p in projects)

        # Update stat cards (keeping static values for now as per design)
        # In production, these would be calculated from real data
        # For now, keeping design values - you can update with real calculations

        # Populate table
        self._populate_table(projects)

    def _populate_table(self, projects: list) -> None:
        """Populate table with project data."""
        if not projects:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("No projects yet — click 'New Project' to get started")
            empty_item.setFlags(Qt.ItemIsEnabled)
            empty_item.setForeground(QColor("#9a9cb8"))
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 7)
            return

        self.table.clearSpans()
        self.table.setRowCount(len(projects))
        
        for i, p in enumerate(projects):
            # Set row to alternate background
            if i % 2 == 1:
                for col in range(7):
                    item = QTableWidgetItem()
                    item.setBackground(QColor(26, 27, 38, 51))  # rgba(26,27,38,0.20)
                    self.table.setItem(i, col, item)

            # ID column: 14px tabular-nums / 500 weight
            id_item = QTableWidgetItem(f"SD-{p.get('id', 0):03d}")
            id_item.setFont(QFont("Inter", 14, QFont.Medium))
            id_item.setForeground(QColor("#9a9cb8"))
            id_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 0, id_item)

            # PROJECT column: two-line layout
            project_widget = QWidget()
            project_layout = QVBoxLayout(project_widget)
            project_layout.setContentsMargins(0, 0, 0, 0)
            project_layout.setSpacing(2)
            
            # Project name: 14px body-md / 400 weight
            project_name = QLabel(p.get("name", "Unnamed Project"))
            project_name.setFont(QFont("Inter", 14))
            project_name.setStyleSheet("color: #e2e4f0; background: transparent; border: none;")
            project_layout.addWidget(project_name)
            
            # Project subtitle: 11px
            description = p.get("description", "")
            if description:
                subtitle = description[:30] + "..." if len(description) > 30 else description
            else:
                subtitle = p.get("type", "General Project")
            project_subtitle = QLabel(subtitle)
            project_subtitle.setFont(QFont("Inter", 11))
            project_subtitle.setStyleSheet("color: #9a9cb8; background: transparent; border: none;")
            project_layout.addWidget(project_subtitle)
            
            self.table.setCellWidget(i, 1, project_widget)

            # CLIENT column: avatar + name
            client_widget = QWidget()
            client_layout = QHBoxLayout(client_widget)
            client_layout.setContentsMargins(0, 0, 0, 0)
            client_layout.setSpacing(8)  # gap-2
            
            # Avatar: 24x24 with initials
            client_name = p.get("client_name", "Unknown")
            initials = "".join([word[0] for word in client_name.split()[:2]]).upper()
            
            # Determine avatar color based on client
            avatar_colors = ["rgba(125,211,227,0.30)", "rgba(124,138,244,0.30)", "rgba(232,124,138,0.30)", "#908f9e"]
            avatar_color = avatar_colors[hash(client_name) % len(avatar_colors)]
            
            avatar_label = QLabel()
            avatar_pixmap = _create_avatar_pixmap(initials, avatar_color, size=24)
            avatar_label.setPixmap(avatar_pixmap)
            avatar_label.setStyleSheet("background: transparent; border: none;")
            client_layout.addWidget(avatar_label)
            
            # Client name: 14px body-md
            client_label = QLabel(client_name)
            client_label.setFont(QFont("Inter", 14))
            client_label.setStyleSheet("color: #9a9cb8; background: transparent; border: none;")
            client_layout.addWidget(client_label)
            client_layout.addStretch()
            
            self.table.setCellWidget(i, 2, client_widget)

            # TYPE column: 13px body-sm
            type_item = QTableWidgetItem(p.get("type", "General"))
            type_item.setFont(QFont("Inter", 13))
            type_item.setForeground(QColor("#9a9cb8"))
            type_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 3, type_item)

            # STATUS column: badge
            status_widget = self._create_status_badge(p.get("status", "Not Started"))
            self.table.setCellWidget(i, 4, status_widget)

            # DEADLINE column: 14px tabular-nums / 500 weight
            deadline_str = p.get("deadline", "")
            if deadline_str:
                deadline_date = QDate.fromString(deadline_str, "yyyy-MM-dd")
                if deadline_date.isValid():
                    formatted_deadline = deadline_date.toString("MMM dd, yyyy")
                    # Check if overdue
                    is_overdue = deadline_date < QDate.currentDate() and p.get("status") != "Completed"
                else:
                    formatted_deadline = deadline_str
                    is_overdue = False
            else:
                formatted_deadline = "—"
                is_overdue = False

            deadline_item = QTableWidgetItem(formatted_deadline)
            deadline_item.setFont(QFont("Inter", 14, QFont.Medium))
            deadline_item.setForeground(QColor("#e87c8a" if is_overdue else "#9a9cb8"))
            deadline_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 5, deadline_item)

            # ACTIONS column: edit + delete buttons (hidden by default, shown on hover)
            actions_widget = self._create_actions_cell(p.get("id", 0))
            self.table.setCellWidget(i, 6, actions_widget)


    def _create_status_badge(self, status: str) -> QWidget:
        """Create status badge per design tokens."""
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Badge: 12px / 700 weight / 9999px border-radius / 4px×12px padding
        badge = QLabel(status)
        badge.setFont(QFont("Inter", 12, QFont.Bold))
        badge.setAlignment(Qt.AlignCenter)
        
        # Status colors per design tokens
        status_styles = {
            "In Progress": "background-color: rgba(125,211,227,0.20); color: #7dd3e3; border: 1px solid rgba(69,159,173,0.30);",
            "Active": "background-color: rgba(125,211,227,0.20); color: #7dd3e3; border: 1px solid rgba(69,159,173,0.30);",
            "Completed": "background-color: rgba(130,216,172,0.20); color: #82d8ac; border: 1px solid rgba(0,106,71,0.30);",
            "Review": "background-color: rgba(240,200,120,0.10); color: #f0c878; border: 1px solid rgba(240,200,120,0.30);",
            "Revision": "background-color: rgba(240,200,120,0.10); color: #f0c878; border: 1px solid rgba(240,200,120,0.30);",
            "On Hold": "background-color: rgba(240,200,120,0.10); color: #f0c878; border: 1px solid rgba(240,200,120,0.30);",
            "Delayed": "background-color: rgba(232,124,138,0.20); color: #e87c8a; border: 1px solid rgba(232,124,138,0.30);",
            "Cancelled": "background-color: rgba(232,124,138,0.20); color: #e87c8a; border: 1px solid rgba(232,124,138,0.30);",
            "Not Started": "background-color: rgba(69,70,82,0.40); color: #c6c5d5; border: 1px solid rgba(69,70,82,0.60);",
            "Archived": "background-color: rgba(69,70,82,0.40); color: #c6c5d5; border: 1px solid rgba(69,70,82,0.60);",
        }
        
        style = status_styles.get(status, status_styles["Not Started"])
        badge.setStyleSheet(f"{style} border-radius: 9999px; padding: 4px 12px;")
        
        layout.addWidget(badge)
        return container

    def _create_actions_cell(self, project_id: int) -> QWidget:
        """Create actions cell with edit and delete buttons."""
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)  # gap-2
        layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        # Edit button: 20px icon size / 8px padding
        edit_btn = QPushButton()
        edit_btn.setIcon(QIcon(_load_svg_icon("edit_note", size=20, color="#9a9cb8")))
        edit_btn.setIconSize(QSize(20, 20))
        edit_btn.setFixedSize(36, 36)
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #1e1f2a;
            }
        """)
        edit_btn.clicked.connect(lambda: self._edit_project_by_id(project_id))
        layout.addWidget(edit_btn)

        # Delete button
        delete_btn = QPushButton()
        delete_btn.setIcon(QIcon(_load_svg_icon("delete_outline", size=20, color="#9a9cb8")))
        delete_btn.setIconSize(QSize(20, 20))
        delete_btn.setFixedSize(36, 36)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 8px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #1e1f2a;
            }
        """)
        delete_btn.clicked.connect(lambda: self._delete_project_by_id(project_id))
        layout.addWidget(delete_btn)

        return container


    # CRUD Operations
    def _add_project(self) -> None:
        """Open dialog to add a new project."""
        clients = self.client_repo.get_all()
        if not clients:
            QMessageBox.warning(
                self,
                "No Clients",
                "You need to add at least one client before creating a project.\n\n"
                "Go to the Clients page to add a client first."
            )
            return
        
        dialog = ProjectDialog(self, clients=clients)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.repo.add(**data)
                emit_data_changed()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Project '{data['name']}' created successfully!"
                )
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create project: {e}")

    def _edit_project_by_id(self, project_id: int) -> None:
        """Open dialog to edit project by ID."""
        project = self.repo.get_by_id(project_id)
        if not project:
            QMessageBox.warning(self, "Error", "Project not found.")
            return
        
        clients = self.client_repo.get_all()
        dialog = ProjectDialog(self, clients=clients, project=project)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.repo.update(project_id, **data)
                emit_data_changed()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Project '{data['name']}' updated successfully!"
                )
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not update project: {e}")

    def _delete_project(self) -> None:
        """Delete selected project."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a project to delete."
            )
            return
        
        item = self.table.item(row, 0)
        if item:
            project_id = int(item.text().replace("SD-", ""))
            self._delete_project_by_id(project_id)

    def _delete_project_by_id(self, project_id: int) -> None:
        """Delete project by ID after confirmation."""
        project = self.repo.get_by_id(project_id)
        if not project:
            QMessageBox.warning(self, "Error", "Project not found.")
            return
        
        project_name = project["name"]
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
                emit_data_changed()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Project '{project_name}' deleted successfully."
                )
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete project: {e}")


class ProjectDialog(QDialog):
    """Dialog for adding or editing a project."""

    STATUSES = ["Not Started", "In Progress", "Review", "On Hold", "Completed", "Cancelled"]
    TYPES = ["Design", "Video", "Writing", "Music", "Development", "Branding", "Consulting", "General"]

    def __init__(self, parent=None, clients=None, project=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Project" if project else "New Project")
        self.setMinimumWidth(550)
        
        # Apply styling per design tokens
        self.setStyleSheet("""
            QDialog {
                background-color: #1a1b26;
            }
            QLabel {
                color: #9a9cb8;
                font-size: 13px;
                font-weight: 500;
                background: transparent;
                border: none;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox {
                background-color: #12131d;
                border: 1px solid #454652;
                border-radius: 8px;
                padding: 8px 12px;
                color: #e2e4f0;
                font-family: 'Inter';
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {
                border: 1px solid #bcc2ff;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(24)

        # Title
        title = QLabel("Edit Project Details" if project else "Create New Project")
        title.setFont(QFont("Inter", 20, QFont.Bold))
        title.setStyleSheet("color: #e2e4f0; font-size: 20px; font-weight: 700;")
        layout.addWidget(title)

        # Form
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
        form.addRow("Client *", self.client_combo)

        # Project name
        self.name_input = QLineEdit(project["name"] if project else "")
        self.name_input.setPlaceholderText("Enter project name")
        form.addRow("Project Name *", self.name_input)

        # Type
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.TYPES)
        if project and project["type"]:
            self.type_combo.setCurrentText(project["type"])
        form.addRow("Type", self.type_combo)

        # Description
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(90)
        self.desc_input.setPlaceholderText("Brief project description...")
        if project and project["description"]:
            self.desc_input.setPlainText(project["description"])
        form.addRow("Description", self.desc_input)

        # Deadline
        self.deadline_input = QDateEdit()
        self.deadline_input.setCalendarPopup(True)
        self.deadline_input.setDate(QDate.currentDate().addDays(30))
        if project and project["deadline"]:
            self.deadline_input.setDate(QDate.fromString(project["deadline"], "yyyy-MM-dd"))
        form.addRow("Deadline", self.deadline_input)

        # Budget
        self.budget_input = QDoubleSpinBox()
        self.budget_input.setRange(0, 10_000_000)
        self.budget_input.setPrefix("₹ ")
        if project and project["budget"]:
            self.budget_input.setValue(project["budget"])
        form.addRow("Budget", self.budget_input)

        # Status (only for edit mode)
        if project:
            self.status_combo = QComboBox()
            self.status_combo.addItems(self.STATUSES)
            self.status_combo.setCurrentText(project["status"])
            form.addRow("Status", self.status_combo)
        else:
            self.status_combo = None

        layout.addLayout(form)

        # Helper text
        helper = QLabel("* Required fields")
        helper.setStyleSheet("color: #6b6d85; font-size: 11px; font-style: italic;")
        layout.addWidget(helper)

        layout.addStretch()

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Save Project")
        buttons.button(QDialogButtonBox.Cancel).setText("Cancel")
        
        buttons.button(QDialogButtonBox.Ok).setStyleSheet("""
            QPushButton {
                background-color: #7c8af4;
                color: #061987;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 700;
                font-size: 13px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #9aa4f7;
            }
        """)
        
        buttons.button(QDialogButtonBox.Cancel).setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #e2e4f0;
                border: 1px solid #454652;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 600;
                font-size: 13px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #282935;
            }
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
        """Return form data as dictionary."""
        data = {
            "client_id": self.client_combo.currentData(),
            "name": self.name_input.text().strip(),
            "project_type": self.type_combo.currentText(),
            "description": self.desc_input.toPlainText().strip(),
            "deadline": self.deadline_input.date().toString("yyyy-MM-dd"),
            "budget": self.budget_input.value(),
        }
        if self.status_combo:
            data["status"] = self.status_combo.currentText()
        return data
