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
from app.ui.widgets.stat_card import StatCard


def _format_short_currency(val: float) -> str:
    """Format large numbers in short format — ₹1,20,339 should show as ₹1.2L, ₹1,14,896 as ₹1.1L."""
    if not val:
        return "₹0"
    if val >= 100000:
        return f"₹{val/100000:.1f}L"
    elif val >= 1000:
        return f"₹{val/1000:.1f}K"
    else:
        return f"₹{val:,.0f}"

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

        # Initialize filter state
        self._active_filter = "All"
        self._all_projects = []

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
        """Build page header: title + New Project button."""
        header_row = QHBoxLayout()
        header_row.setSpacing(0)
        header_row.setContentsMargins(0, 0, 0, 0)

        # Left block: title row
        left_block = QVBoxLayout()
        left_block.setSpacing(0)
        left_block.setContentsMargins(0, 0, 0, 0)

        # Title row: Projects
        title_row = QHBoxLayout()
        title_row.setSpacing(0)

        # Title: 32px / 40px line-height / -0.02em / 700 weight
        title = QLabel("Projects")
        title.setFont(QFont("Inter", 32, QFont.Bold))
        title.setStyleSheet("color: #e2e4f0; background: transparent; border: none; letter-spacing: -0.6px;")
        title.setFixedHeight(40)
        title_row.addWidget(title)
        title_row.addStretch()

        left_block.addLayout(title_row)
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
        """Build stats row: 4 stat cards matching Dashboard style."""
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(0, 0, 0, 0)

        self.card_total = StatCard(
            "Total Projects", "—",
            icon="task_alt",
            accent=Colors.ACCENT_PRIMARY_LIGHT,
        )
        self.card_in_progress = StatCard(
            "In Progress", "—",
            icon="pending_actions",
            accent=Colors.ACCENT_INFO,
        )
        self.card_completed = StatCard(
            "Completed", "—",
            icon="task_alt",
            accent=Colors.ACCENT_SUCCESS,
        )
        self.card_pending_payment = StatCard(
            "Pending Payment", "—",
            icon="payments",
            accent=Colors.ACCENT_WARNING,
        )

        for card in (self.card_total, self.card_in_progress, self.card_completed, self.card_pending_payment):
            card.setObjectName("statCard")
            card.setStyleSheet("background-color: #222336; border-radius: 12px;")
            card.setMinimumHeight(140)
            card.setMaximumHeight(140)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

            title_label = card._label
            value_label = card._value
            subtitle_label = card._sub

            title_label.setFont(QFont("Inter", 9))
            title_label.setStyleSheet("color: #8B8FA8; background: transparent; border: none;")

            value_label.setFont(QFont("Inter", 24, QFont.Bold))
            value_label.setStyleSheet("color: #FFFFFF; background: transparent; border: none; font-size: 26px;")

            subtitle_label.setFont(QFont("Inter", 8))
            subtitle_label.setStyleSheet("color: #6B7280; background: transparent; border: none;")

            card.layout().setContentsMargins(20, 16, 20, 16)
            card.layout().setSpacing(6)

            stats_layout.addWidget(card, 1)

        parent_layout.addLayout(stats_layout)


    def _build_projects_table(self, parent_layout: QVBoxLayout) -> None:
        """Build projects table with header and filter tabs."""
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

        # Filter tabs bar
        filter_bar = QWidget()
        filter_bar.setObjectName("table_filter_bar")
        filter_bar_layout = QHBoxLayout(filter_bar)
        filter_bar_layout.setContentsMargins(24, 16, 24, 16)
        filter_bar_layout.setSpacing(4)

        self._filter_tabs = []
        filter_statuses = ["All", "Not Started", "In Progress", "Review", "On Hold", "Completed", "Cancelled"]

        for fs in filter_statuses:
            btn = QPushButton(fs)
            btn.setObjectName("table_filter_tab")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setChecked(fs == "All")
            btn.setStyleSheet("""
                QPushButton#table_filter_tab {
                    background: transparent;
                    color: #6b6d85;
                    border: 1px solid transparent;
                    border-radius: 8px;
                    padding: 4px 12px;
                    font-size: 12px;
                    font-weight: 500;
                    min-height: 28px;
                }
                QPushButton#table_filter_tab:checked {
                    background: transparent;
                    color: #82d8ac;
                    border-color: #82d8ac;
                }
                QPushButton#table_filter_tab:hover:!checked {
                    background: rgba(200, 203, 223, 0.08);
                    color: #ffffff;
                }
            """)
            btn.clicked.connect(lambda checked, s=fs: self._apply_filter(s))
            filter_bar_layout.addWidget(btn)
            self._filter_tabs.append(btn)

        filter_bar_layout.addStretch()
        table_layout.addWidget(filter_bar)

        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "PROJECT", "CLIENT", "TYPE", "STATUS", "DEADLINE", "BUDGET", "ACTIONS"
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
                padding: 8px 12px;
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
                padding: 12px 12px;
                height: 48px;
            }
        """)

        # Column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive) # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch) # PROJECT
        header.setSectionResizeMode(2, QHeaderView.Interactive) # CLIENT
        header.setSectionResizeMode(3, QHeaderView.Interactive) # TYPE
        header.setSectionResizeMode(4, QHeaderView.Interactive) # STATUS
        header.setSectionResizeMode(5, QHeaderView.Interactive) # DEADLINE
        header.setSectionResizeMode(6, QHeaderView.Interactive) # BUDGET
        header.setSectionResizeMode(7, QHeaderView.Fixed) # ACTIONS

        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 140)
        self.table.setColumnWidth(4, 150)
        self.table.setColumnWidth(5, 150)
        self.table.setColumnWidth(6, 140)
        self.table.setColumnWidth(7, 100)

        table_layout.addWidget(self.table)
        parent_layout.addWidget(table_card)

    def _apply_filter(self, status: str) -> None:
        """Switch the active filter tab and re-render the table."""
        self._active_filter = status
        for tab in self._filter_tabs:
            tab.setChecked(tab.text() == status)

        if status == "All":
            filtered = self._all_projects
        else:
            filtered = [p for p in self._all_projects if p.get("status") == status]
        
        self._populate_table(filtered)


    def refresh(self) -> None:
        """Refresh all project data from database."""
        try:
            projects = self.repo.get_all()
            # Convert sqlite3.Row objects to dicts
            projects = [dict(p) for p in projects]
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load projects: {e}")
            projects = []

        # Store all projects for client-side filtering
        self._all_projects = projects

        # 1. TOTAL PROJECTS
        total_count = len(projects)
        self.card_total.set_value(str(total_count))
        
        # Calculate projects added this month vs last month
        try:
            res_total_this_month = self.db.execute("""
                SELECT COUNT(*) as cnt FROM projects 
                WHERE strftime('%m-%Y', created_date) = strftime('%m-%Y', 'now')
            """)
            this_month_total = res_total_this_month[0]["cnt"] if res_total_this_month else 0
            
            res_total_last_month = self.db.execute("""
                SELECT COUNT(*) as cnt FROM projects 
                WHERE strftime('%m-%Y', created_date) = strftime('%m-%Y', date('now','-1 month'))
            """)
            last_month_total = res_total_last_month[0]["cnt"] if res_total_last_month else 0
            
            if this_month_total > last_month_total:
                sub, color = f"▲ +{this_month_total - last_month_total} from last month", "#7dd3a8"
            elif this_month_total == last_month_total:
                sub, color = "→ Same as last month", "#9a9cb8"
            else:
                sub, color = f"▼ -{last_month_total - this_month_total} from last month", "#e87c8a"
        except Exception:
            sub, color = "—", "#9a9cb8"
        self.card_total.set_sub_text(sub, color)

        # 2. IN PROGRESS
        in_progress_count = sum(1 for p in projects if p.get("status") == "In Progress")
        self.card_in_progress.set_value(str(in_progress_count))
        
        # Overdue & at risk calculations
        today_str = date.today().isoformat()
        week_later_str = (date.today() + timedelta(days=7)).isoformat()
        
        overdue_count = 0
        at_risk_count = 0
        for p in projects:
            if p.get("status") == "In Progress":
                dl = p.get("deadline")
                if dl:
                    if dl < today_str:
                        overdue_count += 1
                    elif today_str <= dl <= week_later_str:
                        at_risk_count += 1
        
        if overdue_count > 0:
            sub, color = f"✕ {overdue_count} project(s) overdue", "#e87c8a"
        elif at_risk_count > 0:
            sub, color = f"⚠ {at_risk_count} due this week", "#9a9cb8"
        else:
            sub, color = "✓ All projects on track", "#7dd3a8"
        self.card_in_progress.set_sub_text(sub, color)

        # 3. COMPLETED
        completed_count = sum(1 for p in projects if p.get("status") == "Completed")
        self.card_completed.set_value(str(completed_count))
        
        # Calculate completed projects this month vs last month
        try:
            res_comp_this_month = self.db.execute("""
                SELECT COUNT(*) as cnt FROM projects 
                WHERE status='Completed'
                AND strftime('%m-%Y', created_date) = strftime('%m-%Y', 'now')
            """)
            this_month_comp = res_comp_this_month[0]["cnt"] if res_comp_this_month else 0
            
            res_comp_last_month = self.db.execute("""
                SELECT COUNT(*) as cnt FROM projects 
                WHERE status='Completed'
                AND strftime('%m-%Y', created_date) = strftime('%m-%Y', date('now','-1 month'))
            """)
            last_month_comp = res_comp_last_month[0]["cnt"] if res_comp_last_month else 0
            
            if this_month_comp > last_month_comp:
                sub, color = f"▲ +{this_month_comp - last_month_comp} from last month", "#7dd3a8"
            elif this_month_comp == last_month_comp:
                sub, color = "→ Same as last month", "#9a9cb8"
            else:
                sub, color = f"▼ -{last_month_comp - this_month_comp} from last month", "#e87c8a"
        except Exception:
            sub, color = "—", "#9a9cb8"
        self.card_completed.set_sub_text(sub, color)

        # 4. PENDING PAYMENT
        try:
            # SUM budget of completed projects with no paid invoice
            res_pending = self.db.execute("""
                SELECT COALESCE(SUM(budget), 0) as total FROM projects 
                WHERE status='Completed' 
                AND id NOT IN (SELECT DISTINCT project_id FROM invoices WHERE status='Paid')
            """)
            pending_amount = res_pending[0]["total"] if res_pending else 0.0
            
            # Fetch completed projects with no paid invoice for status detail
            pending_projects = self.db.execute("""
                SELECT p.id, p.deadline, i.status as invoice_status, i.due_date as invoice_due_date
                FROM projects p
                LEFT JOIN invoices i ON p.id = i.project_id
                WHERE p.status='Completed'
                AND p.id NOT IN (SELECT DISTINCT project_id FROM invoices WHERE status='Paid')
            """)
            
            overdue_payments = 0
            for row in pending_projects:
                inv_status = row["invoice_status"]
                inv_due = row["invoice_due_date"]
                proj_dl = row["deadline"]
                if inv_status == "Unpaid" and inv_due and inv_due < today_str:
                    overdue_payments += 1
                elif not inv_status and proj_dl and proj_dl < today_str:
                    overdue_payments += 1
            
            self.card_pending_payment.set_value(_format_short_currency(pending_amount))
            
            if pending_amount == 0:
                sub, color = "✓ Paid in full", "#7dd3a8"
            elif overdue_payments > 0:
                sub, color = f"✕ {overdue_payments} payment(s) overdue", "#e87c8a"
            else:
                sub, color = f"⚠ {len(pending_projects)} awaiting payment", "#9a9cb8"
        except Exception as e:
            print(f"Error calculating pending payment: {e}")
            self.card_pending_payment.set_value("₹0")
            sub, color = "—", "#9a9cb8"
        self.card_pending_payment.set_sub_text(sub, color)

        # Re-apply filter to table
        self._apply_filter(self._active_filter)

    def _populate_table(self, projects: list) -> None:
        """Populate table with project data."""
        # Properly clear contents and row count
        self.table.clearContents()
        self.table.clearSpans()
        self.table.setRowCount(0)

        if not projects:
            self.table.setRowCount(1)
            msg = "No projects match this filter." if self._active_filter != "All" else \
                  "No projects yet — click 'New Project' to get started"
            empty_item = QTableWidgetItem(msg)
            empty_item.setFlags(Qt.ItemIsEnabled)
            empty_item.setForeground(QColor("#9a9cb8"))
            empty_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 8)
            return

        self.table.setRowCount(len(projects))
        
        for i, p in enumerate(projects):
            # Set row to alternate background
            if i % 2 == 1:
                for col in range(8):
                    item = QTableWidgetItem()
                    item.setBackground(QColor(26, 27, 38, 51))  # rgba(26,27,38,0.20)
                    self.table.setItem(i, col, item)

            # ID column: 14px tabular-nums / 500 weight
            id_item = QTableWidgetItem(f"SD-{p.get('id', 0):03d}")
            id_item.setFont(QFont("Inter", 14, QFont.Medium))
            id_item.setForeground(QColor("#9a9cb8"))
            id_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 0, id_item)

            # PROJECT column: show project name only (no subtitle description)
            project_name = p.get("name", "Unnamed Project")
            project_item = QTableWidgetItem(project_name)
            project_item.setFont(QFont("Inter", 14, QFont.Medium))
            project_item.setForeground(QColor("#e2e4f0"))
            project_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 1, project_item)

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

            # BUDGET column: formatted with rupee symbol
            budget = p.get("budget")
            if budget is not None and budget > 0:
                budget_str = f"₹{int(budget):,}"
            else:
                budget_str = "₹0"
            budget_item = QTableWidgetItem(budget_str)
            budget_item.setFont(QFont("Inter", 14, QFont.Medium))
            budget_item.setForeground(QColor("#e2e4f0"))
            budget_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 6, budget_item)

            # ACTIONS column: edit + delete buttons (hidden by default, shown on hover)
            actions_widget = self._create_actions_cell(p.get("id", 0))
            self.table.setCellWidget(i, 7, actions_widget)


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
