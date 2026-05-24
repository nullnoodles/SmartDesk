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

    def test_projects_page(self, db, qapp):
        from app.ui.pages.projects_page import ProjectsPage
        page = ProjectsPage(db)
        page.refresh()

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

    def test_dashboard_page(self, db, qapp):
        from app.ui.pages.dashboard_page import DashboardPage
        page = DashboardPage(db)
        page.refresh()

    def test_analytics_page(self, db, qapp):
        from app.ui.pages.analytics_page import AnalyticsPage
        page = AnalyticsPage(db)
        page.refresh()


class TestNewPagesSmoke:
    def test_settings_page_builds(self, db, qapp):
        from app.ui.pages.settings_page import SettingsPage

        page = SettingsPage(db)
        page.refresh()
        assert page.name_input is not None
