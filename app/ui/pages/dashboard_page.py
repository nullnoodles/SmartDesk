"""Dashboard page — animated summary cards, gradient bars, chart, recent activity."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QFrame, QGridLayout, QSizePolicy,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPainterPath, QLinearGradient, QFont

from app.data.database import Database
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.project_repo import ProjectRepository
from app.data.repositories.client_repo import ClientRepository
from app.ui.styles.theme import Colors
from app.ui.widgets.animated import AnimatedCard, GradientBar, StaggeredFadeIn


class DashboardPage(QWidget):
    """Main dashboard with animated summary cards, mini chart, and recent activity."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.invoice_repo = InvoiceRepository(db)
        self.project_repo = ProjectRepository(db)
        self.client_repo = ClientRepository(db)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(24)

        # Header
        header_row = QHBoxLayout()
        header = QLabel("Dashboard")
        header.setObjectName("heading")
        header_row.addWidget(header)
        header_row.addStretch()

        greeting = QLabel("Welcome back 👋")
        greeting.setObjectName("subheading")
        header_row.addWidget(greeting)
        layout.addLayout(header_row)

        # ─── Summary Cards Row ────────────────────────────────────────────
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(16)

        self.card_earned = self._create_metric_card(
            "Total Earned", "₹0", Colors.ACCENT_SUCCESS, "💰"
        )
        self.card_pending = self._create_metric_card(
            "Pending", "₹0", Colors.ACCENT_WARNING, "⏳"
        )
        self.card_projects = self._create_metric_card(
            "Active Projects", "0", Colors.ACCENT_INFO, "📁"
        )
        self.card_clients = self._create_metric_card(
            "Total Clients", "0", Colors.ACCENT_PRIMARY, "👥"
        )

        cards_layout.addWidget(self.card_earned)
        cards_layout.addWidget(self.card_pending)
        cards_layout.addWidget(self.card_projects)
        cards_layout.addWidget(self.card_clients)
        layout.addLayout(cards_layout)

        # ─── Middle Row: Mini Chart + Quick Stats ─────────────────────────
        middle_row = QHBoxLayout()
        middle_row.setSpacing(16)

        # Revenue breakdown (gradient bars)
        self.revenue_card = self._create_revenue_card()
        middle_row.addWidget(self.revenue_card, stretch=3)

        # Project status breakdown
        self.status_card = self._create_status_card()
        middle_row.addWidget(self.status_card, stretch=2)

        layout.addLayout(middle_row)

        # ─── Recent Projects Table ────────────────────────────────────────
        table_header = QLabel("Recent Projects")
        table_header.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {Colors.TEXT_PRIMARY};")
        layout.addWidget(table_header)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Project", "Client", "Status", "Deadline", "Budget"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        layout.addWidget(self.table)

        # Staggered entrance animation
        self._cards = [self.card_earned, self.card_pending, self.card_projects, self.card_clients]
        self._stagger = StaggeredFadeIn(self._cards, delay_ms=100, duration_ms=400)

        # Load data after a brief delay for smooth entrance
        QTimer.singleShot(50, self._initial_load)

    def _create_metric_card(self, title: str, value: str, accent: str, icon: str) -> AnimatedCard:
        """Create an animated metric card with icon, title, and value."""
        card = AnimatedCard()
        card.setMinimumHeight(120)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 18, 20, 18)
        card_layout.setSpacing(8)

        # Icon + title row
        top_row = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px; background: transparent;")
        top_row.addWidget(icon_label)
        top_row.addStretch()

        # Small accent dot
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {accent}; font-size: 10px; background: transparent;")
        top_row.addWidget(dot)
        card_layout.addLayout(top_row)

        # Title
        lbl_title = QLabel(title)
        lbl_title.setObjectName("card_title")
        lbl_title.setStyleSheet(f"color: {Colors.TEXT_SECONDARY}; font-size: 11px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; background: transparent;")
        card_layout.addWidget(lbl_title)

        # Value
        lbl_value = QLabel(value)
        lbl_value.setObjectName("card_value")
        lbl_value.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {accent}; background: transparent;")
        card_layout.addWidget(lbl_value)

        return card

    def _create_revenue_card(self) -> AnimatedCard:
        """Card with gradient progress bars showing revenue breakdown."""
        card = AnimatedCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(14)

        title = QLabel("Revenue Overview")
        title.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)

        # Earned bar
        self.bar_earned = self._create_bar_row("Earned", Colors.ACCENT_SUCCESS, Colors.ACCENT_INFO)
        layout.addLayout(self.bar_earned["layout"])

        # Pending bar
        self.bar_pending = self._create_bar_row("Pending", Colors.ACCENT_WARNING, Colors.ACCENT_DANGER)
        layout.addLayout(self.bar_pending["layout"])

        # Overdue bar
        self.bar_overdue = self._create_bar_row("Overdue", Colors.ACCENT_DANGER, Colors.ACCENT_WARNING)
        layout.addLayout(self.bar_overdue["layout"])

        layout.addStretch()
        return card

    def _create_bar_row(self, label: str, color_start: str, color_end: str) -> dict:
        """Create a labeled gradient bar row."""
        row_layout = QVBoxLayout()
        row_layout.setSpacing(4)

        # Label + value
        header = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
        header.addWidget(lbl)
        header.addStretch()
        value_lbl = QLabel("₹0")
        value_lbl.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        header.addWidget(value_lbl)
        row_layout.addLayout(header)

        # Gradient bar
        bar = GradientBar(value=0, max_value=100, color_start=color_start, color_end=color_end, height=8)
        row_layout.addWidget(bar)

        return {"layout": row_layout, "bar": bar, "value_label": value_lbl}

    def _create_status_card(self) -> AnimatedCard:
        """Card showing project status breakdown with colored indicators."""
        card = AnimatedCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title = QLabel("Project Status")
        title.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;")
        layout.addWidget(title)

        self.status_labels: dict[str, QLabel] = {}
        statuses = [
            ("In Progress", Colors.ACCENT_INFO, "●"),
            ("Completed", Colors.ACCENT_SUCCESS, "●"),
            ("On Hold", Colors.ACCENT_WARNING, "●"),
            ("Not Started", Colors.TEXT_MUTED, "●"),
        ]

        for status_name, color, dot in statuses:
            row = QHBoxLayout()
            indicator = QLabel(dot)
            indicator.setStyleSheet(f"color: {color}; font-size: 14px; background: transparent;")
            row.addWidget(indicator)

            name_lbl = QLabel(status_name)
            name_lbl.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; background: transparent;")
            row.addWidget(name_lbl)
            row.addStretch()

            count_lbl = QLabel("0")
            count_lbl.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {Colors.TEXT_PRIMARY}; background: transparent;")
            row.addWidget(count_lbl)
            self.status_labels[status_name] = count_lbl
            layout.addLayout(row)

        layout.addStretch()
        return card

    def _initial_load(self) -> None:
        """Load data and trigger entrance animations."""
        self._stagger.start()
        self.refresh()

    def refresh(self) -> None:
        """Reload dashboard data with animated transitions."""
        try:
            # Update metric cards
            earned = self.invoice_repo.total_earned()
            pending = self.invoice_repo.total_pending()
            status_counts = self.project_repo.count_all_statuses()
            active = status_counts.get("In Progress", 0)
            clients = self.client_repo.count()

            self.card_earned.findChild(QLabel, "card_value").setText(f"₹{earned:,.0f}")
            self.card_pending.findChild(QLabel, "card_value").setText(f"₹{pending:,.0f}")
            self.card_projects.findChild(QLabel, "card_value").setText(str(active))
            self.card_clients.findChild(QLabel, "card_value").setText(str(clients))

            # Update revenue bars
            total = max(earned + pending, 1)
            self.bar_earned["bar"].set_value(earned, animate=True)
            self.bar_earned["bar"]._max_value = total
            self.bar_earned["value_label"].setText(f"₹{earned:,.0f}")

            self.bar_pending["bar"].set_value(pending, animate=True)
            self.bar_pending["bar"]._max_value = total
            self.bar_pending["value_label"].setText(f"₹{pending:,.0f}")

            # Update project status counts (single query instead of N queries)
            for status_name in self.status_labels:
                count = status_counts.get(status_name, 0)
                self.status_labels[status_name].setText(str(count))

            # Update table
            projects = self.project_repo.get_all()
            if not projects:
                self.table.setRowCount(1)
                empty_item = QTableWidgetItem("No projects yet — create one from the Projects page")
                empty_item.setFlags(Qt.ItemIsEnabled)
                self.table.setItem(0, 0, empty_item)
                self.table.setSpan(0, 0, 1, 5)
            else:
                self.table.setRowCount(min(len(projects), 8))
                for i, proj in enumerate(projects[:8]):
                    self.table.setItem(i, 0, QTableWidgetItem(proj["name"]))
                    self.table.setItem(i, 1, QTableWidgetItem(proj["client_name"]))

                    # Status with color coding
                    status_item = QTableWidgetItem(proj["status"])
                    status_colors = {
                        "In Progress": Colors.ACCENT_INFO,
                        "Completed": Colors.ACCENT_SUCCESS,
                        "On Hold": Colors.ACCENT_WARNING,
                    }
                    color = status_colors.get(proj["status"], Colors.TEXT_SECONDARY)
                    status_item.setForeground(QColor(color))
                    self.table.setItem(i, 2, status_item)

                    self.table.setItem(i, 3, QTableWidgetItem(proj["deadline"] or "—"))
                    self.table.setItem(i, 4, QTableWidgetItem(
                        f"₹{proj['budget']:,.0f}" if proj["budget"] else "—"
                    ))
        except Exception:
            pass  # Dashboard should never crash
