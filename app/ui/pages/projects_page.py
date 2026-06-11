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

from PySide6.QtCore import Qt, QDate, QSize, QPropertyAnimation, QEasingCurve, QEvent, Property
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


def _format_indian(n: int) -> str:
    """Format an integer with Indian comma grouping: 1,20,000."""
    s = str(n)
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while rest:
        groups.append(rest[-2:])
        rest = rest[:-2]
    groups.reverse()
    return ",".join(groups) + "," + last3


class CustomProjectsTableWidget(QTableWidget):
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
        self._search_text = ""
        self._filter_status = "All"
        self._filter_type = "All"
        self._filter_date_from = ""
        self._filter_date_to = ""
        self._all_projects_raw = []
        self._all_projects = []
        self.filter_dropdown = None
        self._active_filter = "All"

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
        self._build_stats_row(layout)
        self._build_search_and_action_row(layout)
        self._build_filter_tabs(layout)
        self._build_projects_table(layout)

        scroll.setWidget(content_widget)
        page_layout.addWidget(scroll)

        # Load data
        self.refresh()


    def _build_search_and_action_row(self, parent_layout: QVBoxLayout) -> None:
        """Build search and action row matching clients_page.py."""
        row = QHBoxLayout()
        row.setSpacing(16)

        # Search field with embedded icon
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search projects...")
        self.search_input.setFixedWidth(500)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {Colors.BG_DARK};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 10px;
                padding: 10px 14px 10px 32px;
                color: {Colors.TEXT_PRIMARY};
                font-family: 'Inter';
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {Colors.ACCENT_PRIMARY_LIGHT};
            }}
        """)
        self.search_input.textChanged.connect(self._on_search)

        search_icon = QLabel()
        search_icon.setPixmap(_load_svg_icon("search", size=16, color="#6b6d85"))
        search_icon.setStyleSheet("background: transparent; border: none; padding-left: 8px;")

        search_layout = QHBoxLayout(self.search_input)
        search_layout.addWidget(search_icon, 0, Qt.AlignLeft | Qt.AlignVCenter)
        search_layout.addStretch()
        search_layout.setContentsMargins(0, 0, 0, 0)
        self.search_input.setTextMargins(28, 0, 0, 0)

        row.addWidget(self.search_input)
        row.addStretch()

        # New Project button
        add_btn = QPushButton("+ New Project")
        add_btn.setObjectName("add_project_btn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(36)
        add_btn.setStyleSheet(f"""
            QPushButton#add_project_btn {{
                background-color: {Colors.ACCENT_PRIMARY};
                color: {Colors.TEXT_ON_PRIMARY};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 600;
                font-size: 13px;
                border: none;
            }}
            QPushButton#add_project_btn:hover {{
                background-color: {Colors.ACCENT_PRIMARY_HOVER};
            }}
            QPushButton#add_project_btn:pressed {{
                background-color: {Colors.ACCENT_PRIMARY_PRESSED};
            }}
        """)
        add_btn.clicked.connect(self._add_project)
        row.addWidget(add_btn)

        parent_layout.addLayout(row)

    def _build_filter_tabs(self, parent_layout: QVBoxLayout) -> None:
        """Build filter tabs matching Dashboard style."""
        filter_bar = QWidget()
        filter_bar.setObjectName("projects_filter_bar")
        filter_bar.setStyleSheet("background: transparent;")
        filter_bar_layout = QHBoxLayout(filter_bar)
        filter_bar_layout.setContentsMargins(0, 0, 0, 0)
        filter_bar_layout.setSpacing(8)

        self._filter_tabs: list[QPushButton] = []
        self.current_filter = "All"
        filter_statuses = ["All", "Not Started", "In Progress", "Review", "On Hold", "Completed", "Cancelled"]

        for fs in filter_statuses:
            btn = QPushButton(fs)
            btn.setObjectName("project_filter_tab")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setChecked(fs == "All")
            btn.setStyleSheet("""
                QPushButton#project_filter_tab {
                    background: transparent;
                    color: #9a9cb8;
                    border: 1px solid transparent;
                    border-radius: 6px;
                    padding: 4px 12px;
                    font-size: 13px;
                    font-weight: 500;
                    min-height: 28px;
                }
                QPushButton#project_filter_tab:checked {
                    background: transparent;
                    color: #7c8af4;
                    border: 1px solid #7c8af4;
                }
                QPushButton#project_filter_tab:hover:!checked {
                    background: #1a1b26;
                    color: #e2e4f0;
                }
            """)
            btn.clicked.connect(lambda checked, s=fs: self.filter_by_status(s))
            filter_bar_layout.addWidget(btn)
            self._filter_tabs.append(btn)

        filter_bar_layout.addStretch()
        parent_layout.addWidget(filter_bar)

    def filter_by_status(self, status: str) -> None:
        """Filter table rows by status."""
        self.current_filter = status
        
        # Update tab checked states
        for tab in self._filter_tabs:
            tab.setChecked(tab.text() == status)
        
        # Filter table rows
        for row in range(self.table.rowCount()):
            if status == "All":
                self.table.setRowHidden(row, False)
            else:
                # STATUS column uses a widget (badge), need to get the widget
                status_widget = self.table.cellWidget(row, 4)
                if status_widget:
                    # Find QLabel inside the widget (the badge label)
                    badge_label = status_widget.findChild(QLabel)
                    if badge_label:
                        row_status = badge_label.text()
                        hidden = row_status != status
                        self.table.setRowHidden(row, hidden)
                    else:
                        self.table.setRowHidden(row, True)
                else:
                    self.table.setRowHidden(row, True)

    def _build_stats_row(self, parent_layout: QVBoxLayout) -> None:
        """Build stats row: 4 stat cards with hover animation matching Dashboard style."""
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(0, 0, 0, 0)

        # Create the 4 stat cards using DashboardStatCard with hover animation
        from app.ui.pages.dashboard_page import DashboardStatCard
        
        self.card_total = DashboardStatCard(
            "Total Projects", "—",
            icon="task_alt",
            accent=Colors.ACCENT_PRIMARY_LIGHT,
        )
        self.card_in_progress = DashboardStatCard(
            "In Progress", "—",
            icon="pending_actions",
            accent=Colors.ACCENT_INFO,
        )
        self.card_completed = DashboardStatCard(
            "Completed", "—",
            icon="task_alt",
            accent=Colors.ACCENT_SUCCESS,
        )
        self.card_total_budget = DashboardStatCard(
            "Total Budget", "—",
            icon="account_balance_wallet",
            accent=Colors.ACCENT_WARNING,
        )

        for card in (self.card_total, self.card_in_progress, self.card_completed, self.card_total_budget):
            stats_layout.addWidget(card, 1)

        parent_layout.addLayout(stats_layout)


    def _build_projects_table(self, parent_layout: QVBoxLayout) -> None:
        """Build projects table card."""
        table_card = QFrame()
        table_card.setObjectName("dashboard_table_card")
        table_card.setStyleSheet("QFrame#dashboard_table_card { background-color: #222336; border-radius: 12px; border: 1px solid #2d2e42; }")
        table_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # Table widget
        self.table = CustomProjectsTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "PROJECT", "CLIENT", "TYPE", "STATUS", "DEADLINE", "BUDGET", "ACTIONS"
        ])
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        
        # Hide the horizontal and vertical headers
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)
        
        self.table.setShowGrid(False)
        self.table.setFrameShape(QFrame.NoFrame)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(48)

        # Apply custom style sheet matching dashboard_page.py
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                color: #e2e4f0;
                font-size: 13px;
                outline: none;
            }
            QTableWidget::item {
                border: none;
                padding: 8px 12px;
                border-bottom: 1px solid #2d2e42;
            }
            QTableWidget::item:selected {
                background-color: rgba(124, 138, 244, 0.12);
                border: none;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.04);
                border: none;
            }
        """)

        # Set fixed column widths to prevent collapse during filtering
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        from PySide6.QtWidgets import QHeaderView
        
        # Set all columns to Fixed mode first
        for col in range(8):
            header.setSectionResizeMode(col, QHeaderView.Fixed)
        
        # Set fixed column widths
        self.table.setColumnWidth(0, 90)   # ID
        self.table.setColumnWidth(1, 220)  # PROJECT
        self.table.setColumnWidth(2, 160)  # CLIENT
        self.table.setColumnWidth(3, 110)  # TYPE
        self.table.setColumnWidth(4, 120)  # STATUS
        self.table.setColumnWidth(5, 130)  # DEADLINE
        self.table.setColumnWidth(6, 110)  # BUDGET
        self.table.setColumnWidth(7, 80)   # ACTIONS
        
        # Make PROJECT column stretch to fill remaining space
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        table_layout.addWidget(self.table)
        parent_layout.addWidget(table_card)

    def _on_search(self, text: str) -> None:
        self._search_text = text.strip().lower()
        self._apply_all_filters()

    def _toggle_filter_dropdown(self) -> None:
        if self.filter_dropdown is None:
            self.filter_dropdown = ProjectFilterDropdown(self, self.filter_btn)
        
        if self.filter_dropdown.isVisible():
            self.filter_dropdown.close()
        else:
            self.filter_dropdown.show_below_anchor()

    def apply_filter_rules(self, status: str, project_type: str, d_from: str, d_to: str) -> None:
        self._filter_status = status
        self._filter_type = project_type
        self._filter_date_from = d_from
        self._filter_date_to = d_to
        self._apply_all_filters()

    def _apply_all_filters(self) -> None:
        filtered = []
        for p in self._all_projects_raw:
            # columns: 0: id, 1: client_id, 2: name, 3: type, 4: description, 5: status, 6: deadline, 7: budget, 8: created_date, 9: client_name
            project_name = p[2].lower() if p[2] else ""
            project_desc = p[4].lower() if p[4] else ""
            client_name = p[9].lower() if p[9] else ""
            project_type = p[3] if p[3] else ""
            status = p[5] if p[5] else ""
            deadline = p[6] if p[6] else ""

            # Search check
            if self._search_text:
                if (self._search_text not in project_name and
                    self._search_text not in project_desc and
                    self._search_text not in client_name and
                    self._search_text not in project_type.lower()):
                    continue

            # Dropdown filter check
            # Status check
            if self._filter_status != "All":
                if status != self._filter_status:
                    continue

            # Type check
            if self._filter_type != "All":
                if project_type != self._filter_type:
                    continue

            # Deadline From Date check
            if self._filter_date_from:
                if deadline < self._filter_date_from:
                    continue

            # Deadline To Date check
            if self._filter_date_to:
                if deadline > self._filter_date_to:
                    continue

            filtered.append(p)

        self._populate_projects_table(filtered)

    def refresh(self) -> None:
        """Refresh all project data from database."""
        try:
            # Query database directly, joining projects with clients, returning columns in exact index order:
            # 0: id, 1: client_id, 2: name, 3: type, 4: description, 5: status, 6: deadline, 7: budget, 8: created_date, 9: client_name
            projects = self.db.execute("""
                SELECT p.id, p.client_id, p.name, p.type, p.description, p.status, p.deadline, p.budget, p.created_date, c.name as client_name
                FROM projects p
                LEFT JOIN clients c ON p.client_id = c.id
                ORDER BY p.created_date DESC
            """)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load projects: {e}")
            projects = []

        # Store all projects for client-side filtering
        self._all_projects_raw = projects
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
        in_progress_count = sum(1 for p in projects if p[5] == "In Progress")
        self.card_in_progress.set_value(str(in_progress_count))
        
        # Overdue & at risk calculations
        today_str = date.today().isoformat()
        week_later_str = (date.today() + timedelta(days=7)).isoformat()
        
        overdue_count = 0
        at_risk_count = 0
        for p in projects:
            if p[5] == "In Progress":
                dl = p[6]
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
        completed_count = sum(1 for p in projects if p[5] == "Completed")
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

        # 4. TOTAL BUDGET
        try:
            # SUM budget of all projects
            res_budget = self.db.execute("""
                SELECT COALESCE(SUM(budget), 0) as total FROM projects
            """)
            total_budget = res_budget[0]["total"] if res_budget else 0.0
            
            # Calculate budget added this month vs last month
            res_budget_this_month = self.db.execute("""
                SELECT COALESCE(SUM(budget), 0) as total FROM projects 
                WHERE strftime('%m-%Y', created_date) = strftime('%m-%Y', 'now')
            """)
            this_month_budget = res_budget_this_month[0]["total"] if res_budget_this_month else 0.0
            
            res_budget_last_month = self.db.execute("""
                SELECT COALESCE(SUM(budget), 0) as total FROM projects 
                WHERE strftime('%m-%Y', created_date) = strftime('%m-%Y', date('now','-1 month'))
            """)
            last_month_budget = res_budget_last_month[0]["total"] if res_budget_last_month else 0.0
            
            self.card_total_budget.set_value(_format_short_currency(total_budget))
            
            if this_month_budget > last_month_budget:
                diff = this_month_budget - last_month_budget
                sub, color = f"▲ +{_format_short_currency(diff)} from last month", "#7dd3a8"
            elif this_month_budget == last_month_budget:
                sub, color = "→ Same as last month", "#9a9cb8"
            else:
                diff = last_month_budget - this_month_budget
                sub, color = f"▼ -{_format_short_currency(diff)} from last month", "#e87c8a"
        except Exception as e:
            print(f"Error calculating total budget: {e}")
            self.card_total_budget.set_value("₹0")
            sub, color = "—", "#9a9cb8"
        self.card_total_budget.set_sub_text(sub, color)

        # Re-apply all filters to table
        self._apply_all_filters()


    def _populate_projects_table(self, projects: list) -> None:
        """Populate table with project data."""
        self.table.clearSpans()
        if len(projects) == 0:
            self.table.setRowCount(1)
            self.table.setRowHeight(0, 120)
            self.table.setSpan(0, 0, 1, 8)
            msg = "No projects match this filter." if self._active_filter != "All" else \
                  "No projects yet — click 'New Project' to get started"
            empty_label = QLabel(msg)
            empty_label.setStyleSheet("color: #6B7280; font-size: 13px; background: transparent; border: none;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(0, 0, empty_label)
        else:
            self.table.setRowCount(len(projects))
            self.table.verticalHeader().setDefaultSectionSize(48)

            for i, row in enumerate(projects):
                # Map columns correctly
                project_id   = f"SD-{row[0]:03d}"
                project_name = row[2]
                project_type = row[3]
                status       = row[5]
                deadline     = row[6]
                budget       = row[7]
                client_name  = row[9] if row[9] else "No Client"

                # 0 - ID column (e.g. SD-042)
                id_item = QTableWidgetItem(project_id)
                id_item.setForeground(QColor(Colors.TEXT_MUTED))
                id_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                id_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(i, 0, id_item)

                # 1 - PROJECT column: single-line name (bold white)
                name_item = QTableWidgetItem(project_name)
                name_item.setForeground(QColor(Colors.TEXT_PRIMARY))
                font = name_item.font()
                font.setWeight(QFont.DemiBold)
                name_item.setFont(font)
                name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                name_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(i, 1, name_item)

                # 2 - CLIENT column: avatar + name
                client_widget = QWidget()
                client_widget.setObjectName("table_client_container")
                client_widget.setStyleSheet("background: transparent; border: none;")
                client_layout = QHBoxLayout(client_widget)
                client_layout.setContentsMargins(6, 0, 6, 0)
                client_layout.setSpacing(8)
                
                initials = "".join([word[0] for word in client_name.split()[:2]]).upper()
                
                # Determine avatar color based on client name
                avatar_colors = ["rgba(125,211,227,0.30)", "rgba(124,138,244,0.30)", "rgba(232,124,138,0.30)", "#908f9e"]
                avatar_color = avatar_colors[hash(client_name) % len(avatar_colors)]
                
                avatar_label = QLabel()
                avatar_pixmap = _create_avatar_pixmap(initials, avatar_color, size=28)
                avatar_label.setPixmap(avatar_pixmap)
                avatar_label.setFixedSize(28, 28)
                avatar_label.setStyleSheet("background: transparent; border: none;")
                client_layout.addWidget(avatar_label)
                
                client_label = QLabel(client_name)
                client_label.setObjectName("table_client_name")
                client_label.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 13px; font-weight: 500; background: transparent; border: none;")
                client_layout.addWidget(client_label)
                client_layout.addStretch()
                
                self.table.setCellWidget(i, 2, client_widget)

                # 3 - TYPE column
                type_item = QTableWidgetItem(project_type if project_type else "General")
                type_item.setForeground(QColor(Colors.TEXT_SECONDARY))
                type_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                type_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(i, 3, type_item)

                # 4 - STATUS column: badge
                status_widget = self._create_status_badge(status if status else "Not Started")
                self.table.setCellWidget(i, 4, status_widget)

                # 5 - DEADLINE column
                is_overdue = False
                formatted_deadline = "—"
                if deadline:
                    deadline_date = QDate.fromString(deadline, "yyyy-MM-dd")
                    if deadline_date.isValid():
                        formatted_deadline = deadline_date.toString("MMM dd, yyyy")
                        is_overdue = deadline_date < QDate.currentDate() and status != "Completed"
                    else:
                        formatted_deadline = deadline

                deadline_item = QTableWidgetItem(formatted_deadline)
                if is_overdue:
                    deadline_item.setForeground(QColor("#e87c8a"))  # ACCENT_RED
                    font = QFont()
                    font.setBold(True)
                    deadline_item.setFont(font)
                else:
                    deadline_item.setForeground(QColor(Colors.TEXT_SECONDARY))
                deadline_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                deadline_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(i, 5, deadline_item)

                # 6 - BUDGET column
                if budget is not None and budget > 0:
                    budget_str = "₹" + _format_indian(int(budget))
                else:
                    budget_str = "₹0"
                budget_item = QTableWidgetItem(budget_str)
                budget_item.setForeground(QColor(Colors.TEXT_PRIMARY))
                budget_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                budget_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                self.table.setItem(i, 6, budget_item)

                # 7 - ACTIONS column
                actions_widget = self._create_actions_cell(row[0])
                self.table.setCellWidget(i, 7, actions_widget)

        self.table.updateGeometry()

    # Alias helper in case _populate_table is called elsewhere or in tests
    _populate_table = _populate_projects_table


    def _create_status_badge(self, status: str) -> QWidget:
        """Styled pill badge matching the Stitch design with outline and proper spacing."""
        border_colors: dict[str, tuple[str, str]] = {
            # (border-color, text-color)
            "Completed":   ("#82d8ac", "#82d8ac"),
            "In Progress": ("#7c8af4", "#bcc2ff"),
            "Active":      ("#7c8af4", "#bcc2ff"),
            "Not Started": ("#555770", "#8B8FA8"),
            "On Hold":     ("#f0c878", "#f0c878"),
            "Review":      ("#7dd3e3", "#7dd3e3"),
            "Revision":    ("#7dd3e3", "#7dd3e3"),
            "Delayed":     ("#e87c8a", "#e87c8a"),
            "Cancelled":   ("#e87c8a", "#e87c8a"),
        }
        border, fg = border_colors.get(status, ("#555770", "#8B8FA8"))

        container = QWidget()
        container.setObjectName("table_status_container")
        container.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

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
        lay.addWidget(badge)
        return container

    def _create_actions_cell(self, project_id: int) -> QWidget:
        """Create actions cell with edit and delete buttons."""
        container = QWidget()
        container.setObjectName("table_actions_container")
        container.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        edit_btn = QPushButton()
        edit_btn.setObjectName("table_action_icon_btn")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setToolTip("Edit Project")
        edit_btn.setIcon(QIcon(_load_svg_icon("edit", size=16, color="#6b6d85")))
        edit_btn.setIconSize(QSize(16, 16))
        edit_btn.setFixedSize(28, 28)
        edit_btn.setStyleSheet("""
            QPushButton#table_action_icon_btn {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton#table_action_icon_btn:hover {
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        edit_btn.clicked.connect(lambda: self._edit_project_by_id(project_id))

        del_btn = QPushButton()
        del_btn.setObjectName("table_action_icon_btn")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Delete Project")
        del_btn.setIcon(QIcon(_load_svg_icon("delete", size=16, color="#6b6d85")))
        del_btn.setIconSize(QSize(16, 16))
        del_btn.setFixedSize(28, 28)
        del_btn.setStyleSheet("""
            QPushButton#table_action_icon_btn {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton#table_action_icon_btn:hover {
                background: rgba(232, 124, 138, 0.15);
            }
        """)
        del_btn.clicked.connect(lambda: self._delete_project_by_id(project_id))

        layout.addWidget(edit_btn)
        layout.addWidget(del_btn)
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
        title.setStyleSheet("color: #e2e4f0; font-size: 20px; font-weight: 700; background: transparent; border: none;")
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
        helper.setStyleSheet("color: #6b6d85; font-size: 11px; font-style: italic; background: transparent; border: none;")
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
