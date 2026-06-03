
from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.data.database import Database
from app.data.repositories.client_repo import ClientRepository
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.project_repo import ProjectRepository
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedCard, GradientBar, StaggeredFadeIn
from app.ui.widgets.charts import IncomeTrendChart, ProjectTypeChart
from app.ui.widgets.page_header import PageHeader
from app.ui.widgets.stat_card import StatCard
from app.ui.widgets.status_pill import StatusPill


class DashboardPage(QWidget):
    """Main dashboard with KPI cards, revenue bars, status breakdown, and recent table."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.invoice_repo = InvoiceRepository(db)
        self.project_repo = ProjectRepository(db)
        self.client_repo = ClientRepository(db)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)  # Fix: Increased margins (min 12px)
        layout.setSpacing(28)  # Fix: Increased spacing

        # ─── Header ───────────────────────────────────────────────────────
        header_row = QHBoxLayout()
        header_row.setSpacing(20)  # Fix: Increased spacing

        header = PageHeader(
            title="Dashboard",
            subtitle="Overview of your freelance business at a glance",
        )
        header.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)  # Fix: Allow expansion
        header_row.addWidget(header, 1)

        greeting = QLabel("Welcome back 👋")
        greeting.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        greeting.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 14px; font-weight: 600; padding: 4px 8px;"  # Fix: Increased size and padding
        )
        greeting.setMinimumHeight(24)  # Fix: Minimum height
        header_row.addWidget(greeting, 0)
        layout.addLayout(header_row)

        # ─── Stat cards row ───────────────────────────────────────────────
        cards_row = QHBoxLayout()
        cards_row.setSpacing(24)  # Fix: Increased spacing between cards

        self.card_earned = StatCard("Total Earned", "₹0", icon="💰", accent=Colors.ACCENT_SUCCESS)
        self.card_pending = StatCard("Pending Amount", "₹0", icon="⏳", accent=Colors.ACCENT_WARNING)
        self.card_projects = StatCard("Active Projects", "0", icon="🚀", accent=Colors.ACCENT_INFO)
        self.card_clients = StatCard("Total Clients", "0", icon="👥", accent=Colors.ACCENT_PRIMARY_LIGHT)

        # Fix: Ensure all cards expand equally with proper stretch factor
        for card in (self.card_earned, self.card_pending, self.card_projects, self.card_clients):
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Fix: Allow vertical expansion
            cards_row.addWidget(card, 1)
        layout.addLayout(cards_row)

        # ─── Middle row: revenue + status ────────────────────────────────
        mid_row = QHBoxLayout()
        mid_row.setSpacing(24)  # Fix: Increased spacing

        # Revenue overview
        self.revenue_card = AnimatedCard()
        self.revenue_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Fix: Allow full expansion
        self.revenue_card.setMinimumHeight(320)  # Fix: Ensure minimum height
        rev_layout = QVBoxLayout(self.revenue_card)
        rev_layout.setContentsMargins(26, 24, 26, 24)  # Fix: Increased padding (min 12px)
        rev_layout.setSpacing(22)  # Fix: Increased spacing

        rev_title = QLabel("Revenue Overview")
        rev_title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 17px; font-weight: 700; padding: 4px 0px;"  # Fix: Increased size and padding
        )
        rev_title.setMinimumHeight(24)  # Fix: Minimum height
        rev_layout.addWidget(rev_title)

        self.bar_earned = self._build_bar_row("Collected Revenue", Colors.ACCENT_SUCCESS, Colors.ACCENT_PRIMARY_LIGHT)
        rev_layout.addLayout(self.bar_earned["layout"])

        self.bar_pending = self._build_bar_row("Pending Invoices", Colors.ACCENT_WARNING, Colors.ACCENT_WARNING_HOVER)
        rev_layout.addLayout(self.bar_pending["layout"])

        self.bar_overdue = self._build_bar_row("Overdue Amount", Colors.ACCENT_DANGER, Colors.ACCENT_DANGER_HOVER)
        rev_layout.addLayout(self.bar_overdue["layout"])

        rev_layout.addStretch()
        mid_row.addWidget(self.revenue_card, 2)

        # Project status
        self.status_card = AnimatedCard()
        self.status_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Fix: Allow full expansion
        self.status_card.setMinimumHeight(320)  # Fix: Match revenue card height
        status_layout = QVBoxLayout(self.status_card)
        status_layout.setContentsMargins(26, 24, 26, 24)  # Fix: Increased padding (min 12px)
        status_layout.setSpacing(12)  # Fix: Increased spacing

        status_title = QLabel("Project Status")
        status_title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 17px; font-weight: 700; padding: 4px 0px;"  # Fix: Increased size and padding
        )
        status_title.setMinimumHeight(24)  # Fix: Minimum height
        status_layout.addWidget(status_title)
        status_layout.addSpacing(10)  # Fix: Increased spacing

        self.status_labels: dict[str, QLabel] = {}
        self.status_definitions = [
            ("In Progress", Colors.ACCENT_INFO),
            ("Completed", Colors.ACCENT_SUCCESS),
            ("On Hold", Colors.ACCENT_WARNING),
            ("Not Started", Colors.TEXT_MUTED),
        ]
        for status_name, color in self.status_definitions:
            row = QHBoxLayout()
            row.setSpacing(14)  # Fix: Increased spacing
            row.setContentsMargins(0, 8, 0, 8)  # Fix: Increased vertical margins

            dot = QLabel("●")
            dot.setFixedWidth(18)  # Fix: Fixed width for alignment
            dot.setStyleSheet(
                f"color: {color}; background: transparent; "
                f"font-size: 12px; padding: 2px;"  # Fix: Increased size and padding
            )
            dot.setMinimumHeight(20)  # Fix: Minimum height
            row.addWidget(dot)

            name_lbl = QLabel(status_name)
            name_lbl.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; background: transparent; "
                f"font-size: 14px; font-weight: 500; padding: 2px 4px;"  # Fix: Increased size and padding
            )
            name_lbl.setMinimumHeight(20)  # Fix: Minimum height
            row.addWidget(name_lbl)
            row.addStretch()

            count_lbl = QLabel("0")
            count_lbl.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
                f"font-size: 16px; font-weight: 700; padding: 2px 4px;"  # Fix: Increased size and padding
            )
            count_lbl.setMinimumHeight(20)  # Fix: Minimum height
            row.addWidget(count_lbl)

            self.status_labels[status_name] = count_lbl
            status_layout.addLayout(row)

        status_layout.addStretch()
        mid_row.addWidget(self.status_card, 1)

        layout.addLayout(mid_row)

        # ─── Charts row ──────────────────────────────────────────────────
        # Fix: Larger charts with proper titles and context
        charts_section_title = QLabel("Performance Analytics")
        charts_section_title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 18px; font-weight: 700; padding: 8px 0px;"
        )
        charts_section_title.setMinimumHeight(28)
        layout.addWidget(charts_section_title)
        
        charts_row = QHBoxLayout()
        charts_row.setSpacing(24)  # Fix: Increased spacing

        # Income Trend Chart Card
        income_card = AnimatedCard()
        income_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        income_card.setMinimumHeight(450)  # Fix: Much larger height (was 340)
        income_layout = QVBoxLayout(income_card)
        income_layout.setContentsMargins(28, 26, 28, 26)  # Fix: Increased padding
        income_layout.setSpacing(12)
        
        # Chart title and description
        income_title = QLabel("💰 Income Trend")
        income_title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 16px; font-weight: 700; padding: 4px 0px;"
        )
        income_title.setMinimumHeight(24)
        income_layout.addWidget(income_title)
        
        income_desc = QLabel("Monthly revenue from paid invoices over the last 6 months")
        income_desc.setWordWrap(True)
        income_desc.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; "
            f"font-size: 12px; padding: 0px 0px 8px 0px;"
        )
        income_desc.setMinimumHeight(18)
        income_layout.addWidget(income_desc)
        
        # Chart widget - now much larger
        self.income_chart = IncomeTrendChart(self.db)
        self.income_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.income_chart.setMinimumHeight(320)  # Fix: Larger chart (was none)
        income_layout.addWidget(self.income_chart, 1)  # Fix: Stretch factor
        charts_row.addWidget(income_card, 3)

        # Project Type Chart Card
        type_card = AnimatedCard()
        type_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        type_card.setMinimumHeight(450)  # Fix: Much larger height (was 340)
        type_layout = QVBoxLayout(type_card)
        type_layout.setContentsMargins(28, 26, 28, 26)  # Fix: Increased padding
        type_layout.setSpacing(12)
        
        # Chart title and description
        type_title = QLabel("📊 Revenue by Type")
        type_title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 16px; font-weight: 700; padding: 4px 0px;"
        )
        type_title.setMinimumHeight(24)
        type_layout.addWidget(type_title)
        
        type_desc = QLabel("Total revenue breakdown by project category")
        type_desc.setWordWrap(True)
        type_desc.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; "
            f"font-size: 12px; padding: 0px 0px 8px 0px;"
        )
        type_desc.setMinimumHeight(18)
        type_layout.addWidget(type_desc)
        
        # Chart widget - now much larger
        self.type_chart = ProjectTypeChart(self.db)
        self.type_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.type_chart.setMinimumHeight(320)  # Fix: Larger chart (was none)
        type_layout.addWidget(self.type_chart, 1)  # Fix: Stretch factor
        charts_row.addWidget(type_card, 2)

        layout.addLayout(charts_row)

        # ─── Recent projects table ────────────────────────────────────────
        table_header = QLabel("Recent Projects")
        table_header.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 17px; font-weight: 700; padding: 4px 0px;"  # Fix: Increased size and padding
        )
        table_header.setMinimumHeight(24)  # Fix: Minimum height
        layout.addWidget(table_header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Project", "Client", "Status", "Deadline", "Budget"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(300)  # Fix: Set minimum height for table
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Fix: Allow expansion
        layout.addWidget(self.table)

        # Staggered entrance for stat cards
        self._stagger = StaggeredFadeIn(
            [self.card_earned, self.card_pending, self.card_projects, self.card_clients],
            delay_ms=100,
            duration_ms=400,
        )
        QTimer.singleShot(50, self._initial_load)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _build_bar_row(self, label: str, color_start: str, color_end: str) -> dict:
        row_layout = QVBoxLayout()
        row_layout.setSpacing(6)

        header = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; background: transparent; "
            f"font-size: 12px; font-weight: 500;"
        )
        header.addWidget(lbl)
        header.addStretch()

        value_lbl = QLabel("₹0")
        value_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 13px; font-weight: 700;"
        )
        header.addWidget(value_lbl)
        row_layout.addLayout(header)

        bar = GradientBar(value=0, max_value=100, color_start=color_start, color_end=color_end, height=8)
        row_layout.addWidget(bar)

        return {"layout": row_layout, "bar": bar, "value_label": value_lbl}

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    def _initial_load(self) -> None:
        self._stagger.start()
        self.refresh()

    def refresh(self) -> None:
        try:
            earned = self.invoice_repo.total_earned()
            pending = self.invoice_repo.total_pending()
            overdue_rows = self.invoice_repo.get_overdue()
            overdue = sum(float(row["total"]) for row in overdue_rows) if overdue_rows else 0.0
            status_counts = self.project_repo.count_all_statuses()
            active = status_counts.get("In Progress", 0)
            clients = self.client_repo.count()

            self.card_earned.set_value(f"₹{earned:,.0f}")
            self.card_pending.set_value(f"₹{pending:,.0f}")
            self.card_projects.set_value(str(active))
            self.card_clients.set_value(str(clients))

            total = max(earned + pending + overdue, 1)
            self._update_bar(self.bar_earned, earned, total)
            self._update_bar(self.bar_pending, pending, total)
            self._update_bar(self.bar_overdue, overdue, total)

            for status_name, _ in self.status_definitions:
                self.status_labels[status_name].setText(str(status_counts.get(status_name, 0)))

            # Refresh charts
            try:
                self.income_chart.refresh()
                self.type_chart.refresh()
            except Exception:
                pass

            self._populate_recent_projects()
        except Exception:
            pass

    def _update_bar(self, bar_dict: dict, value: float, total: float) -> None:
        bar_dict["bar"]._max_value = total
        bar_dict["bar"].set_value(value, animate=True)
        bar_dict["value_label"].setText(f"₹{value:,.0f}")

    def _populate_recent_projects(self) -> None:
        try:
            projects = self.project_repo.get_all()
        except Exception:
            projects = []

        if not projects:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem("No projects yet — create one from the Projects page")
            empty_item.setFlags(Qt.ItemIsEnabled)
            empty_item.setForeground(QColor(Colors.TEXT_MUTED))
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 5)
            return

        self.table.clearSpans()
        rows = projects[:8]
        self.table.setRowCount(len(rows))
        status_colors = {
            "In Progress": Colors.ACCENT_INFO,
            "Completed": Colors.ACCENT_SUCCESS,
            "On Hold": Colors.ACCENT_WARNING,
            "Not Started": Colors.TEXT_MUTED,
            "Cancelled": Colors.ACCENT_DANGER,
        }

        for i, proj in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(proj["name"]))
            self.table.setItem(i, 1, QTableWidgetItem(proj["client_name"]))

            color = status_colors.get(proj["status"], Colors.TEXT_SECONDARY)
            pill = StatusPill(proj["status"], color)
            self.table.setCellWidget(i, 2, pill)

            self.table.setItem(i, 3, QTableWidgetItem(proj["deadline"] or "—"))
            self.table.setItem(
                i,
                4,
                QTableWidgetItem(f"₹{proj['budget']:,.0f}" if proj["budget"] else "—"),
            )
