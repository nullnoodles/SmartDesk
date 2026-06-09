"""
Dashboard — Modern, professional overview of freelance business.

Displays KPIs, revenue breakdown, project status, income trends, and recent projects.
Clean card-based layout with animated elements for smooth user experience.
"""
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
    """
    Main dashboard with KPI cards, revenue visualization, and recent activity.
    
    Layout Structure:
    ┌─────────────────────────────────────────────────────────────┐
    │ Page Header                          Welcome Back 👋        │
    │ ─────────────────────────────────────────────────────────── │
    │ [Total Earned] [Pending] [Active Projects] [Total Clients] │
    │ ─────────────────────────────────────────────────────────── │
    │ [Revenue Overview Card    ] [Project Status Card         ]  │
    │ ─────────────────────────────────────────────────────────── │
    │ [Income Trend Chart                ] [Project Types Chart]  │
    │ ─────────────────────────────────────────────────────────── │
    │ Recent Projects Table                                       │
    └─────────────────────────────────────────────────────────────┘
    """

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.invoice_repo = InvoiceRepository(db)
        self.project_repo = ProjectRepository(db)
        self.client_repo = ClientRepository(db)

        # Main layout with consistent spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 36, 36, 36)
        layout.setSpacing(28)

        # Build UI sections
        self._build_header(layout)
        self._build_stat_cards(layout)
        self._build_revenue_and_status(layout)
        self._build_charts(layout)
        self._build_recent_projects_table(layout)
        
        # Initialize animations and data
        self._setup_animations()
        QTimer.singleShot(50, self._initial_load)

    # ══════════════════════════════════════════════════════════════════
    # UI CONSTRUCTION METHODS
    # ══════════════════════════════════════════════════════════════════

    def _build_header(self, parent_layout: QVBoxLayout) -> None:
        """Build page header with title and greeting."""
        header_row = QHBoxLayout()
        header_row.setSpacing(20)

        # Page title and subtitle
        header = PageHeader(
            title="Dashboard",
            subtitle="Overview of your freelance business at a glance",
        )
        header_row.addWidget(header, 1)

        # Greeting message
        greeting = QLabel("Welcome back 👋")
        greeting.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        greeting.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 14px; font-weight: 600; letter-spacing: -0.01em;"
        )
        header_row.addWidget(greeting, 0)
        
        parent_layout.addLayout(header_row)

    def _build_stat_cards(self, parent_layout: QVBoxLayout) -> None:
        """Build the four KPI stat cards row."""
        cards_row = QHBoxLayout()
        cards_row.setSpacing(22)

        # Create stat cards with icons and accent colors
        self.card_earned = StatCard(
            "Total Earned", 
            "₹0", 
            icon="💰", 
            accent=Colors.ACCENT_SUCCESS
        )
        self.card_pending = StatCard(
            "Pending Amount", 
            "₹0", 
            icon="⏳", 
            accent=Colors.ACCENT_WARNING
        )
        self.card_projects = StatCard(
            "Active Projects", 
            "0", 
            icon="🚀", 
            accent=Colors.ACCENT_INFO
        )
        self.card_clients = StatCard(
            "Total Clients", 
            "0", 
            icon="👥", 
            accent=Colors.ACCENT_PRIMARY_LIGHT
        )

        # Add all cards to row with equal stretch
        for card in (self.card_earned, self.card_pending, self.card_projects, self.card_clients):
            cards_row.addWidget(card, 1)
        
        parent_layout.addLayout(cards_row)

    def _build_revenue_and_status(self, parent_layout: QVBoxLayout) -> None:
        """Build revenue overview card and project status card side-by-side."""
        mid_row = QHBoxLayout()
        mid_row.setSpacing(22)

        # Revenue overview card (left, 2/3 width)
        self._build_revenue_card(mid_row)
        
        # Project status card (right, 1/3 width)
        self._build_status_card(mid_row)

        parent_layout.addLayout(mid_row)

    def _build_revenue_card(self, parent_layout: QHBoxLayout) -> None:
        """Build the revenue overview card with gradient bars."""
        self.revenue_card = AnimatedCard()
        self.revenue_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.revenue_card.setMinimumHeight(280)
        
        rev_layout = QVBoxLayout(self.revenue_card)
        rev_layout.setContentsMargins(26, 24, 26, 24)
        rev_layout.setSpacing(22)

        # Card title
        rev_title = QLabel("Revenue Overview")
        rev_title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 17px; font-weight: 700; letter-spacing: -0.01em;"
        )
        rev_layout.addWidget(rev_title)
        
        rev_layout.addSpacing(4)

        # Three revenue bars
        self.bar_earned = self._build_bar_row(
            "Collected Revenue", 
            Colors.ACCENT_SUCCESS, 
            Colors.ACCENT_PRIMARY_LIGHT
        )
        rev_layout.addLayout(self.bar_earned["layout"])

        self.bar_pending = self._build_bar_row(
            "Pending Invoices", 
            Colors.ACCENT_WARNING, 
            Colors.ACCENT_WARNING_HOVER
        )
        rev_layout.addLayout(self.bar_pending["layout"])

        self.bar_overdue = self._build_bar_row(
            "Overdue Amount", 
            Colors.ACCENT_DANGER, 
            Colors.ACCENT_DANGER_HOVER
        )
        rev_layout.addLayout(self.bar_overdue["layout"])

        rev_layout.addStretch()
        parent_layout.addWidget(self.revenue_card, 2)

    def _build_status_card(self, parent_layout: QHBoxLayout) -> None:
        """Build the project status breakdown card."""
        self.status_card = AnimatedCard()
        self.status_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.status_card.setMinimumHeight(280)
        
        status_layout = QVBoxLayout(self.status_card)
        status_layout.setContentsMargins(26, 24, 26, 24)
        status_layout.setSpacing(10)

        # Card title
        status_title = QLabel("Project Status")
        status_title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 17px; font-weight: 700; letter-spacing: -0.01em;"
        )
        status_layout.addWidget(status_title)
        status_layout.addSpacing(8)

        # Status rows with colored dots
        self.status_labels: dict[str, QLabel] = {}
        self.status_definitions = [
            ("In Progress", Colors.ACCENT_INFO),
            ("Completed", Colors.ACCENT_SUCCESS),
            ("On Hold", Colors.ACCENT_WARNING),
            ("Not Started", Colors.TEXT_MUTED),
        ]
        
        for status_name, color in self.status_definitions:
            row = QHBoxLayout()
            row.setSpacing(12)
            row.setContentsMargins(0, 8, 0, 8)

            # Status indicator dot
            dot = QLabel("●")
            dot.setFixedWidth(16)
            dot.setStyleSheet(
                f"color: {color}; background: transparent; "
                f"font-size: 12px;"
            )
            row.addWidget(dot)

            # Status name
            name_lbl = QLabel(status_name)
            name_lbl.setStyleSheet(
                f"color: {Colors.TEXT_SECONDARY}; background: transparent; "
                f"font-size: 14px; font-weight: 500;"
            )
            row.addWidget(name_lbl)
            row.addStretch()

            # Count value
            count_lbl = QLabel("0")
            count_lbl.setStyleSheet(
                f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
                f"font-size: 16px; font-weight: 700;"
            )
            row.addWidget(count_lbl)

            self.status_labels[status_name] = count_lbl
            status_layout.addLayout(row)

        status_layout.addStretch()
        parent_layout.addWidget(self.status_card, 1)

    def _build_charts(self, parent_layout: QVBoxLayout) -> None:
        """Build income trend and project type charts side-by-side."""
        charts_row = QHBoxLayout()
        charts_row.setSpacing(22)

        # Income trend chart (left, wider)
        income_card = AnimatedCard()
        income_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        income_card.setMinimumHeight(320)
        income_layout = QVBoxLayout(income_card)
        income_layout.setContentsMargins(22, 20, 22, 20)
        
        self.income_chart = IncomeTrendChart(self.db)
        income_layout.addWidget(self.income_chart)
        charts_row.addWidget(income_card, 3)

        # Project type chart (right, narrower)
        type_card = AnimatedCard()
        type_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        type_card.setMinimumHeight(320)
        type_layout = QVBoxLayout(type_card)
        type_layout.setContentsMargins(22, 20, 22, 20)
        
        self.type_chart = ProjectTypeChart(self.db)
        type_layout.addWidget(self.type_chart)
        charts_row.addWidget(type_card, 2)

        parent_layout.addLayout(charts_row)

    def _build_recent_projects_table(self, parent_layout: QVBoxLayout) -> None:
        """Build the recent projects table section."""
        # Section header
        table_header = QLabel("Recent Projects")
        table_header.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 17px; font-weight: 700; letter-spacing: -0.01em;"
        )
        parent_layout.addWidget(table_header)

        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Project", 
            "Client", 
            "Status", 
            "Deadline", 
            "Budget"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setMinimumHeight(300)
        
        # Adjust column widths for better proportions
        header = self.table.horizontalHeader()
        header.setDefaultSectionSize(150)
        
        parent_layout.addWidget(self.table)

    def _build_bar_row(self, label: str, color_start: str, color_end: str) -> dict:
        """
        Build a labeled gradient bar for revenue visualization.
        
        Returns:
            Dictionary with layout, bar widget, and value label references.
        """
        row_layout = QVBoxLayout()
        row_layout.setSpacing(8)

        # Label and value header
        header = QHBoxLayout()
        header.setSpacing(0)
        
        lbl = QLabel(label)
        lbl.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; background: transparent; "
            f"font-size: 13px; font-weight: 500;"
        )
        header.addWidget(lbl)
        header.addStretch()

        value_lbl = QLabel("₹0")
        value_lbl.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 14px; font-weight: 700;"
        )
        header.addWidget(value_lbl)
        row_layout.addLayout(header)

        # Gradient bar
        bar = GradientBar(
            value=0, 
            max_value=100, 
            color_start=color_start, 
            color_end=color_end, 
            height=10
        )
        row_layout.addWidget(bar)

        return {
            "layout": row_layout, 
            "bar": bar, 
            "value_label": value_lbl
        }

    def _setup_animations(self) -> None:
        """Initialize staggered fade-in animation for stat cards."""
        self._stagger = StaggeredFadeIn(
            [
                self.card_earned, 
                self.card_pending, 
                self.card_projects, 
                self.card_clients
            ],
            delay_ms=100,
            duration_ms=400,
        )

    # ══════════════════════════════════════════════════════════════════
    # DATA LOADING AND REFRESH
    # ══════════════════════════════════════════════════════════════════

    def _initial_load(self) -> None:
        """Trigger initial animation and data load."""
        self._stagger.start()
        self.refresh()

    def refresh(self) -> None:
        """
        Refresh all dashboard data from database.
        Safely handles errors to prevent dashboard from breaking.
        """
        try:
            # Fetch financial data
            earned = self.invoice_repo.total_earned()
            pending = self.invoice_repo.total_pending()
            overdue_rows = self.invoice_repo.get_overdue()
            overdue = sum(float(row["total"]) for row in overdue_rows) if overdue_rows else 0.0
            
            # Fetch project and client data
            status_counts = self.project_repo.count_all_statuses()
            active = status_counts.get("In Progress", 0)
            clients = self.client_repo.count()

            # Update KPI cards
            self.card_earned.set_value(f"₹{earned:,.0f}")
            self.card_pending.set_value(f"₹{pending:,.0f}")
            self.card_projects.set_value(str(active))
            self.card_clients.set_value(str(clients))

            # Update revenue bars
            total = max(earned + pending + overdue, 1)
            self._update_bar(self.bar_earned, earned, total)
            self._update_bar(self.bar_pending, pending, total)
            self._update_bar(self.bar_overdue, overdue, total)

            # Update project status counts
            for status_name, _ in self.status_definitions:
                count = status_counts.get(status_name, 0)
                self.status_labels[status_name].setText(str(count))

            # Refresh charts (gracefully handle errors)
            try:
                self.income_chart.refresh()
                self.type_chart.refresh()
            except Exception:
                pass

            # Refresh recent projects table
            self._populate_recent_projects()
            
        except Exception:
            # Silently fail to prevent dashboard crash
            pass

    def _update_bar(self, bar_dict: dict, value: float, total: float) -> None:
        """
        Update a revenue bar with new value and animate the change.
        
        Args:
            bar_dict: Dictionary containing bar widget and value label
            value: Current value to display
            total: Total value for percentage calculation
        """
        bar_dict["bar"]._max_value = total
        bar_dict["bar"].set_value(value, animate=True)
        bar_dict["value_label"].setText(f"₹{value:,.0f}")

    def _populate_recent_projects(self) -> None:
        """
        Populate the recent projects table with the 8 most recent projects.
        Shows empty state message if no projects exist.
        """
        try:
            projects = self.project_repo.get_all()
        except Exception:
            projects = []

        # Empty state handling
        if not projects:
            self.table.setRowCount(1)
            empty_item = QTableWidgetItem(
                "No projects yet — create one from the Projects page"
            )
            empty_item.setFlags(Qt.ItemIsEnabled)
            empty_item.setForeground(QColor(Colors.TEXT_MUTED))
            self.table.setItem(0, 0, empty_item)
            self.table.setSpan(0, 0, 1, 5)
            return

        # Clear any previous spans
        self.table.clearSpans()
        
        # Show up to 8 most recent projects
        rows = projects[:8]
        self.table.setRowCount(len(rows))
        
        # Status color mapping
        status_colors = {
            "In Progress": Colors.ACCENT_INFO,
            "Completed": Colors.ACCENT_SUCCESS,
            "On Hold": Colors.ACCENT_WARNING,
            "Not Started": Colors.TEXT_MUTED,
            "Cancelled": Colors.ACCENT_DANGER,
        }

        # Populate table rows
        for i, proj in enumerate(rows):
            # Project name
            name_item = QTableWidgetItem(proj["name"])
            self.table.setItem(i, 0, name_item)
            
            # Client name
            client_item = QTableWidgetItem(proj["client_name"])
            self.table.setItem(i, 1, client_item)

            # Status pill (custom widget)
            color = status_colors.get(proj["status"], Colors.TEXT_SECONDARY)
            pill = StatusPill(proj["status"], color)
            self.table.setCellWidget(i, 2, pill)

            # Deadline
            deadline_item = QTableWidgetItem(proj["deadline"] or "—")
            self.table.setItem(i, 3, deadline_item)
            
            # Budget
            budget_text = f"₹{proj['budget']:,.0f}" if proj["budget"] else "—"
            budget_item = QTableWidgetItem(budget_text)
            self.table.setItem(i, 4, budget_item)
