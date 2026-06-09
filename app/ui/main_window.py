"""
Main application window with sidebar, top bar, and stacked pages.

Modern, professional layout with proper spacing and visual hierarchy.
All functionality preserved while enhancing the visual design.
"""
from __future__ import annotations

from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
    QGraphicsOpacityEffect,
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
from app.ui.styles.theme import Colors


class MainWindow(QMainWindow):
    """
    Root window — professional sidebar + top bar + stacked content pages.
    
    Layout Structure:
    ┌─────────────────────────────────────────┐
    │ [Sidebar] │ [Top Bar              ]     │
    │           │ ─────────────────────────── │
    │           │                             │
    │  Nav      │    Page Content             │
    │  Items    │    (QStackedWidget)         │
    │           │                             │
    │  User     │                             │
    │  Card     │                             │
    └─────────────────────────────────────────┘
    """

    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        
        # Window configuration
        self.setWindowTitle("SmartDesk — Freelancer Management")
        self.setMinimumSize(1280, 800)
        self.resize(1440, 900)  # Optimal default size
        
        # Set window icon
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        elif ICON_PNG_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PNG_PATH)))

        # Apply window-level styling for consistent dark theme
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {Colors.BG_DARK};
            }}
        """)

        # Build UI structure
        self._setup_status_bar()
        self._setup_central_widget()
        self._setup_pages()
        self._connect_signals()
        
        # Show dashboard by default
        self.show_page("dashboard")

    def _setup_status_bar(self) -> None:
        """Configure the bottom status bar with app version info."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"SmartDesk v{APP_VERSION} — Ready")

    def _setup_central_widget(self) -> None:
        """
        Build the main layout: sidebar | (top bar / content stack).
        No margins or spacing for edge-to-edge design.
        """
        central = QWidget()
        central.setObjectName("app_shell")
        self.setCentralWidget(central)
        
        # Root horizontal layout: sidebar + right column
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Sidebar navigation (fixed width)
        self.sidebar = Sidebar()
        root_layout.addWidget(self.sidebar)

        # Right column: top bar above content stack
        right_column = QFrame()
        right_column.setObjectName("right_workspace")
        right_layout = QVBoxLayout(right_column)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top bar (search + user info)
        self.top_bar = TopBar(user_name="Freelancer", role="OFFLINE WORKSPACE")
        right_layout.addWidget(self.top_bar)

        # Content stack (all page widgets)
        self.stack = QStackedWidget()
        right_layout.addWidget(self.stack, 1)
        
        root_layout.addWidget(right_column, 1)

    def _setup_pages(self) -> None:
        """
        Initialize all page widgets and add them to the stack.
        Each page receives the database instance for data access.
        """
        self.pages: dict[str, QWidget] = {}
        
        # Define all pages with their IDs
        page_definitions = [
            ("dashboard", DashboardPage(self.db)),
            ("clients", ClientsPage(self.db)),
            ("projects", ProjectsPage(self.db)),
            ("invoices", InvoicesPage(self.db)),
            ("time", TimePage(self.db)),
            ("contracts", ContractsPage(self.db)),
            ("analytics", AnalyticsPage(self.db)),
            ("settings", SettingsPage(self.db)),
        ]
        
        # Register each page
        for page_id, widget in page_definitions:
            self._add_page(page_id, widget)

    def _add_page(self, page_id: str, widget: QWidget) -> None:
        """Register a page widget in both the dictionary and the stack."""
        self.pages[page_id] = widget
        self.stack.addWidget(widget)

    def _connect_signals(self) -> None:
        """Wire up sidebar navigation to page switching and global data change signals."""
        self.sidebar.page_changed.connect(self._switch_page)
        
        # Connect to global data change signal to refresh relevant pages
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app and hasattr(app, "data_changed"):
            app.data_changed.signal.connect(self._on_data_changed)

    def show_page(self, page_id: str) -> None:
        """
        Programmatically navigate to a page.
        Updates both the stack and sidebar selection state.
        
        Args:
            page_id: The unique identifier for the page (e.g., "dashboard")
        """
        if page_id not in self.pages:
            return
            
        # Update stack to show the page
        self.stack.setCurrentWidget(self.pages[page_id])
        
        # Sync sidebar selection
        self.sidebar.set_active(page_id)
        
        # Refresh page data if supported
        page = self.pages[page_id]
        if hasattr(page, "refresh"):
            page.refresh()
        
        # Update status bar with page context
        page_names = {
            "dashboard": "Dashboard",
            "clients": "Clients",
            "projects": "Projects",
            "invoices": "Invoices",
            "time": "Time Tracking",
            "contracts": "Contracts",
            "analytics": "AI Analytics",
            "settings": "Settings",
        }
        page_name = page_names.get(page_id, page_id.title())
        self.status_bar.showMessage(
            f"SmartDesk v{APP_VERSION} — {page_name}"
        )

    def _switch_page(self, page_id: str) -> None:
        """
        Internal handler for sidebar navigation signals.
        Delegates to show_page for consistent behavior.
        
        Args:
            page_id: The unique identifier for the page
        """
        self.show_page(page_id)

    def _on_data_changed(self) -> None:
        """
        Handle global data change signals by refreshing relevant pages.
        This ensures all pages stay in sync when data is modified.
        """
        # Always refresh dashboard as it aggregates data from all sources
        if "dashboard" in self.pages:
            dashboard = self.pages["dashboard"]
            if hasattr(dashboard, "refresh"):
                dashboard.refresh()
        
        # Refresh the currently visible page to show updated data
        current_widget = self.stack.currentWidget()
        if current_widget and hasattr(current_widget, "refresh"):
            current_widget.refresh()
            
        # Optionally refresh other critical pages that might cache data
        # This can be expanded based on which pages need real-time updates
        pages_to_refresh = ["clients", "projects", "invoices"]
        for page_id in pages_to_refresh:
            if page_id in self.pages:
                page = self.pages[page_id]
                if hasattr(page, "refresh"):
                    # Only refresh if it's not the current page (already refreshed above)
                    if page != current_widget:
                        page.refresh()
