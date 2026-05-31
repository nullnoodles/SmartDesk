"""Main application window with sidebar, top bar, and stacked pages."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app.config import APP_VERSION, ICON_PATH, ICON_PNG_PATH
from app.data.database import Database
from app.ui.pages.analytics_page import AnalyticsPage
from app.ui.pages.clients_page import ClientsPage
from app.ui.pages.contracts_page import ContractsPage
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.invoices_page import InvoicesPage
from app.ui.pages.projects_page import ProjectsPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.pages.time_page import TimePage
from app.ui.widgets.sidebar import Sidebar
from app.ui.widgets.top_bar import TopBar


class MainWindow(QMainWindow):
    """Root window — sidebar + top bar + stacked content pages."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setWindowTitle("SmartDesk — Freelancer Management")
        self.setMinimumSize(1280, 800)

        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        elif ICON_PNG_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PNG_PATH)))

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"SmartDesk v{APP_VERSION} — Ready")

        # Central widget: sidebar | (top bar / stack)
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        root_layout.addWidget(self.sidebar)

        # Right column: top bar + stack
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.top_bar = TopBar(user_name="Freelancer", role="OFFLINE WORKSPACE")
        right_layout.addWidget(self.top_bar)

        self.stack = QStackedWidget()
        right_layout.addWidget(self.stack, 1)
        root_layout.addWidget(right_column, 1)

        # Pages
        self.pages: dict[str, QWidget] = {}
        self._add_page("dashboard", DashboardPage(db))
        self._add_page("clients", ClientsPage(db))
        self._add_page("projects", ProjectsPage(db))
        self._add_page("invoices", InvoicesPage(db))
        self._add_page("time", TimePage(db))
        self._add_page("contracts", ContractsPage(db))
        self._add_page("analytics", AnalyticsPage(db))
        self._add_page("settings", SettingsPage(db))

        self.sidebar.page_changed.connect(self._switch_page)

    def _add_page(self, page_id: str, widget: QWidget) -> None:
        self.pages[page_id] = widget
        self.stack.addWidget(widget)

    def show_page(self, page_id: str) -> None:
        """Programmatically navigate to a page (also updates sidebar selection)."""
        if page_id in self.pages:
            self.stack.setCurrentWidget(self.pages[page_id])
            self.sidebar.set_active(page_id)
            page = self.pages[page_id]
            if hasattr(page, "refresh"):
                page.refresh()

    def _switch_page(self, page_id: str) -> None:
        if page_id in self.pages:
            self.stack.setCurrentWidget(self.pages[page_id])
            page = self.pages[page_id]
            if hasattr(page, "refresh"):
                page.refresh()
