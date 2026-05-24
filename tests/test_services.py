"""Service layer tests — invoice service, time tracker."""
from __future__ import annotations

import datetime

import pytest

from app.config import GST_RATE
from app.core.invoice_service import InvoiceService
from app.core.time_tracker import TimeTracker
from app.data.repositories.client_repo import ClientRepository
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.project_repo import ProjectRepository


def _make_project(db) -> int:
    cid = ClientRepository(db).add("Client", "c@x.com", "", "", "")
    return ProjectRepository(db).add(cid, "Project", "Design", "", "2026-12-01", 0)


# ---------------------------------------------------------------------------
# Invoice service
# ---------------------------------------------------------------------------

class TestInvoiceService:
    def test_creates_invoice_with_gst(self, db):
        pid = _make_project(db)
        service = InvoiceService(db)
        number = service.create_invoice(pid, amount=1000, due_days=14)

        repo = InvoiceRepository(db)
        inv = repo.get_by_number(number)
        assert inv is not None
        assert inv["amount"] == pytest.approx(1000)
        assert inv["tax"] == pytest.approx(1000 * GST_RATE)
        assert inv["total"] == pytest.approx(1180)

    def test_due_date_offset(self, db):
        pid = _make_project(db)
        service = InvoiceService(db)
        number = service.create_invoice(pid, amount=500, due_days=7)
        inv = InvoiceRepository(db).get_by_number(number)
        expected = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
        assert inv["due_date"] == expected

    def test_mark_paid_and_cancelled(self, db):
        pid = _make_project(db)
        service = InvoiceService(db)
        number = service.create_invoice(pid, amount=500, due_days=7)
        repo = InvoiceRepository(db)
        inv = repo.get_by_number(number)
        assert inv["status"] == "Unpaid"

        service.mark_paid(inv["id"])
        assert repo.get_by_id(inv["id"])["status"] == "Paid"

        service.mark_cancelled(inv["id"])
        assert repo.get_by_id(inv["id"])["status"] == "Cancelled"


# ---------------------------------------------------------------------------
# Time tracker
# ---------------------------------------------------------------------------

class TestTimeTracker:
    def test_start_then_stop_logs_session(self, db):
        pid = _make_project(db)
        tracker = TimeTracker(db)
        tracker.start(pid, "drafting")
        assert tracker.is_running
        hours = tracker.stop()
        assert hours >= 0
        assert not tracker.is_running

    def test_double_start_raises(self, db):
        pid = _make_project(db)
        tracker = TimeTracker(db)
        tracker.start(pid)
        with pytest.raises(RuntimeError):
            tracker.start(pid)

    def test_stop_without_start_raises(self, db):
        tracker = TimeTracker(db)
        with pytest.raises(RuntimeError):
            tracker.stop()

    def test_add_manual(self, db):
        from app.data.repositories.time_log_repo import TimeLogRepository

        pid = _make_project(db)
        tracker = TimeTracker(db)
        tracker.add_manual(pid, 2.5, "research")
        repo = TimeLogRepository(db)
        assert repo.total_hours_for_project(pid) == pytest.approx(2.5)
