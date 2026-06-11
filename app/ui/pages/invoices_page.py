"""Invoices Page — Studio Graphite redesign matching the Stitch design system.

Features:
- Page header (title only, count and subtitle removed).
- 4 stat cards (Total Earned, Pending, Overdue, Total Invoices) with live calculations.
- Full-width Monthly Revenue bar chart (last 6 months, Matplotlib, styled background).
- Search + Filter row (search bar on left, filter tabs in center, + Create Invoice on right).
- Styled invoices table (avatar + client name, right-aligned total, red overdue due dates, StatusPill).
- Create/Edit Dialog with dependent Client-Project dropdowns and action buttons inside Edit mode.
"""
from __future__ import annotations

import datetime
from pathlib import Path
import sys

from PySide6.QtCore import Qt, QDate, QSize
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

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from app.config import ASSETS_DIR, GST_RATE
from app.data.database import Database
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.project_repo import ProjectRepository
from app.data.repositories.client_repo import ClientRepository
from app.ui.styles.theme import Colors
from app.ui.widgets.page_header import PageHeader
from app.ui.widgets.status_pill import StatusPill
from app.core.signals import emit_data_changed
from app.core.email_service import EmailService
from app.core.invoice_service import InvoiceService
from app.core.pdf_exporter import PDFExporter
from app.core.settings_service import SettingsService

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

    # Initials text (contrast text)
    painter.setPen(QColor("#12131d"))
    font = QFont("Inter", 9)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), Qt.AlignCenter, initials)

    painter.end()
    return pixmap


class MonthlyRevenueChart(FigureCanvas):
    """Matplotlib bar chart showing paid invoice totals per month for last 6 months."""

    def __init__(self, db: Database, parent=None):
        fig = Figure(figsize=(8.0, 3.0), facecolor="#1a1b26", dpi=100)
        super().__init__(fig)
        self.setParent(parent)
        self.db = db
        self.ax = fig.add_subplot(111)
        self.ax.set_facecolor("#1a1b26")
        self.setMinimumSize(400, 200)
        self.refresh()

    def refresh(self) -> None:
        try:
            rows = self.db.execute(
                """
                SELECT strftime('%Y-%m', date_issued) as month, SUM(total) as income
                FROM invoices
                WHERE status = 'Paid'
                GROUP BY month
                ORDER BY month
                """
            )
        except Exception:
            rows = []

        # Build last-6-month buckets (filling zeros)
        buckets = self._last_n_months(6)
        data = {row["month"]: float(row["income"]) for row in rows}
        values = [data.get(m, 0.0) for m in buckets]

        self.ax.clear()
        self.ax.set_facecolor("#1a1b26")

        # Hide axis lines (spines) except bottom
        for spine in ("top", "right", "left"):
            self.ax.spines[spine].set_visible(False)
        self.ax.spines["bottom"].set_color("#2d2e42")

        # Map buckets to English month names
        month_names_map = {
            "01": "Jan", "02": "Feb", "03": "Mar", "04": "Apr", "05": "May", "06": "Jun",
            "07": "Jul", "08": "Aug", "09": "Sep", "10": "Oct", "11": "Nov", "12": "Dec"
        }
        labels = [month_names_map[m.split("-")[1]] for m in buckets]

        if not any(values):
            self.ax.text(
                0.5, 0.5,
                "No monthly revenue data available",
                ha="center", va="center",
                color="#6b6d85", fontsize=11,
                transform=self.ax.transAxes,
            )
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        else:
            x = range(len(labels))
            self.ax.bar(x, values, color="#7c8af4", width=0.4, zorder=3)
            self.ax.set_xticks(x)
            self.ax.set_xticklabels(labels)
            self.ax.tick_params(colors="#9a9cb8", labelsize=9)
            
            # Format Y-axis with rupee amounts in short format
            def rupee_formatter(value, _pos):
                if abs(value) >= 100000:
                    return f"₹{value/100000:.1f}L"
                if abs(value) >= 1000:
                    return f"₹{value/1000:.0f}K"
                return f"₹{value:.0f}"
            self.ax.yaxis.set_major_formatter(FuncFormatter(rupee_formatter))
            self.ax.grid(True, axis="y", color="#2d2e42", linewidth=0.5, alpha=0.5, zorder=0)

        self.figure.tight_layout(pad=1.0)
        self.draw_idle()

    @staticmethod
    def _last_n_months(n: int) -> list[str]:
        from datetime import date
        today = date.today()
        months = []
        year, month = today.year, today.month
        for _ in range(n):
            months.append(f"{year:04d}-{month:02d}")
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        return list(reversed(months))


class CustomInvoicesTableWidget(QTableWidget):
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


class InvoicesPage(QWidget):
    """Invoice list redesign matching Studio Graphite design system."""

    def __init__(self, db: Database):
        super().__init__()
        self.setObjectName("invoices_page")
        self.db = db
        self.repo = InvoiceRepository(db)
        self.project_repo = ProjectRepository(db)
        self.client_repo = ClientRepository(db)
        self.service = InvoiceService(db)
        self.pdf_exporter = PDFExporter()
        self.settings = SettingsService(db)
        self.email = EmailService(db)

        # Filters state
        self._search_text = ""
        self.current_filter = "All"
        self._all_invoices_raw = []

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
        
        # Scrollbar styling
        scroll.setStyleSheet("""
            QScrollBar:vertical {
                width: 6px;
                background: #12131d;
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

        # Create content widget
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(28)
        layout.setAlignment(Qt.AlignTop)

        # ─── Header (Title only) ──────────────────────────────────────────
        self.header = PageHeader(title="Invoices")
        layout.addWidget(self.header)

        # ─── Stat cards row ────────────────────────────────────────────────
        # Using DashboardStatCard from dashboard_page.py for consistency
        from app.ui.pages.dashboard_page import DashboardStatCard
        
        self.card_earned = DashboardStatCard(
            "Total Earned", "₹0",
            icon="payments",
            accent=Colors.ACCENT_SUCCESS,
        )
        self.card_pending = DashboardStatCard(
            "Pending", "₹0",
            icon="pending_actions",
            accent=Colors.ACCENT_WARNING,
        )
        self.card_overdue = DashboardStatCard(
            "Overdue", "₹0",
            icon="error",
            accent=Colors.ACCENT_DANGER,
        )
        self.card_total = DashboardStatCard(
            "Total Invoices", "0",
            icon="description",
            accent=Colors.ACCENT_PRIMARY_LIGHT,
        )

        stat_row = QHBoxLayout()
        stat_row.setSpacing(16)
        stat_row.setContentsMargins(0, 0, 0, 0)
        for c in (self.card_earned, self.card_pending, self.card_overdue, self.card_total):
            stat_row.addWidget(c, 1)
        layout.addLayout(stat_row)

        # ─── Monthly Revenue Chart Card ──────────────────────────────────
        chart_card = QFrame()
        chart_card.setObjectName("monthly_revenue_chart_card")
        chart_card.setStyleSheet("""
            QFrame#monthly_revenue_chart_card {
                background-color: #1a1b26;
                border: 1px solid rgba(69, 70, 82, 0.3);
                border-radius: 8px;
                padding: 24px;
            }
        """)
        chart_layout = QVBoxLayout(chart_card)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        chart_layout.setSpacing(12)

        chart_title = QLabel("Monthly Revenue — Last 6 Months")
        chart_title.setStyleSheet("""
            color: #e2e1f1;
            font-size: 16px;
            font-weight: 500;
            background: transparent;
            border: none;
        """)
        chart_layout.addWidget(chart_title)

        self.revenue_chart = MonthlyRevenueChart(self.db)
        chart_layout.addWidget(self.revenue_chart)
        layout.addWidget(chart_card)

        # ─── Search and Filters Row ────────────────────────────────────────
        self._build_search_and_filter_row(layout)

        # ─── Invoices Table Card ──────────────────────────────────────────
        self._build_invoices_table(layout)

        # Set up scroll area
        scroll.setWidget(content_widget)
        page_layout.addWidget(scroll)

        self.refresh()

    def _build_search_and_filter_row(self, parent_layout: QVBoxLayout) -> None:
        row = QHBoxLayout()
        row.setSpacing(16)

        # Search field with icon
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search invoices or clients...")
        self.search_input.setFixedWidth(400)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1b26;
                border: 1px solid rgba(69, 70, 82, 0.3);
                border-radius: 8px;
                padding: 10px 14px 10px 32px;
                color: #e2e1f1;
                font-family: 'Inter';
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #7c8af4;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #9a9cb8;
            }
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

        # Filter tabs
        self._filter_tabs: list[QPushButton] = []
        filter_statuses = ["All", "Paid", "Unpaid", "Overdue", "Cancelled"]
        
        filter_bar_widget = QWidget()
        filter_bar_layout = QHBoxLayout(filter_bar_widget)
        filter_bar_layout.setContentsMargins(12, 0, 0, 0)
        filter_bar_layout.setSpacing(8)

        for fs in filter_statuses:
            btn = QPushButton(fs)
            btn.setObjectName("invoice_filter_tab")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setChecked(fs == "All")
            btn.setStyleSheet("""
                QPushButton#invoice_filter_tab {
                    background: transparent;
                    color: #9a9cb8;
                    border: 1px solid transparent;
                    border-radius: 6px;
                    padding: 4px 12px;
                    font-size: 13px;
                    font-weight: 500;
                    min-height: 28px;
                }
                QPushButton#invoice_filter_tab:checked {
                    background: #333440;
                    color: #e2e1f1;
                    border: 1px solid transparent;
                }
                QPushButton#invoice_filter_tab:hover:!checked {
                    background: #1e1f2a;
                    color: #e2e4f0;
                }
            """)
            btn.clicked.connect(lambda checked, s=fs: self.filter_by_status(s))
            filter_bar_layout.addWidget(btn)
            self._filter_tabs.append(btn)
            
        row.addWidget(filter_bar_widget)
        row.addStretch()

        # Create Invoice Button
        add_btn = QPushButton("+ Create Invoice")
        add_btn.setObjectName("create_invoice_btn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(40)
        add_btn.setStyleSheet("""
            QPushButton#create_invoice_btn {
                background-color: #7c8af4;
                color: #12131d;
                border-radius: 8px;
                padding: 10px 24px;
                font-weight: 700;
                font-size: 14px;
                border: none;
            }
            QPushButton#create_invoice_btn:hover {
                opacity: 0.9;
            }
        """)
        add_btn.clicked.connect(self._create_invoice)
        row.addWidget(add_btn)

        parent_layout.addLayout(row)

    def _build_invoices_table(self, parent_layout: QVBoxLayout) -> None:
        table_card = QFrame()
        table_card.setObjectName("invoices_table_card")
        table_card.setStyleSheet("QFrame#invoices_table_card { background-color: #1a1b26; border-radius: 8px; border: 1px solid rgba(69, 70, 82, 0.3); }")
        table_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        table_layout = QVBoxLayout(table_card)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # Table widget
        self.table = CustomInvoicesTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "#", "INVOICE NO.", "CLIENT", "PROJECT", "TOTAL", "DUE DATE", "STATUS", "ACTIONS"
        ])
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(True)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.verticalHeader().setDefaultSectionSize(48)
        self.table.setFrameShape(QFrame.NoFrame)

        self.table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
                color: #e2e1f1;
                font-size: 14px;
                outline: none;
            }
            QTableWidget::item {
                border: none;
                padding: 16px 24px;
                border-bottom: 1px solid rgba(69, 70, 82, 0.1);
            }
            QTableWidget::item:selected {
                background-color: rgba(124, 138, 244, 0.12);
                border: none;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: rgba(124, 138, 244, 0.04);
                border: none;
            }
            QHeaderView::section {
                background-color: transparent;
                color: #e2e1f1;
                padding: 16px 24px;
                border: none;
                border-bottom: 1px solid rgba(69, 70, 82, 0.3);
                font-size: 11px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
        """)

        # Column modes and sizes
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        for col in range(8):
            header.setSectionResizeMode(col, QHeaderView.Fixed)
            
        self.table.setColumnWidth(0, 60)   # # (ID)
        self.table.setColumnWidth(1, 140)  # INVOICE NO.
        self.table.setColumnWidth(2, 200)  # CLIENT
        self.table.setColumnWidth(3, 200)  # PROJECT
        self.table.setColumnWidth(4, 120)  # TOTAL
        self.table.setColumnWidth(5, 120)  # DUE DATE
        self.table.setColumnWidth(6, 120)  # STATUS
        self.table.setColumnWidth(7, 80)   # ACTIONS

        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)

        table_layout.addWidget(self.table)
        parent_layout.addWidget(table_card)

    def _on_search(self, text: str) -> None:
        self._search_text = text.strip().lower()
        self._apply_all_filters()

    def filter_by_status(self, status: str) -> None:
        self.current_filter = status
        for tab in self._filter_tabs:
            tab.setChecked(tab.text() == status)
        self._apply_all_filters()

    def _apply_all_filters(self) -> None:
        filtered = []
        today_str = datetime.date.today().isoformat()

        for inv in self._all_invoices_raw:
            # 1. Search text filter
            inv_no = inv["invoice_number"].lower() if inv["invoice_number"] else ""
            client = inv["client_name"].lower() if inv["client_name"] else ""
            project = inv["project_name"].lower() if inv["project_name"] else ""

            if self._search_text:
                if (self._search_text not in inv_no and
                    self._search_text not in client and
                    self._search_text not in project):
                    continue

            # 2. Filter tabs
            status = inv["status"]
            is_overdue = inv["due_date"] and inv["due_date"] < today_str and status != "Paid" and status != "Cancelled"

            if self.current_filter == "Paid":
                if status != "Paid":
                    continue
            elif self.current_filter == "Unpaid":
                if status != "Unpaid":
                    continue
            elif self.current_filter == "Overdue":
                if not is_overdue:
                    continue
            elif self.current_filter == "Cancelled":
                if status != "Cancelled":
                    continue

            filtered.append(inv)

        self._populate_table(filtered)

    def _populate_table(self, invoices: list) -> None:
        self.table.clearSpans()
        today_str = datetime.date.today().isoformat()

        if not invoices:
            self.table.setRowCount(1)
            self.table.setRowHeight(0, 100)
            self.table.setSpan(0, 0, 1, 8)
            msg = "No invoices match this filter." if self.current_filter != "All" or self._search_text else \
                  "No invoices yet — click Create Invoice to add one"
            empty_item = QLabel(msg)
            empty_item.setAlignment(Qt.AlignCenter)
            empty_item.setStyleSheet("color: #6b6d85; font-size: 14px; background: transparent; border: none;")
            self.table.setCellWidget(0, 0, empty_item)
            return

        self.table.setRowCount(len(invoices))
        for i, inv in enumerate(invoices):
            # 0 - ID
            id_item = QTableWidgetItem(f"INV-{inv['id']:03d}")
            id_item.setForeground(QColor(Colors.TEXT_MUTED))
            id_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 0, id_item)

            # 1 - INVOICE NO
            no_item = QTableWidgetItem(inv["invoice_number"])
            no_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            font = no_item.font()
            font.setWeight(QFont.DemiBold)
            no_item.setFont(font)
            no_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 1, no_item)

            # 2 - CLIENT (avatar + name)
            client_name = inv["client_name"] or "No Client"
            client_widget = QWidget()
            client_widget.setStyleSheet("background: transparent; border: none;")
            client_layout = QHBoxLayout(client_widget)
            client_layout.setContentsMargins(6, 0, 6, 0)
            client_layout.setSpacing(8)

            initials = "".join([word[0] for word in client_name.split()[:2]]).upper()
            avatar_colors = ["rgba(125,211,227,0.30)", "rgba(124,138,244,0.30)", "rgba(232,124,138,0.30)", "#908f9e"]
            avatar_color = avatar_colors[hash(client_name) % len(avatar_colors)]

            avatar_label = QLabel()
            avatar_pixmap = _create_avatar_pixmap(initials, avatar_color, size=24)
            avatar_label.setPixmap(avatar_pixmap)
            avatar_label.setFixedSize(24, 24)
            client_layout.addWidget(avatar_label)

            client_label = QLabel(client_name)
            client_label.setStyleSheet("color: #e2e1f1; font-size: 14px; font-weight: 400; background: transparent; border: none;")
            client_layout.addWidget(client_label)
            client_layout.addStretch()
            self.table.setCellWidget(i, 2, client_widget)

            # 3 - PROJECT
            proj_item = QTableWidgetItem(inv["project_name"] or "—")
            proj_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            proj_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 3, proj_item)

            # 4 - TOTAL (right-aligned)
            total_item = QTableWidgetItem(f"₹{inv['total']:,.2f}")
            total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            total_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            total_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 4, total_item)

            # 5 - DUE DATE
            due = inv["due_date"] or "—"
            due_item = QTableWidgetItem(due)
            is_overdue = inv["due_date"] and inv["due_date"] < today_str and inv["status"] != "Paid" and inv["status"] != "Cancelled"
            if is_overdue:
                due_item.setForeground(QColor(Colors.ACCENT_DANGER))
                f = due_item.font()
                f.setBold(True)
                due_item.setFont(f)
            else:
                due_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            due_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(i, 5, due_item)

            # 6 - STATUS
            status = inv["status"]
            if status == "Unpaid" and inv["due_date"] and inv["due_date"] < today_str:
                status = "Overdue"
            
            status_colors = {
                "Paid": Colors.ACCENT_SUCCESS,
                "Unpaid": Colors.ACCENT_WARNING,
                "Overdue": Colors.ACCENT_DANGER,
                "Cancelled": Colors.TEXT_MUTED,
            }
            color = status_colors.get(status, Colors.TEXT_SECONDARY)
            self.table.setCellWidget(i, 6, StatusPill(status, color))

            # 7 - ACTIONS
            self.table.setCellWidget(i, 7, self._create_actions_cell(inv["id"]))

    def _create_actions_cell(self, invoice_id: int) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        edit_btn = QPushButton()
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.setToolTip("Edit Invoice")
        edit_btn.setIcon(QIcon(_load_svg_icon("edit", size=16, color="#6b6d85")))
        edit_btn.setIconSize(QSize(16, 16))
        edit_btn.setFixedSize(28, 28)
        edit_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.08);
            }
        """)
        edit_btn.clicked.connect(lambda: self._edit_invoice_by_id(invoice_id))

        del_btn = QPushButton()
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setToolTip("Delete Invoice")
        del_btn.setIcon(QIcon(_load_svg_icon("delete", size=16, color="#6b6d85")))
        del_btn.setIconSize(QSize(16, 16))
        del_btn.setFixedSize(28, 28)
        del_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background: rgba(232, 124, 138, 0.15);
            }
        """)
        del_btn.clicked.connect(lambda: self._delete_invoice_by_id(invoice_id))

        layout.addWidget(edit_btn)
        layout.addWidget(del_btn)
        return container

    def refresh(self) -> None:
        # Load invoices
        try:
            self._all_invoices_raw = self.repo.get_all()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not load invoices: {e}")
            self._all_invoices_raw = []

        # Refresh stats row
        try:
            # 1. TOTAL EARNED
            total_earned = self.repo.total_earned()
            self.card_earned.set_value(f"₹{total_earned:,.0f}")
            
            # Calculate direction vs last month
            this_month_earned = self.db.execute(
                """SELECT COALESCE(SUM(amount), 0) as total FROM invoices 
                   WHERE status='Paid' AND strftime('%m-%Y', date_issued) = strftime('%m-%Y', 'now')"""
            )[0]["total"]
            last_month_earned = self.db.execute(
                """SELECT COALESCE(SUM(amount), 0) as total FROM invoices 
                   WHERE status='Paid' AND strftime('%m-%Y', date_issued) = strftime('%m-%Y', date('now', '-1 month'))"""
            )[0]["total"]
            
            if this_month_earned > last_month_earned:
                sub, color = f"▲ +₹{this_month_earned - last_month_earned:,.0f} vs last month", Colors.ACCENT_SUCCESS
            elif this_month_earned == last_month_earned:
                sub, color = "→ Same as last month", Colors.TEXT_SECONDARY
            else:
                sub, color = f"▼ -₹{last_month_earned - this_month_earned:,.0f} vs last month", Colors.ACCENT_DANGER
            self.card_earned.set_sub_text(sub, color)

            # 2. PENDING
            pending_total = self.repo.total_pending()
            pending_count = len(self.repo.get_unpaid())
            self.card_pending.set_value(f"₹{pending_total:,.0f}")
            if pending_count > 0:
                self.card_pending.set_sub_text(f"{pending_count} awaiting payment", Colors.TEXT_MUTED)
            else:
                self.card_pending.set_sub_text("None", Colors.ACCENT_SUCCESS)

            # 3. OVERDUE
            overdue_invoices = self.repo.get_overdue()
            overdue_total = sum(float(r["total"]) for r in overdue_invoices) if overdue_invoices else 0.0
            overdue_count = len(overdue_invoices)
            self.card_overdue.set_value(f"₹{overdue_total:,.0f}")
            if overdue_count > 0:
                self.card_overdue.set_sub_text(f"{overdue_count} overdue", Colors.ACCENT_DANGER)
            else:
                self.card_overdue.set_sub_text("All caught up", Colors.ACCENT_SUCCESS)

            # 4. TOTAL INVOICES
            total_count = len(self._all_invoices_raw)
            self.card_total.set_value(str(total_count))
            
            this_month_count = self.db.execute(
                """SELECT COUNT(*) as cnt FROM invoices 
                   WHERE strftime('%m-%Y', date_issued) = strftime('%m-%Y', 'now')"""
            )[0]["cnt"]
            self.card_total.set_sub_text(f"{this_month_count} this month", Colors.TEXT_SECONDARY)
            
        except Exception as e:
            print(f"Error calculating invoice stats: {e}")

        # Refresh matplotlib chart
        self.revenue_chart.refresh()

        # Apply client-side filters to table
        self._apply_all_filters()

    def _create_invoice(self) -> None:
        clients = self.client_repo.get_all()
        if not clients:
            QMessageBox.warning(self, "No Clients", "Please add a client first.")
            return

        projects = self.project_repo.get_all()
        if not projects:
            QMessageBox.warning(self, "No Projects", "Please add a project first.")
            return

        default_due = self.settings.get_default_due_days()
        dialog = InvoiceDialog(self, default_due_days=default_due)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                # Add to database
                amount = data["amount"]
                tax = round(amount * GST_RATE, 2)
                total = round(amount + tax, 2)

                self.repo.add(
                    project_id=data["project_id"],
                    invoice_number=data["invoice_number"],
                    amount=amount,
                    tax=tax,
                    total=total,
                    due_date=data["due_date"],
                    status=data["status"],
                    notes=data["notes"],
                )
                emit_data_changed()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not create invoice: {e}")

    def _edit_invoice_by_id(self, invoice_id: int) -> None:
        rows = self.db.execute(
            """SELECT i.*, p.client_id
               FROM invoices i
               JOIN projects p ON i.project_id = p.id
               WHERE i.id = ?""",
            (invoice_id,),
        )
        if not rows:
            QMessageBox.warning(self, "Error", "Invoice not found.")
            return
        invoice = dict(rows[0])

        dialog = InvoiceDialog(self, invoice=invoice)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            try:
                amount = data["amount"]
                tax = round(amount * GST_RATE, 2)
                total = round(amount + tax, 2)

                self.repo.update(
                    invoice_id=invoice_id,
                    project_id=data["project_id"],
                    invoice_number=data["invoice_number"],
                    amount=amount,
                    tax=tax,
                    total=total,
                    due_date=data["due_date"],
                    status=data["status"],
                    notes=data["notes"],
                )
                emit_data_changed()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not update invoice: {e}")

    def _delete_invoice_by_id(self, invoice_id: int) -> None:
        inv = self.repo.get_by_id(invoice_id)
        if not inv:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete invoice '{inv['invoice_number']}'?\n\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                self.repo.delete(invoice_id)
                emit_data_changed()
                self.refresh()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not delete invoice: {e}")

    # ─── Relocated Edit Actions ───────────────────────────────────────
    
    def _export_invoice_pdf(self, invoice_id: int) -> None:
        inv = self.repo.get_by_id(invoice_id)
        if not inv:
            return

        try:
            rows = self.db.execute(
                """
                SELECT i.*, p.name as project_name, c.name as client_name, c.email as client_email
                FROM invoices i
                JOIN projects p ON i.project_id = p.id
                JOIN clients c ON p.client_id = c.id
                WHERE i.id = ?
                """,
                (invoice_id,),
            )
            if not rows:
                return

            data = rows[0]
            invoice_data = {
                "invoice_number": data["invoice_number"],
                "client_name": data["client_name"],
                "client_email": data["client_email"],
                "project_name": data["project_name"],
                "amount": data["amount"],
                "tax": data["tax"],
                "total": data["total"],
                "date_issued": data["date_issued"],
                "due_date": data["due_date"],
            }

            business = self.settings.export_business_as_dict()
            path = self.pdf_exporter.export_invoice(invoice_data, business=business)
            QMessageBox.information(self, "Exported", f"PDF saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Could not export PDF: {e}")

    def _email_invoice_by_id(self, invoice_id: int) -> None:
        rows = self.db.execute(
            """
            SELECT i.*, p.name as project_name, c.name as client_name, c.email as client_email
            FROM invoices i
            JOIN projects p ON i.project_id = p.id
            JOIN clients c ON p.client_id = c.id
            WHERE i.id = ?
            """,
            (invoice_id,),
        )
        if not rows:
            return
        data = rows[0]

        if not data["client_email"]:
            QMessageBox.warning(
                self,
                "Missing Email",
                f"{data['client_name']} has no email address on file.",
            )
            return

        try:
            invoice_data = {
                "invoice_number": data["invoice_number"],
                "client_name": data["client_name"],
                "client_email": data["client_email"],
                "project_name": data["project_name"],
                "amount": data["amount"],
                "tax": data["tax"],
                "total": data["total"],
                "date_issued": data["date_issued"],
                "due_date": data["due_date"],
            }
            business = self.settings.export_business_as_dict()
            pdf_path = self.pdf_exporter.export_invoice(invoice_data, business=business)
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Could not generate PDF: {e}")
            return

        biz_name = self.settings.get_business().name
        subject = self.email.invoice_subject(data["invoice_number"], biz_name)
        body = self.email.invoice_body(
            client_name=data["client_name"],
            invoice_number=data["invoice_number"],
            total=float(data["total"]),
            due_date=data["due_date"] or "—",
            business_name=biz_name,
        )

        confirm = QMessageBox.question(
            self,
            "Send Invoice",
            f"Send {data['invoice_number']} to {data['client_email']}?\n\nSubject: {subject}",
        )
        if confirm != QMessageBox.Yes:
            return

        try:
            self.email.send(data["client_email"], subject, body, attachment=pdf_path)
            QMessageBox.information(self, "Sent", f"Invoice emailed to {data['client_email']}.")
        except Exception as e:
            QMessageBox.critical(self, "Email Failed", f"Could not send email: {e}")

    def _send_single_overdue_reminder(self, invoice_id: int) -> None:
        rows = self.db.execute(
            """
            SELECT i.invoice_number, i.total, i.due_date, c.name as client_name,
                   c.email as client_email, i.status
            FROM invoices i
            JOIN projects p ON i.project_id = p.id
            JOIN clients c ON p.client_id = c.id
            WHERE i.id = ?
            """,
            (invoice_id,),
        )
        if not rows:
            return
        row = rows[0]

        if row["status"] != "Unpaid":
            QMessageBox.information(self, "No Reminder Needed", "This invoice is not unpaid.")
            return

        if not row["client_email"]:
            QMessageBox.warning(
                self,
                "Missing Email",
                f"{row['client_name']} has no email address on file.",
            )
            return

        confirm = QMessageBox.question(
            self,
            "Send Reminder",
            f"Send overdue reminder for {row['invoice_number']} to {row['client_email']}?",
        )
        if confirm != QMessageBox.Yes:
            return

        from datetime import date
        today = date.today()
        biz_name = self.settings.get_business().name
        try:
            due = date.fromisoformat(row["due_date"])
            days_overdue = max((today - due).days, 1)
        except Exception:
            days_overdue = 1

        subject = self.email.overdue_subject(row["invoice_number"])
        body = self.email.overdue_body(
            client_name=row["client_name"],
            invoice_number=row["invoice_number"],
            total=float(row["total"]),
            due_date=row["due_date"] or "—",
            days_overdue=days_overdue,
            business_name=biz_name,
        )

        try:
            self.email.send(row["client_email"], subject, body)
            QMessageBox.information(self, "Sent", f"Overdue reminder sent for {row['invoice_number']}.")
        except Exception as e:
            QMessageBox.critical(self, "Email Failed", f"Could not send reminder: {e}")


class InvoiceDialog(QDialog):
    """Create or edit invoice details — styled to match the Add Client dialog."""

    STATUSES = ["Unpaid", "Paid", "Overdue", "Cancelled"]

    def __init__(self, parent: InvoicesPage, default_due_days: int = 14, invoice: dict | None = None):
        super().__init__(parent)
        self.parent_page = parent
        self.invoice = invoice
        self.db = parent.db
        self.repo = parent.repo
        self.project_repo = parent.project_repo
        self.client_repo = parent.client_repo

        self.setWindowTitle("Edit Invoice" if invoice else "Create Invoice")
        self.setMinimumWidth(500)

        # Dialog Styling (Matching ClientDialog & ProjectDialog)
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
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QDoubleSpinBox {{
                background-color: {Colors.BG_ELEVATED};
                border: 1px solid {Colors.BORDER_DEFAULT};
                border-radius: 8px;
                padding: 8px 12px;
                color: {Colors.TEXT_PRIMARY};
                font-family: 'Inter';
                font-size: 14px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QDoubleSpinBox:focus {{
                border: 1px solid {Colors.ACCENT_PRIMARY_LIGHT};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(24)

        # Title
        title_text = "Edit Invoice Details" if invoice else "Create New Invoice"
        title = QLabel(title_text)
        title.setStyleSheet(f"""
            color: {Colors.TEXT_PRIMARY};
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.01em;
        """)
        layout.addWidget(title)

        # Form Layout
        form = QFormLayout()
        form.setSpacing(14)
        form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Invoice No
        self.number_input = QLineEdit()
        self.number_input.setReadOnly(True)
        self.number_input.setStyleSheet("QLineEdit { background-color: #12131a; color: #6b6d85; }")
        if invoice:
            self.number_input.setText(invoice["invoice_number"])
        else:
            self.number_input.setText(self.repo.next_invoice_number())
        form.addRow("Invoice No *", self.number_input)

        # Client dropdown
        self.client_combo = QComboBox()
        self.client_combo.setMinimumWidth(250)
        clients = self.client_repo.get_all()
        
        # Project dropdown
        self.project_combo = QComboBox()
        self.project_combo.setMinimumWidth(250)

        # Connect client selection change to project filter
        self.client_combo.currentIndexChanged.connect(self._on_client_changed)

        # Populate client and initial project dropdown
        self.client_combo.blockSignals(True)
        for c in clients:
            self.client_combo.addItem(c["name"], c["id"])
            
        if invoice:
            client_idx = self.client_combo.findData(invoice["client_id"])
            if client_idx >= 0:
                self.client_combo.setCurrentIndex(client_idx)
            
            # Populate project combo and set index
            projects = self.project_repo.get_by_client(invoice["client_id"])
            for p in projects:
                self.project_combo.addItem(p["name"], p["id"])
            proj_idx = self.project_combo.findData(invoice["project_id"])
            if proj_idx >= 0:
                self.project_combo.setCurrentIndex(proj_idx)
        else:
            self.client_combo.blockSignals(False)
            self._on_client_changed()
            self.client_combo.blockSignals(True)
            
        self.client_combo.blockSignals(False)

        form.addRow("Client *", self.client_combo)
        form.addRow("Project *", self.project_combo)

        # Amount
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(100, 10_000_000)
        self.amount_input.setPrefix("₹ ")
        self.amount_input.setDecimals(2)
        if invoice:
            self.amount_input.setValue(invoice["amount"])
        else:
            self.amount_input.setValue(5000)
        form.addRow("Amount (before GST) *", self.amount_input)

        # Due Date
        self.due_date_input = QDateEdit()
        self.due_date_input.setCalendarPopup(True)
        if invoice and invoice["due_date"]:
            self.due_date_input.setDate(QDate.fromString(invoice["due_date"], "yyyy-MM-dd"))
        else:
            future_date = datetime.date.today() + datetime.timedelta(days=default_due_days)
            self.due_date_input.setDate(QDate(future_date.year, future_date.month, future_date.day))
        form.addRow("Due Date *", self.due_date_input)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(self.STATUSES)
        if invoice:
            self.status_combo.setCurrentText(invoice["status"])
        else:
            self.status_combo.setCurrentText("Unpaid")
        form.addRow("Status", self.status_combo)

        # Notes
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("Optional notes or payment instructions...")
        if invoice and invoice["notes"]:
            self.notes_input.setPlainText(invoice["notes"])
        form.addRow("Notes", self.notes_input)

        layout.addLayout(form)

        # Required field reminder label
        helper = QLabel("* Required field")
        helper.setStyleSheet(f"color: {Colors.TEXT_MUTED}; font-size: 11px; font-style: italic;")
        layout.addWidget(helper)

        # ─── Relocated Action Buttons (Edit mode only) ─────────────────
        if invoice:
            sep = QFrame()
            sep.setFrameShape(QFrame.HLine)
            sep.setStyleSheet(f"background-color: {Colors.BORDER_SUBTLE}; max-height: 1px;")
            layout.addWidget(sep)

            action_row = QHBoxLayout()
            action_row.setSpacing(10)

            action_btn_style = f"""
                QPushButton {{
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: 600;
                    font-size: 12px;
                    border: none;
                    min-height: 32px;
                }}
            """

            # Export PDF
            export_btn = QPushButton("📄 Export PDF")
            export_btn.setCursor(Qt.PointingHandCursor)
            export_btn.setStyleSheet(action_btn_style + f"""
                QPushButton {{
                    background-color: {Colors.ACCENT_INFO};
                    color: {Colors.BG_DEEPEST};
                }}
                QPushButton:hover {{
                    background-color: {Colors.ACCENT_INFO_HOVER};
                }}
            """)
            export_btn.clicked.connect(lambda: self.parent_page._export_invoice_pdf(invoice["id"]))
            action_row.addWidget(export_btn)

            # Email
            email_btn = QPushButton("✉️ Email Invoice")
            email_btn.setCursor(Qt.PointingHandCursor)
            email_btn.setStyleSheet(action_btn_style + f"""
                QPushButton {{
                    background-color: {Colors.ACCENT_INFO};
                    color: {Colors.BG_DEEPEST};
                }}
                QPushButton:hover {{
                    background-color: {Colors.ACCENT_INFO_HOVER};
                }}
            """)
            email_btn.clicked.connect(lambda: self.parent_page._email_invoice_by_id(invoice["id"]))
            action_row.addWidget(email_btn)

            # Reminder
            remind_btn = QPushButton("🔔 Send Reminder")
            remind_btn.setCursor(Qt.PointingHandCursor)
            remind_btn.setStyleSheet(action_btn_style + f"""
                QPushButton {{
                    background-color: {Colors.ACCENT_WARNING};
                    color: {Colors.BG_DEEPEST};
                }}
                QPushButton:hover {{
                    background-color: {Colors.ACCENT_WARNING_HOVER};
                }}
            """)
            remind_btn.clicked.connect(lambda: self.parent_page._send_single_overdue_reminder(invoice["id"]))
            action_row.addWidget(remind_btn)

            # Mark Paid
            paid_btn = QPushButton("✓ Mark Paid")
            paid_btn.setCursor(Qt.PointingHandCursor)
            paid_btn.setStyleSheet(action_btn_style + f"""
                QPushButton {{
                    background-color: {Colors.ACCENT_SUCCESS};
                    color: {Colors.BG_DEEPEST};
                }}
                QPushButton:hover {{
                    background-color: {Colors.ACCENT_SUCCESS_HOVER};
                }}
            """)
            paid_btn.clicked.connect(self._mark_paid)
            action_row.addWidget(paid_btn)

            layout.addLayout(action_row)

        layout.addStretch()

        # Dialog Save / Cancel Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Save Invoice")
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

    def _on_client_changed(self) -> None:
        self.project_combo.clear()
        client_id = self.client_combo.currentData()
        if client_id is not None:
            projects = self.project_repo.get_by_client(client_id)
            for p in projects:
                self.project_combo.addItem(p["name"], p["id"])

    def _mark_paid(self) -> None:
        self.status_combo.setCurrentText("Paid")

    def get_data(self) -> dict:
        return {
            "invoice_number": self.number_input.text(),
            "project_id": self.project_combo.currentData(),
            "amount": self.amount_input.value(),
            "due_date": self.due_date_input.date().toString("yyyy-MM-dd"),
            "status": self.status_combo.currentText(),
            "notes": self.notes_input.toPlainText(),
        }
