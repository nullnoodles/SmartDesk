"""Smoke tests — instantiate each page widget to catch __init__/refresh regressions."""
from __future__ import annotations

import os
import sys

import pytest

# Force Qt to use offscreen platform so tests run headless on CI/local without display
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@pytest.fixture(scope="module")
def qapp():
    """Single QApplication for the whole smoke-test module."""
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication(sys.argv)
    yield app


class TestPagesSmoke:
    def test_clients_page(self, db, qapp):
        from app.ui.pages.clients_page import ClientsPage
        page = ClientsPage(db)
        page.refresh()  # second refresh should not crash

        assert page.objectName() == "clients_page"

        # Test each card's layout, spacing, and styling constraints
        for card in (page.card_new, page.card_avg, page.card_retention):
            assert card.objectName() == "statCard"

        # Test charts card
        assert page.chart_card.objectName() == "card"

        # Test table card
        assert page.table_card.objectName() == "card"

    def test_clients_page_pagination(self, db, qapp):
        from app.ui.pages.clients_page import ClientsPage
        page = ClientsPage(db)
        
        # Seed 15 clients in DB
        db.execute("DELETE FROM clients")
        for i in range(15):
            db.execute(
                "INSERT INTO clients (name, email, phone, address, company) VALUES (?, ?, ?, ?, ?)",
                (f"Client {i}", f"client{i}@example.com", "123456", "Addr", f"Company {i}")
            )
            
        page.refresh()
        
        # Table must display exactly 10 clients on page 1
        assert page.table.rowCount() == 10
        assert page.current_page == 0
        
        # Check table height is dynamic via sizeHint matching computed height
        hh = page.table.horizontalHeader().height()
        if hh <= 0:
            hh = 38
        expected_h1 = hh + sum(page.table.rowHeight(r) for r in range(page.table.rowCount())) + 4
        assert page.table.sizeHint().height() == expected_h1
        
        # Click Next page
        page._next_page()
        assert page.current_page == 1
        assert page.table.rowCount() == 5
        
        hh = page.table.horizontalHeader().height()
        if hh <= 0:
            hh = 38
        expected_h2 = hh + sum(page.table.rowHeight(r) for r in range(page.table.rowCount())) + 4
        assert page.table.sizeHint().height() == expected_h2


    def test_clients_page_dynamic_stats(self, db, qapp):
        from app.ui.pages.clients_page import ClientsPage
        page = ClientsPage(db)
        
        # Clear database
        db.execute("DELETE FROM clients")
        db.execute("DELETE FROM projects")
        
        # Add two clients
        c1_id = db.execute_returning_id("INSERT INTO clients (name, created_date) VALUES ('C1', DATE('now'))")
        c2_id = db.execute_returning_id("INSERT INTO clients (name, created_date) VALUES ('C2', DATE('now'))")
        
        # Add projects for c1 (active) and c2 (completed)
        db.execute("INSERT INTO projects (client_id, name, status, budget) VALUES (?, 'P1', 'In Progress', 50000)", (c1_id,))
        db.execute("INSERT INTO projects (client_id, name, status, budget) VALUES (?, 'P2', 'Completed', 30000)", (c2_id,))
        
        page.refresh()
        
        # 2 clients added this month
        assert page.card_new._value.text() == "2"
        # Total revenue = 80000. Active clients = 2.
        # Average revenue = 80000 / 2 = 40000 (₹40K)
        assert page.card_avg._value.text() == "₹40K"
        # Retention: 1 out of 2 clients has completed projects = 50%
        assert page.card_retention._value.text() == "50%"

    def test_clients_page_clear_all(self, db, qapp):
        from app.ui.pages.clients_page import ClientsPage, DeleteConfirmDialog
        from PySide6.QtWidgets import QLabel

        # Seed some clients
        db.execute("DELETE FROM clients")
        db.execute("INSERT INTO clients (name) VALUES ('C1')")
        db.execute("INSERT INTO clients (name) VALUES ('C2')")

        page = ClientsPage(db)
        page.refresh()
        
        # Check that we have 2 rows initially
        assert page.table.rowCount() == 2

        # Check Clear All button exists and is styled
        assert page.clear_btn is not None
        assert page.clear_btn.text() == " Clear All"
        assert page.clear_btn.height() == 36

        # Test the DeleteConfirmDialog with is_clear_all=True
        dialog = DeleteConfirmDialog(parent=page, is_clear_all=True)
        assert dialog.windowTitle() == "Clear All Clients"
        
        # Simulate clear all directly
        db.execute("DELETE FROM clients")
        page.refresh()

        # Check empty state is displayed (table has 1 row with empty state widget)
        assert page.table.rowCount() == 1
        empty_widget = page.table.cellWidget(0, 0)
        assert isinstance(empty_widget, QLabel)
        assert empty_widget.text() == "No clients found. Add your first client to get started."

        # Check KPIs are updated
        assert page.card_new._value.text() == "0"

    def test_projects_page(self, db, qapp):
        from app.ui.pages.projects_page import ProjectsPage
        page = ProjectsPage(db)
        page.refresh()
        assert page.table.columnCount() == 8
        assert page.table.verticalHeader().defaultSectionSize() == 48
        assert not page.table.alternatingRowColors()

    def test_invoices_page(self, db, qapp):
        from app.ui.pages.invoices_page import InvoicesPage
        page = InvoicesPage(db)
        page.refresh()

    def test_time_page(self, db, qapp):
        from app.ui.pages.time_page import TimePage
        page = TimePage(db)
        page.refresh()

    def test_contracts_page_builds_and_refreshes(self, db, qapp):
        """Regression: ContractsPage previously crashed on refresh."""
        from app.ui.pages.contracts_page import ContractsPage
        page = ContractsPage(db)
        # If __init__ did not build UI, this would AttributeError
        assert page.project_combo is not None
        page.refresh()

        # Test background color is set correctly
        assert "background-color: #12131d" in page.styleSheet()

        # Test analyzer widgets exist
        assert page.circular_score is not None
        assert page.multi_progress is not None
        assert page.upload_area is not None
        assert len(page.risk_cards) == 5
        assert "ip_transfer" in page.risk_cards
        assert "payment_terms" in page.risk_cards
        assert "revision_scope" in page.risk_cards
        assert "termination" in page.risk_cards
        assert "indemnity" in page.risk_cards

    def test_dashboard_page(self, db, qapp):
        from app.ui.pages.dashboard_page import DashboardPage, _format_short_currency
        from PySide6.QtWidgets import QSizePolicy, QWidget

        # Test formatting function
        assert _format_short_currency(120339) == "₹1.2L"
        assert _format_short_currency(114896) == "₹1.1L"
        assert _format_short_currency(8450) == "₹8.4K"
        assert _format_short_currency(0) == "₹0"

        page = DashboardPage(db)
        page.refresh()

        assert page.objectName() == "dashboard_page"

        # Test each card's layout, spacing, and styling constraints
        for card in (page.card_revenue, page.card_projects, page.card_pending, page.card_hours):
            assert card.objectName() == "statCard"
            assert "background-color: #1a1b26" in card.styleSheet()
            assert "border-radius: 12px" in card.styleSheet()
            assert card.minimumHeight() == 140
            assert card.maximumHeight() == 140
            assert card.sizePolicy().horizontalPolicy() == QSizePolicy.Expanding
            assert card.sizePolicy().verticalPolicy() == QSizePolicy.Fixed

            # Internal layout margins and spacing
            margin = card.layout().contentsMargins()
            assert margin.left() == 20
            assert margin.top() == 16
            assert margin.right() == 20
            assert margin.bottom() == 16
            assert card.layout().spacing() == 6

        # Test other cards on dashboard
        from PySide6.QtWidgets import QFrame
        frames = page.findChildren(QFrame)
        cards = [f for f in frames if f.objectName() == "card"]
        assert len(cards) >= 3

        # Test specific label styling
        assert "color: #8B8FA8; background: transparent; border: none;" in page.card_revenue._label.styleSheet()
        assert "color: #FFFFFF; background: transparent; border: none;" in page.card_revenue._value.styleSheet()
        assert "background: transparent; border: none;" in page.card_hours._sub.styleSheet()

        # Test container layout (stats_layout) margins and spacing
        content_widget = page.findChild(QWidget, "dashboard_content")
        assert content_widget is not None
        main_layout = content_widget.layout()
        stats_layout = main_layout.itemAt(0).layout()
        assert stats_layout is not None
        assert stats_layout.spacing() == 16
        stats_margin = stats_layout.contentsMargins()
        assert stats_margin.left() == 0
        assert stats_margin.top() == 0
        assert stats_margin.right() == 0
        assert stats_margin.bottom() == 0

    def test_analytics_page(self, db, qapp):
        from app.ui.pages.analytics_page import AnalyticsPage
        page = AnalyticsPage(db)
        page.refresh()

        # Test background color is set correctly
        assert "background-color: #12131d" in page.styleSheet()

        # Test matplotlib figure background color
        facecolor = page.chart_canvas.figure.get_facecolor()
        assert abs(facecolor[0] - 26/255) < 1e-4
        assert abs(facecolor[1] - 27/255) < 1e-4
        assert abs(facecolor[2] - 38/255) < 1e-4


class TestNewPagesSmoke:
    def test_settings_page_builds(self, db, qapp):
        from app.ui.pages.settings_page import SettingsPage

        page = SettingsPage(db)
        page.refresh()
        assert page.name_input is not None

        # Test background color is set correctly
        assert "background-color: #12131d" in page.styleSheet()
