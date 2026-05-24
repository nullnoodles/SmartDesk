"""Main application window with sidebar navigation and stacked pages."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QStatusBar,
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt

from app.config import ICON_PATH, ICON_PNG_PATH, APP_VERSION
from app.data.database import Database
from app.ui.widgets.sidebar import Sidebar
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.clients_page import ClientsPage
from app.ui.pages.projects_page import ProjectsPage
from app.ui.pages.invoices_page import InvoicesPage
from app.ui.pages.time_page import TimePage
from app.ui.pages.contracts_page import ContractsPage
from app.ui.pages.analytics_page import AnalyticsPage
from app.ui.pages.settings_page import SettingsPage


class MainWindow(QMainWindow):
    """Root window — sidebar + stacked content pages."""

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.setWindowTitle("SmartDesk — Freelancer Management")
        self.setMinimumSize(1200, 750)

        # Window icon
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        elif ICON_PNG_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PNG_PATH)))

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"SmartDesk v{APP_VERSION} — Ready")

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar()
        layout.addWidget(self.sidebar)

        # Page stack
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Register pages
        self.pages: dict[str, QWidget] = {}
        self._add_page("dashboard", DashboardPage(db))
        self._add_page("clients", ClientsPage(db))
        self._add_page("projects", ProjectsPage(db))
        self._add_page("invoices", InvoicesPage(db))
        self._add_page("time", TimePage(db))
        self._add_page("contracts", ContractsPage(db))
        self._add_page("analytics", AnalyticsPage(db))
        self._add_page("settings", SettingsPage(db))

        # Connect sidebar
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
            # Refresh page data when switching
            page = self.pages[page_id]
            if hasattr(page, "refresh"):
                page.refresh()
