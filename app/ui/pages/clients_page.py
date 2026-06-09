"""Clients Page — refined to match the reference layout from Smartdesk Freelancer Suite.

Features: KPI cards, top clients by revenue chart, separate search and action row,
8-column table with inline avatars + status dots + action buttons, and pagination footer.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

# Add project root to sys.path if run directly to support executing the file directly
_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect, Property
from PySide6.QtGui import QColor, QIcon, QPixmap, QPainter, QBrush, QFont, QFontDatabase
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QAbstractScrollArea,
    QComboBox,
)

from app.config import ASSETS_DIR
from app.data.database import Database
from app.data.repositories.client_repo import ClientRepository
from app.ui.styles.theme import Colors
from app.ui.widgets.stat_card import StatCard
from app.ui.widgets.animated import GradientBar
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


def _create_avatar_pixmap(initials: str, size: int = 32) -> QPixmap:
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


def _create_solid_avatar_pixmap(initials: str, size: int = 32) -> QPixmap:
    """Create a circular avatar image with a solid colored background and dark text."""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Solid circle background (#7c8af4)
    painter.setBrush(QBrush(QColor("#7c8af4")))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, size, size)

    # Initials text in dark contrast color #0f208b
    painter.setPen(QColor("#0f208b"))
    font = QFont("Inter")
    font.setPixelSize(12)
    font.setWeight(QFont.Weight.DemiBold)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, initials)

    painter.end()
    return pixmap



def _format_lakhs(val: float) -> str:
    """Format money values in Lakhs (L) or Thousands (K)."""
    if val >= 100000:
        return f"₹{val/100000:.1f}L"
    elif val >= 1000:
        return f"₹{val/1000:.0f}K"
    else:
        return f"₹{val:,.0f}"


def _get_client_status(db: Database, client_id: int) -> str:
    """Compute client status dynamically based on active projects and invoices."""
    proj_rows = db.execute("SELECT status FROM projects WHERE client_id = ?", (client_id,))
    statuses = [p["status"] for p in proj_rows]

    if not statuses:
        return "Inactive"

    if "In Progress" in statuses:
        return "Active"
    elif "Review" in statuses:
        return "Pending"
    elif "Completed" in statuses:
        # Check if they have unpaid invoices
        inv_rows = db.execute(
            """SELECT i.status FROM invoices i 
               JOIN projects p ON i.project_id = p.id 
               WHERE p.client_id = ? AND i.status = 'Unpaid'""",
            (client_id,),
        )
        if inv_rows:
            return "Pending"
        return "Active"
    else:
        return "Inactive"


# ClientStatCard class removed in favor of standard StatCard


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


class ClientsPage(QWidget):
    """Clients page - matches the reference screen layout."""

    def __init__(self, db: Database):
        super().__init__()
        self.setObjectName("clients_page")
        self.db = db
        self.repo = ClientRepository(db)

        self.current_page = 0
        self.page_size = 10
        self.all_clients = []
        self.all_clients_raw = []
        self.filter_dropdown = None

        # Main layout with QScrollArea
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_widget.setObjectName("clients_content")
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignTop)

        # 1. Header (Simple QLabel matching visual design)
        self.title_lbl = QLabel("Clients")
        self.title_lbl.setObjectName("clients_page_title")
        self.title_lbl.setProperty("class", "heading_xl")
        layout.addWidget(self.title_lbl)

        # 2. KPI Cards row
        self._build_stat_cards(layout)

        # 3. Top Clients by Revenue Chart
        self._build_top_clients_chart(layout)

        # 4. Search and Action Row
        self._build_search_and_action_row(layout)

        # 5. Clients Table Card (Includes custom QTableWidget and Footer)
        self._build_table(layout)

        scroll.setWidget(content_widget)
        page_layout.addWidget(scroll)

        # Load data
        self.refresh()

    def _build_stat_cards(self, parent_layout: QVBoxLayout) -> None:
        stat_row = QHBoxLayout()
        stat_row.setContentsMargins(0, 0, 0, 0)
        stat_row.setSpacing(16)

        # Card 1: New Clients
        self.card_new = StatCard(
            "New Clients", "0",
            icon="person_add",
            accent=Colors.ACCENT_PRIMARY_LIGHT,
            sub_text=""
        )

        # Card 2: Avg. Revenue
        self.card_avg = StatCard(
            "Avg. Revenue", "₹0.0L",
            icon="payments",
            accent=Colors.ACCENT_INFO,
            sub_text="per active client contract"
        )

        # Card 3: Retention Rate
        self.card_retention = StatCard(
            "Retention Rate", "94%",
            icon="favorite",
            accent=Colors.ACCENT_WARNING,
            sub_text="High satisfaction rating"
        )

        tints = {
            Colors.ACCENT_PRIMARY_LIGHT: "rgba(188, 194, 255, 0.10)",
            Colors.ACCENT_INFO: "rgba(125, 211, 227, 0.10)",
            Colors.ACCENT_WARNING: "rgba(240, 200, 120, 0.10)",
            Colors.ACCENT_SUCCESS: "rgba(130, 216, 172, 0.10)",
        }

        card_configs = [
            (self.card_new, Colors.ACCENT_PRIMARY_LIGHT, "person_add"),
            (self.card_avg, Colors.ACCENT_INFO, "payments"),
            (self.card_retention, Colors.ACCENT_WARNING, "favorite"),
        ]

        for card, accent, icon_name in card_configs:
            # Enable mouse tracking for hover effects
            card.setAttribute(Qt.WA_Hover, True)
            card.setMouseTracking(True)

            # Setup shadow effect for hover animation
            card_shadow = QGraphicsDropShadowEffect(card)
            card_shadow.setBlurRadius(0)
            card_shadow.setColor(QColor(124, 138, 244, 180))  # Purple glow
            card_shadow.setOffset(0, 0)
            card.setGraphicsEffect(card_shadow)
            
            # Create animation for blur radius
            shadow_animation = QPropertyAnimation(card_shadow, b"blurRadius")
            shadow_animation.setDuration(200)  # 200ms animation
            shadow_animation.setEasingCurve(QEasingCurve.OutCubic)
            
            # Store references for later use
            card._shadow = card_shadow
            card._shadow_animation = shadow_animation
            card._original_stylesheet = "QFrame#dashboard_stat_card { background-color: #222336; border-radius: 12px; border: none; padding: 0px; }"
            card._hover_stylesheet = "QFrame#dashboard_stat_card { background-color: #2a2c3e; border-radius: 12px; border: none; padding: 0px; }"
            
            # 1. Height and size policy constraints
            # Add extra margins to accommodate the shadow without causing layout shift
            card.setMinimumHeight(140)
            card.setMaximumHeight(140)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            card.setStyleSheet(card._original_stylesheet)
            card.setContentsMargins(4, 4, 4, 4)  # Add margin to prevent shadow clipping
            
            # Fix icon bubble to prevent any movement during shadow animation
            card._icon_bubble.setAttribute(Qt.WA_TranslucentBackground, False)
            card._icon_bubble.setMinimumSize(24, 24)
            card._icon_bubble.setMaximumSize(24, 24)
            
            # 2. Internal layout
            layout = card.layout()
            if layout:
                layout.setAlignment(Qt.Alignment())
                layout.setContentsMargins(20, 16, 20, 16)
                layout.setSpacing(4)
                
            # 3. Icon bubble background tint and fixed positioning
            rgba_color = tints.get(accent, "rgba(124, 138, 244, 0.10)")
            # Ensure icon bubble maintains fixed size and doesn't shift
            card._icon_bubble.setFixedSize(24, 24)
            card._icon_bubble.setScaledContents(False)
            if icon_name and (_ICONS_DIR / f"{icon_name}.svg").exists():
                icon_pixmap = _load_svg_icon(icon_name, size=16, color=accent)
                card._icon_bubble.setPixmap(icon_pixmap)
            card._icon_bubble.setStyleSheet(f"background-color: {rgba_color}; border-radius: 4px; border: none; min-width: 24px; max-width: 24px; min-height: 24px; max-height: 24px;")
            
            # 4. Typography styling
            title_label = card._label
            value_label = card._value
            subtitle_label = card._sub

            title_label.setFont(QFont("Inter", 9))
            title_label.setStyleSheet("color: #8B8FA8; background: transparent; border: none;")

            value_label.setFont(QFont("Inter", 24, QFont.Bold))
            value_label.setStyleSheet("color: #FFFFFF; background: transparent; border: none; font-size: 28px;")

            subtitle_label.setFont(QFont("Inter", 8))
            subtitle_label.setStyleSheet("color: #6B7280; background: transparent; border: none;")
            
            # Install event filter for hover events
            card.installEventFilter(self)

            stat_row.addWidget(card, 1)

        parent_layout.addLayout(stat_row)

    def _build_top_clients_chart(self, parent_layout: QVBoxLayout) -> None:
        self.chart_card = QFrame()
        self.chart_card.setObjectName("dashboard_chart_card")
        self.chart_card.setStyleSheet("QFrame#dashboard_chart_card { background-color: #222336; border-radius: 12px; border: 1px solid #2d2e42; }")
        self.chart_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        chart_layout = QVBoxLayout(self.chart_card)
        chart_layout.setContentsMargins(24, 24, 24, 24)
        chart_layout.setSpacing(16)

        title = QLabel("Top Clients by Revenue")
        title.setProperty("class", "heading_lg")
        chart_layout.addWidget(title)

        # Container for the client rows
        self.chart_rows_container = QWidget()
        self.chart_rows_container.setObjectName("chart_rows_container")
        self.chart_rows_layout = QVBoxLayout(self.chart_rows_container)
        self.chart_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.chart_rows_layout.setSpacing(16)

        chart_layout.addWidget(self.chart_rows_container)
        parent_layout.addWidget(self.chart_card)

    def _build_search_and_action_row(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        row.setSpacing(16)

        left_side = QHBoxLayout()
        left_side.setSpacing(12)

        # Search field with embedded icon
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search clients...")
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
        self.filter_btn.clicked.connect(self._toggle_filter_dropdown)
        
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
            QPushButton#filter_btn:pressed {{
                background-color: #1e1f2f;
            }}
        """)
        
        # Setup shadow effect for hover animation on filter button
        self.filter_btn.setAttribute(Qt.WA_Hover, True)
        filter_btn_shadow = QGraphicsDropShadowEffect(self.filter_btn)
        filter_btn_shadow.setBlurRadius(0)
        filter_btn_shadow.setColor(QColor(124, 138, 244, 180))  # Purple glow
        filter_btn_shadow.setOffset(0, 0)
        self.filter_btn.setGraphicsEffect(filter_btn_shadow)
        
        # Create shadow animation
        self._filter_btn_shadow_animation = QPropertyAnimation(filter_btn_shadow, b"blurRadius")
        self._filter_btn_shadow_animation.setDuration(200)
        self._filter_btn_shadow_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.filter_btn.installEventFilter(self)
        
        left_side.addWidget(self.filter_btn)

        row.addLayout(left_side)
        row.addStretch()

        right_side = QHBoxLayout()
        right_side.setSpacing(8)
        right_side.setContentsMargins(0, 0, 0, 0)

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
        self.clear_btn.clicked.connect(self._clear_all_clients)
        right_side.addWidget(self.clear_btn)

        # Add Client button
        self.add_btn = QPushButton("Add Client")
        self.add_btn.setObjectName("add_client_btn")
        self.add_btn.setCursor(Qt.PointingHandCursor)
        self.add_btn.setStyleSheet(f"""
            QPushButton#add_client_btn {{
                background-color: {Colors.ACCENT_PRIMARY};
                color: #ffffff;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
                border: none;
            }}
            QPushButton#add_client_btn:hover {{
                background-color: {Colors.ACCENT_PRIMARY_HOVER};
            }}
            QPushButton#add_client_btn:pressed {{
                background-color: {Colors.ACCENT_PRIMARY_PRESSED};
            }}
        """)
        add_icon = _load_svg_icon("add", size=16, color="#ffffff")
        self.add_btn.setIcon(QIcon(add_icon))
        self.add_btn.clicked.connect(self._add_client)
        right_side.addWidget(self.add_btn)

        row.addLayout(right_side)
        parent_layout.addLayout(row)

    def _build_table(self, parent_layout: QVBoxLayout) -> None:
        self.table_card = QFrame()
        self.table_card.setObjectName("dashboard_table_card")
        self.table_card.setStyleSheet("QFrame#dashboard_table_card { background-color: #222336; border-radius: 12px; border: 1px solid #2d2e42; }")
        self.table_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        table_layout = QVBoxLayout(self.table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # Table widget - PaginationTableWidget dynamically sizes height to rows
        self.table = PaginationTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "CLIENT", "STATUS", "EMAIL ADDRESS", "PHONE", "COMPANY", "CREATED", "ACTIONS"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setFrameShape(QFrame.NoFrame)

        # Proportional column sizing
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        from PySide6.QtWidgets import QHeaderView
        header.setSectionResizeMode(0, QHeaderView.Fixed)            # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Client
        header.setSectionResizeMode(2, QHeaderView.Fixed)            # Status
        header.setSectionResizeMode(3, QHeaderView.Stretch)          # Email
        header.setSectionResizeMode(4, QHeaderView.Fixed)            # Phone
        header.setSectionResizeMode(5, QHeaderView.Stretch)          # Company
        header.setSectionResizeMode(6, QHeaderView.Fixed)            # Created
        header.setSectionResizeMode(7, QHeaderView.Fixed)            # Actions

        self.table.setColumnWidth(0, 85)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(4, 110)
        self.table.setColumnWidth(6, 110)
        self.table.setColumnWidth(7, 80)

        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        table_layout.addWidget(self.table)

        # ─── Pagination Footer ─────────────────────────────────────────────
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
        self.info_label.setStyleSheet("color: #9a9cb8; font-size: 13px; font-weight: 400;")
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

    # ══════════════════════════════════════════════════════════════════
    # DATA LOADING AND REFRESH
    # ══════════════════════════════════════════════════════════════════
    
    def eventFilter(self, obj, event):
        """Handle hover events for stat cards to trigger shadow animation."""
        from PySide6.QtCore import QEvent
        # Check if the object is one of our stat cards
        if obj in (self.card_new, self.card_avg, self.card_retention):
            if hasattr(obj, '_shadow') and hasattr(obj, '_shadow_animation'):
                event_type = event.type()
                if event_type == QEvent.Enter:
                    # Mouse entered - animate shadow in and lighten background
                    obj._shadow_animation.stop()
                    obj._shadow_animation.setStartValue(obj._shadow.blurRadius())
                    obj._shadow_animation.setEndValue(20)
                    obj._shadow_animation.start()
                    if hasattr(obj, '_hover_stylesheet'):
                        obj.setStyleSheet(obj._hover_stylesheet)
                elif event_type == QEvent.Leave:
                    # Mouse left - animate shadow out and restore background
                    obj._shadow_animation.stop()
                    obj._shadow_animation.setStartValue(obj._shadow.blurRadius())
                    obj._shadow_animation.setEndValue(0)
                    obj._shadow_animation.start()
                    if hasattr(obj, '_original_stylesheet'):
                        obj.setStyleSheet(obj._original_stylesheet)
        elif obj == self.filter_btn:
            shadow = self.filter_btn.graphicsEffect()
            if shadow and hasattr(self, '_filter_btn_shadow_animation'):
                event_type = event.type()
                if event_type == QEvent.Enter:
                    self._filter_btn_shadow_animation.stop()
                    self._filter_btn_shadow_animation.setStartValue(shadow.blurRadius())
                    self._filter_btn_shadow_animation.setEndValue(15)  # 15px glow radius
                    self._filter_btn_shadow_animation.start()
                elif event_type == QEvent.Leave:
                    self._filter_btn_shadow_animation.stop()
                    self._filter_btn_shadow_animation.setStartValue(shadow.blurRadius())
                    self._filter_btn_shadow_animation.setEndValue(0)
                    self._filter_btn_shadow_animation.start()
        return super().eventFilter(obj, event)

    def refresh(self) -> None:
        try:
            clients = self.repo.get_all()
        except Exception:
            clients = []

        # Convert records to lists/dicts safely
        clients = [dict(c) for c in clients]

        # Calculate live dynamic stats directly from the database:
        
        # 1. NEW CLIENTS = count of clients added this month
        try:
            prefix = date.today().strftime("%Y-%m")
            res_new = self.db.execute("SELECT COUNT(*) as cnt FROM clients WHERE created_date LIKE ?", (f"{prefix}%",))
            new_count = res_new[0]["cnt"] if res_new else 0
        except Exception:
            new_count = 0

        # 2. AVG. REVENUE = total revenue divided by number of active clients
        try:
            res_total = self.db.execute("SELECT SUM(budget) as total FROM projects")
            total_revenue = res_total[0]["total"] if (res_total and res_total[0]["total"] is not None) else 0.0
            
            # Active clients count based on dynamic status
            active_clients_count = 0
            for c in clients:
                status = _get_client_status(self.db, c["id"])
                if status == "Active":
                    active_clients_count += 1
            
            avg_revenue = total_revenue / active_clients_count if active_clients_count > 0 else 0.0
        except Exception:
            avg_revenue = 0.0

        # 3. RETENTION RATE = percentage of clients with at least one completed project
        try:
            total_clients_count = len(clients)
            res_completed = self.db.execute(
                "SELECT COUNT(DISTINCT client_id) as cnt FROM projects WHERE status = 'Completed'"
            )
            completed_clients_count = res_completed[0]["cnt"] if res_completed else 0
            
            retention_rate = (completed_clients_count / total_clients_count * 100) if total_clients_count > 0 else 0.0
        except Exception:
            retention_rate = 0.0

        # Update KPI Cards
        self.card_new.set_value(str(new_count))
        self.card_new.set_sub_text('<span style="color: #82d8ac;">▲ this month</span>')
        self.card_avg.set_value(_format_lakhs(avg_revenue))
        self.card_avg.set_sub_text("per active client")
        self.card_retention.set_value(f"{retention_rate:.0f}%")
        self.card_retention.set_sub_text("with completed projects")

        # Query & Draw top clients chart
        self._populate_top_clients()

        # Update all clients and populate table
        self.all_clients = clients
        self.all_clients_raw = clients
        self.current_page = 0
        self._populate_table_current_page()

    def _populate_top_clients(self) -> None:
        # Stop and clear existing animations
        if hasattr(self, "_progress_animations"):
            for anim in self._progress_animations:
                anim.stop()
            self._progress_animations.clear()
        else:
            self._progress_animations = []

        # Clear existing rows in layout
        while self.chart_rows_layout.count():
            item = self.chart_rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Query top 3 clients by project budget sum
        query = """
            SELECT c.id, c.name, c.company, COALESCE(SUM(p.budget), 0) as revenue
            FROM clients c
            LEFT JOIN projects p ON c.id = p.client_id
            GROUP BY c.id
            ORDER BY revenue DESC
            LIMIT 3
        """
        try:
            rows = [dict(r) for r in self.db.execute(query)]
        except Exception:
            rows = []

        # Use fallback reference data if empty
        if not rows or sum(r["revenue"] for r in rows) == 0:
            rows = [
                {"name": "Priya Sharma", "company": "Priya Design Studio", "revenue": 550000},
                {"name": "Arjun Nair", "company": "Tech Trails", "revenue": 380000},
                {"name": "Rohan Kapoor", "company": "Kapoor & Assoc.", "revenue": 210000},
            ]

        max_rev = rows[0]["revenue"] if rows else 1

        for idx, row in enumerate(rows):
            row_widget = QFrame()
            row_widget.setObjectName("chart_client_row")
            row_widget.setFrameShape(QFrame.NoFrame)
            
            row_layout = QVBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(12)  # 12px spacing between Row 1 and Row 2

            # Row 1 layout: [Avatar] [Client Name] -------- [Revenue]
            row1_layout = QHBoxLayout()
            row1_layout.setContentsMargins(0, 0, 0, 0)
            row1_layout.setSpacing(12)  # 12px spacing between avatar and name

            name = row.get("company") or row.get("name") or "—"
            initials = "".join([p[0] for p in name.split() if p])[:2].upper()

            # Avatar: 32x32px fixed size
            avatar_lbl = QLabel()
            avatar_lbl.setPixmap(_create_solid_avatar_pixmap(initials, size=32))
            avatar_lbl.setFixedSize(32, 32)
            row1_layout.addWidget(avatar_lbl, 0, Qt.AlignVCenter)

            # Client name label
            name_lbl = QLabel(name)
            name_lbl.setObjectName("chart_client_name")
            row1_layout.addWidget(name_lbl, 0, Qt.AlignVCenter)
            row1_layout.addStretch()

            # Revenue amount label on the right
            rev_val = row["revenue"]
            rev_lbl = QLabel(_format_lakhs(rev_val))
            rev_lbl.setObjectName("chart_client_revenue")
            row1_layout.addWidget(rev_lbl, 0, Qt.AlignVCenter)

            row_layout.addLayout(row1_layout)

            # Row 2: GradientBar (with gradient animation matching the old color palette)
            percentage = int((row["revenue"] / max_rev) * 100) if max_rev > 0 else 0
            
            # Select start and end colors based on index to match old palette in gradient format
            color_pairs = [
                ("#7c8af4", "#bcc2ff"),  # Client 1: Purple to Lavender gradient
                ("#3a8e9e", "#7dd3e3"),  # Client 2: Dark Teal/Blue to Light Teal gradient
                ("#56b582", "#82d8ac"),  # Client 3: Dark Mint to Light Mint/Green gradient
            ]
            color_start, color_end = color_pairs[idx % len(color_pairs)]
            
            bar = GradientBar(
                value=0.0,
                max_value=100.0,
                color_start=color_start,
                color_end=color_end,
                height=6,
                parent=self
            )
            bar.setObjectName(f"top_client_progress_{idx + 1}")
            bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            
            row_layout.addWidget(bar)
            self.chart_rows_layout.addWidget(row_widget)

            # Animate the bar's value to the target percentage with QEasingCurve.OutCubic over 1000ms
            bar._value_anim.setDuration(1000)
            bar.set_value(percentage, animate=True)

    def _populate_table(self, clients: list) -> None:
        self.table.clearSpans()
        if len(clients) == 0:
            self.table.setRowCount(1)
            self.table.setRowHeight(0, 120)
            self.table.setSpan(0, 0, 1, 8)
            empty_label = QLabel("No clients found. Add your first client to get started.")
            empty_label.setStyleSheet("color: #6B7280; font-size: 13px;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(0, 0, empty_label)
        else:
            self.table.setRowCount(len(clients))
            self.table.verticalHeader().setDefaultSectionSize(48)

            for i, c in enumerate(clients):
                client_id = c["id"]

                # 1. ID column (e.g. #CL-042)
                id_str = f"#CL-{client_id:03d}"
                id_item = QTableWidgetItem(id_str)
                id_item.setForeground(QColor(Colors.TEXT_MUTED))
                id_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                self.table.setItem(i, 0, id_item)

                # 2. Client column (Avatar + Name)
                client_widget = QFrame()
                client_widget.setObjectName("table_client_container")
                client_widget.setFrameShape(QFrame.NoFrame)
                client_layout = QHBoxLayout(client_widget)
                client_layout.setContentsMargins(8, 0, 8, 0)
                client_layout.setSpacing(8)

                name = c["name"]
                initials = "".join([p[0] for p in name.split() if p])[:2].upper()
                avatar_lbl = QLabel()
                avatar_lbl.setPixmap(_create_avatar_pixmap(initials, size=28))
                client_layout.addWidget(avatar_lbl)

                name_lbl = QLabel(name)
                name_lbl.setObjectName("table_client_name")
                client_layout.addWidget(name_lbl)
                client_layout.addStretch()

                self.table.setCellWidget(i, 1, client_widget)

                # 3. Status column (Color dot next to status text)
                status_text = _get_client_status(self.db, client_id)
                status_widget = self._create_status_cell(status_text)
                self.table.setCellWidget(i, 2, status_widget)

                # 4. Email Address
                email_item = QTableWidgetItem(c.get("email") or "—")
                email_item.setForeground(QColor(Colors.TEXT_SECONDARY))
                self.table.setItem(i, 3, email_item)

                # 5. Phone
                phone_item = QTableWidgetItem(c.get("phone") or "—")
                phone_item.setForeground(QColor(Colors.TEXT_SECONDARY))
                self.table.setItem(i, 4, phone_item)

                # 6. Company
                company_item = QTableWidgetItem(c.get("company") or "—")
                company_item.setForeground(QColor(Colors.TEXT_SECONDARY))
                self.table.setItem(i, 5, company_item)

                # 7. Created Date
                raw_date = c.get("created_date") or ""
                formatted_date = "—"
                if raw_date:
                    try:
                        from datetime import datetime
                        dt = datetime.fromisoformat(raw_date.split()[0])
                        formatted_date = dt.strftime("%d %b, %Y")
                    except Exception:
                        formatted_date = raw_date
                created_item = QTableWidgetItem(formatted_date)
                created_item.setForeground(QColor(Colors.TEXT_SECONDARY))
                self.table.setItem(i, 6, created_item)

                # 8. Actions
                actions_widget = self._create_actions_cell(client_id)
                self.table.setCellWidget(i, 7, actions_widget)

        self.table.updateGeometry()

    def _create_status_cell(self, status: str) -> QWidget:
        """Styled pill badge matching the Stitch design with outline and proper spacing."""
        # Map client statuses to colors
        status_colors: dict[str, tuple[str, str]] = {
            # (border-color, text-color)
            "Active":   ("#82d8ac", "#82d8ac"),      # Green
            "Inactive": ("#555770", "#8B8FA8"),      # Grey
            "Pending":  ("#f0c878", "#f0c878"),      # Yellow
        }
        border, fg = status_colors.get(status, ("#555770", "#8B8FA8"))

        container = QWidget()
        container.setObjectName("table_status_container")
        container.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        badge = QLabel(status)
        badge.setObjectName("status_pill_badge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(
            f"QLabel#status_pill_badge {{"
            f"  background-color: transparent;"
            f"  color: {fg};"
            f"  border: 1px solid {border};"
            f"  border-radius: 10px;"
            f"  font-size: 11px;"
            f"  font-weight: 600;"
            f"  padding: 3px 12px;"
            f"  min-height: 20px;"
            f"}}"
        )
        layout.addWidget(badge)
        return container

    def _create_actions_cell(self, client_id: int) -> QWidget:
        container = QFrame()
        container.setObjectName("table_actions_container")
        container.setFrameShape(QFrame.NoFrame)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 16, 0)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        edit_btn = QPushButton()
        edit_btn.setObjectName("table_action_icon_btn")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setToolTip("Edit Client")
        edit_btn.setIcon(QIcon(_load_svg_icon("edit", size=18, color="#6b6d85")))
        edit_btn.setIconSize(QSize(18, 18))
        edit_btn.clicked.connect(lambda: self._edit_client_by_id(client_id))

        del_btn = QPushButton()
        del_btn.setObjectName("table_action_icon_btn")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Delete Client")
        del_btn.setIcon(QIcon(_load_svg_icon("delete", size=18, color="#6b6d85")))
        del_btn.setIconSize(QSize(18, 18))
        del_btn.clicked.connect(lambda: self._delete_client_by_id(client_id))

        layout.addWidget(edit_btn)
        layout.addWidget(del_btn)
        return container

    def _on_search(self, text: str) -> None:
        try:
            if text.strip():
                results = self.repo.search(text)
            else:
                results = self.repo.get_all()
        except Exception:
            results = []
        
        # Convert records to lists/dicts safely
        results = [dict(c) for c in results]
        self.all_clients = results
        self.all_clients_raw = results
        self.current_page = 0
        self._populate_table_current_page()

    def _toggle_filter_dropdown(self) -> None:
        if self.filter_dropdown is None:
            self.filter_dropdown = FilterDropdown(self, self.filter_btn)
        
        if self.filter_dropdown.isVisible():
            self.filter_dropdown.close()
        else:
            self.filter_dropdown.show_below_anchor()

    def apply_filter_rules(self, status: str, company: str, d_from: str, d_to: str) -> None:
        filtered = []
        for c in self.all_clients_raw:
            client_id = c["id"]
            
            # Status check
            if status != "All":
                c_status = _get_client_status(self.db, client_id)
                if c_status != status:
                    continue
            
            # Company check
            if company:
                c_company = (c.get("company") or "").lower()
                if company not in c_company:
                    continue
            
            # Date check
            c_date = (c.get("created_date") or "").split()[0]
            if d_from:
                if c_date < d_from:
                    continue
            if d_to:
                if c_date > d_to:
                    continue
            
            filtered.append(c)
        
        self.all_clients = filtered
        self.current_page = 0
        self._populate_table_current_page()

    def _populate_table_current_page(self) -> None:
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_clients = self.all_clients[start_idx:end_idx]
        
        self._populate_table(page_clients)
        self._update_pagination_ui()

    def _update_pagination_ui(self) -> None:
        total_items = len(self.all_clients)
        total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)
        
        if self.current_page >= total_pages:
            self.current_page = max(0, total_pages - 1)
            
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, total_items)
        
        if total_items == 0:
            self.info_label.setText("Showing 0 to 0 of 0 clients")
        else:
            self.info_label.setText(f"Showing {start_idx + 1} to {end_idx} of {total_items} clients")
            
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
        total_items = len(self.all_clients)
        total_pages = max(1, (total_items + self.page_size - 1) // self.page_size)
        if self.current_page < total_pages - 1:
            self._go_to_page(self.current_page + 1)

    # ══════════════════════════════════════════════════════════════════
    # CRUD OPERATIONS
    # ══════════════════════════════════════════════════════════════════

    def _add_client(self) -> None:
        dialog = ClientDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.repo.add(**data)
                emit_data_changed()
                SuccessDialog.show_success(
                    f"Client '{data['name']}' added successfully!", self
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not add client: {e}")
                return
            self.refresh()

    def _edit_client(self) -> None:
        """Edit currently selected table row (kept for double-click compatibility)."""
        row = self.table.currentRow()
        if row < 0:
            return
        # Fetch client ID from column 0 (e.g. #CL-042)
        item = self.table.item(row, 0)
        if item:
            try:
                client_id = int(item.text().replace("#CL-", ""))
                self._edit_client_by_id(client_id)
            except ValueError:
                pass

    def _edit_client_by_id(self, client_id: int) -> None:
        client = self.repo.get_by_id(client_id)
        if not client:
            QMessageBox.warning(self, "Error", "Client not found.")
            return

        dialog = ClientDialog(self, dict(client))
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                self.repo.update(client_id, **data)
                emit_data_changed()
                SuccessDialog.show_success(
                    f"Client '{data['name']}' updated successfully!", self
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not update client: {e}")
                return
            self.refresh()

    def _delete_client(self) -> None:
        """Delete currently selected table row (kept for compatibility)."""
        row = self.table.currentRow()
        if row < 0:
            return
        item = self.table.item(row, 0)
        if item:
            try:
                client_id = int(item.text().replace("#CL-", ""))
                self._delete_client_by_id(client_id)
            except ValueError:
                pass

    def _delete_client_by_id(self, client_id: int) -> None:
        client = self.repo.get_by_id(client_id)
        if not client:
            return
        client_name = client["name"]

        dialog = DeleteConfirmDialog(client_name, self)
        if dialog.exec() == QDialog.Accepted:
            try:
                self.repo.delete(client_id)
                emit_data_changed()
                SuccessDialog.show_success(
                    f"Client '{client_name}' deleted successfully.", self
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete client: {e}")
                return
            self.refresh()

    def _clear_all_clients(self) -> None:
        dialog = DeleteConfirmDialog(parent=self, is_clear_all=True)
        if dialog.exec() == QDialog.Accepted:
            try:
                self.db.execute("DELETE FROM clients")
                emit_data_changed()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete clients: {e}")
                return
            self.refresh()
            SuccessDialog.show_success(
                "All clients have been deleted successfully.", self
            )


class DeleteConfirmDialog(QDialog):
    """Dialog for confirming client deletion, styled with custom colors and layout."""

    def __init__(self, client_name: str = "", parent=None, is_clear_all: bool = False):
        super().__init__(parent)
        title_text = "Clear All Clients" if is_clear_all else "Confirm Delete"
        self.setWindowTitle(title_text)
        if is_clear_all:
            self.setFixedSize(600, 220)
        else:
            self.setFixedSize(600, 200)
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
        
        title = QLabel(title_text)
        title.setFont(QFont("Inter", 15, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        layout.addWidget(title)
        
        layout.addSpacing(8)
        
        question_text = "Are you sure you want to delete ALL clients?" if is_clear_all else f"Are you sure you want to delete client '{client_name}'?"
        question_label = QLabel(question_text)
        question_label.setWordWrap(True)
        question_label.setFont(QFont("Segoe UI", 12))
        question_label.setStyleSheet("color: #8B8FA8; background: transparent; border: none;")
        layout.addWidget(question_label)
        
        layout.addSpacing(4)
        
        if is_clear_all:
            warning_text = "This will permanently delete all clients and their related projects, invoices, and time logs. This action cannot be undone."
        else:
            warning_text = (
                "This will also delete all related projects, invoices, and time logs.\n"
                "This action cannot be undone."
            )
        warning_label = QLabel(warning_text)
        warning_label.setWordWrap(True)
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
        
        yes_btn_text = "Yes, Delete All" if is_clear_all else "Yes, Delete"
        self.yes_btn = QPushButton(yes_btn_text)
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


class SuccessDialog(QDialog):
    """Custom Success dialog matching requirements exactly."""

    def __init__(self, message: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Success")
        self.setFixedSize(400, 70)
        self.setObjectName("success_dialog")
        
        self.setStyleSheet("""
            QDialog#success_dialog {
                background-color: #252840;
                border: none;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(0)
        
        title = QLabel("Success")
        title.setFont(QFont("Inter", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        layout.addWidget(title)
        
        layout.addSpacing(8)
        
        body = QLabel(message)
        body.setFont(QFont("Inter", 10))
        body.setStyleSheet("color: #8B8FA8; background: transparent; border: none;")
        body.setWordWrap(True)
        layout.addWidget(body)
        
        layout.addStretch()
        
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.setCursor(Qt.PointingHandCursor)
        ok_btn.setFixedSize(80, 36)
        ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_PRIMARY};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: 600;
                padding: 0;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_PRIMARY_HOVER};
            }}
        """)
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        
        layout.addLayout(btn_row)

    @staticmethod
    def show_success(message: str, parent=None):
        dialog = SuccessDialog(message, parent)
        dialog.exec()


class ClientDialog(QDialog):
    """Dialog for adding or editing a client."""

    def __init__(self, parent=None, client=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Client" if client else "Add New Client")
        self.setMinimumWidth(500)
        
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

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(24)

        title = QLabel("Edit Client Details" if client else "Add New Client")
        title.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.01em;
        """)
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

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

        form.addRow("Name", self.name_input)
        form.addRow("Email", self.email_input)
        form.addRow("Phone", self.phone_input)
        form.addRow("Address", self.address_input)
        form.addRow("Company", self.company_input)
        
        layout.addLayout(form)

        helper = QLabel("* Required field")
        helper.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: 8px;
            font-style: italic;
        """)
        layout.addWidget(helper)

        layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Save Client")
        buttons.button(QDialogButtonBox.Cancel).setText("Cancel")
        
        buttons.button(QDialogButtonBox.Ok).setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_PRIMARY};
                color: {Colors.TEXT_INVERSE};
                border: none;
                border-radius: 8px;
                padding: 4px 16px;
                font-weight: 700;
                font-size: 13px;
                min-width: 80px;
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
                padding: 4px 16px;
                font-weight: 600;
                font-size: 13px;
                min-width: 80px;
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
        if not self.name_input.text().strip():
            QMessageBox.warning(
                self, "Validation Error", "Client name is required. Please enter a name."
            )
            self.name_input.setFocus()
            return
        
        email = self.email_input.text().strip()
        if email and "@" not in email:
            QMessageBox.warning(
                self, "Validation Error", "Please enter a valid email address."
            )
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


class FilterDropdown(QFrame):
    def __init__(self, parent_page: ClientsPage, anchor_widget: QWidget):
        super().__init__(parent_page, Qt.Popup | Qt.Window)
        self.parent_page = parent_page
        self.anchor_widget = anchor_widget
        self._is_closing = False
        
        self.setObjectName("filter_dropdown")
        self.setStyleSheet(f"""
            QFrame#filter_dropdown {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 8px;
            }}
            QLabel {{
                color: {Colors.TEXT_SECONDARY};
                font-size: 12px;
                font-weight: 500;
            }}
            QLineEdit {{
                background-color: {Colors.BG_ELEVATED};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 12px;
                color: {Colors.TEXT_PRIMARY};
            }}
            QComboBox {{
                background-color: {Colors.BG_ELEVATED};
                border: 1px solid {Colors.BORDER_SUBTLE};
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
                min-height: 24px;
                color: {Colors.TEXT_PRIMARY};
            }}
            QPushButton {{
                border-radius: 6px;
                font-size: 12px;
                font-weight: 600;
                padding: 6px 12px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["All", "Active", "Inactive", "Pending"])
        form.addRow("Status", self.status_combo)

        # Company
        self.company_input = QLineEdit()
        self.company_input.setPlaceholderText("Enter company name")
        form.addRow("Company", self.company_input)

        # Date range From
        self.date_from = QLineEdit()
        self.date_from.setPlaceholderText("YYYY-MM-DD (From)")
        form.addRow("From Date", self.date_from)

        # Date range To
        self.date_to = QLineEdit()
        self.date_to.setPlaceholderText("YYYY-MM-DD (To)")
        form.addRow("To Date", self.date_to)

        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {Colors.TEXT_PRIMARY};
                border: 1px solid {Colors.BORDER_SUBTLE};
            }}
            QPushButton:hover {{
                background-color: {Colors.BG_HOVER};
            }}
        """)
        self.reset_btn.clicked.connect(self.reset_filters)

        self.apply_btn = QPushButton("Apply Filter")
        self.apply_btn.setCursor(Qt.PointingHandCursor)
        self.apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.ACCENT_PRIMARY};
                color: {Colors.TEXT_INVERSE};
                border: none;
            }}
            QPushButton:hover {{
                background-color: {Colors.ACCENT_PRIMARY_HOVER};
            }}
        """)
        self.apply_btn.clicked.connect(self.apply_filters)

        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.apply_btn)
        layout.addLayout(btn_layout)

    def reset_filters(self):
        self.status_combo.setCurrentIndex(0)
        self.company_input.clear()
        self.date_from.clear()
        self.date_to.clear()
        self.apply_filters()

    def apply_filters(self):
        status = self.status_combo.currentText()
        company = self.company_input.text().strip().lower()
        d_from = self.date_from.text().strip()
        d_to = self.date_to.text().strip()

        self.parent_page.apply_filter_rules(status, company, d_from, d_to)
        self.close()

    def get_dropdown_height(self) -> int:
        return self.height()

    def set_dropdown_height(self, h: int) -> None:
        self.setFixedHeight(h)

    dropdownHeight = Property(int, get_dropdown_height, set_dropdown_height)

    def _on_animation_finished(self):
        # Restore normal height constraints
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX

    def show_below_anchor(self):
        self._is_closing = False
        # Position the popup right below the anchor button
        pos = self.anchor_widget.mapToGlobal(self.anchor_widget.rect().bottomLeft())
        pos.setY(pos.y() + 4)
        self.move(pos)
        
        # Calculate natural target size
        self.adjustSize()
        target_height = self.sizeHint().height()
        if target_height <= 0:
            target_height = 200  # Fallback if sizeHint isn't calculated yet
        
        # Initialize height to 0 before showing to avoid visual flash
        self.setFixedHeight(0)
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Animate custom height property
        self._slide_anim = QPropertyAnimation(self, b"dropdownHeight")
        self._slide_anim.setDuration(250)  # 250ms slide duration
        self._slide_anim.setStartValue(0)
        self._slide_anim.setEndValue(target_height)
        self._slide_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._slide_anim.finished.connect(self._on_animation_finished)
        self._slide_anim.start()

    def closeEvent(self, event):
        if self._is_closing:
            event.accept()
            return

        self._is_closing = True
        event.ignore()
        
        # Animate height to 0
        self._slide_anim = QPropertyAnimation(self, b"dropdownHeight")
        self._slide_anim.setDuration(200)  # 200ms close duration
        self._slide_anim.setStartValue(self.height())
        self._slide_anim.setEndValue(0)
        self._slide_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._slide_anim.finished.connect(self.real_close)
        self._slide_anim.start()

    def real_close(self):
        super().close()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from app.data.database import Database
    from app.ui.styles.theme import apply_dark_theme

    app = QApplication(sys.argv)
    apply_dark_theme(app)

    db = Database()
    db.initialize()

    window = ClientsPage(db)
    window.setWindowTitle("Clients Page Test")
    window.resize(1200, 800)
    window.show()

    sys.exit(app.exec())
