"""Repository layer tests — exercise CRUD against an isolated SQLite file."""
from __future__ import annotations

import datetime

import pytest

from app.data.repositories.client_repo import ClientRepository
from app.data.repositories.contract_repo import ContractRepository
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.payment_repo import PaymentRepository
from app.data.repositories.project_repo import ProjectRepository
from app.data.repositories.task_repo import TaskRepository
from app.data.repositories.time_log_repo import TimeLogRepository


# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------

class TestClientRepository:
    def test_add_and_get(self, db):
        repo = ClientRepository(db)
        cid = repo.add("Alice", "alice@example.com", "+91 9999900000", "Mumbai", "Acme")
        assert cid > 0

        client = repo.get_by_id(cid)
        assert client["name"] == "Alice"
        assert client["email"] == "alice@example.com"

    def test_get_all_orders_and_counts(self, db):
        repo = ClientRepository(db)
        repo.add("Alice", "a@x.com", "", "", "")
        repo.add("Bob", "b@x.com", "", "", "")
        assert repo.count() == 2
        assert len(repo.get_all()) == 2

    def test_search_by_name(self, db):
        repo = ClientRepository(db)
        repo.add("Alice Designs", "a@x.com", "", "", "Acme")
        repo.add("Bob Studios", "b@x.com", "", "", "BobCo")
        results = repo.search("alice")
        assert len(results) == 1
        assert results[0]["name"] == "Alice Designs"

    def test_update_and_delete(self, db):
        repo = ClientRepository(db)
        cid = repo.add("Alice", "a@x.com", "", "", "")
        repo.update(cid, "Alice B", "alice.b@x.com", "9999", "Pune", "Acme")
        client = repo.get_by_id(cid)
        assert client["name"] == "Alice B"
        assert client["phone"] == "9999"

        repo.delete(cid)
        assert repo.get_by_id(cid) is None


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------

class TestProjectRepository:
    def _make_client(self, db) -> int:
        return ClientRepository(db).add("Client", "c@x.com", "", "", "")

    def test_add_and_get(self, db):
        cid = self._make_client(db)
        repo = ProjectRepository(db)
        pid = repo.add(cid, "Logo Design", "Design", "Brand logo", "2026-12-01", 5000)
        assert pid > 0

        proj = repo.get_by_id(pid)
        assert proj["name"] == "Logo Design"
        assert proj["client_id"] == cid

    def test_default_status(self, db):
        cid = self._make_client(db)
        repo = ProjectRepository(db)
        pid = repo.add(cid, "Logo", "Design", "", "2026-12-01", 0)
        assert repo.get_by_id(pid)["status"] == "Not Started"

    def test_update_changes_client(self, db):
        repo = ProjectRepository(db)
        c1 = ClientRepository(db).add("C1", "c1@x.com", "", "", "")
        c2 = ClientRepository(db).add("C2", "c2@x.com", "", "", "")
        pid = repo.add(c1, "Logo", "Design", "", "2026-12-01", 100)

        repo.update(pid, c2, "Logo v2", "Design", "tweaked", "2026-12-15", 200, "In Progress")
        proj = repo.get_by_id(pid)
        assert proj["client_id"] == c2
        assert proj["status"] == "In Progress"
        assert proj["budget"] == 200

    def test_update_without_status(self, db):
        """Edit dialog in add mode passes no status; ensure repo handles it."""
        cid = self._make_client(db)
        repo = ProjectRepository(db)
        pid = repo.add(cid, "Logo", "Design", "", "2026-12-01", 0)
        # Should not raise — status arg is optional now
        repo.update(pid, cid, "Logo v2", "Design", "", "2026-12-02", 100)
        assert repo.get_by_id(pid)["name"] == "Logo v2"

    def test_count_all_statuses(self, db):
        cid = self._make_client(db)
        repo = ProjectRepository(db)
        p1 = repo.add(cid, "A", "Design", "", "2026-12-01", 0)
        p2 = repo.add(cid, "B", "Design", "", "2026-12-01", 0)
        repo.update_status(p1, "In Progress")
        repo.update_status(p2, "Completed")
        counts = repo.count_all_statuses()
        assert counts.get("In Progress") == 1
        assert counts.get("Completed") == 1


# ---------------------------------------------------------------------------
# Invoices
# ---------------------------------------------------------------------------

class TestInvoiceRepository:
    def _make_project(self, db) -> int:
        cid = ClientRepository(db).add("C", "c@x.com", "", "", "")
        return ProjectRepository(db).add(cid, "P", "Design", "", "2026-12-01", 0)

    def test_next_invoice_number_uses_current_year(self, db):
        repo = InvoiceRepository(db)
        year = datetime.date.today().year
        num = repo.next_invoice_number()
        assert num == f"INV-{year}-0001"

    def test_next_invoice_number_increments(self, db):
        pid = self._make_project(db)
        repo = InvoiceRepository(db)
        year = datetime.date.today().year
        repo.add(pid, repo.next_invoice_number(), 1000, 180, 1180, "2026-12-01")
        repo.add(pid, repo.next_invoice_number(), 2000, 360, 2360, "2026-12-01")
        assert repo.next_invoice_number() == f"INV-{year}-0003"

    def test_total_earned_and_pending(self, db):
        pid = self._make_project(db)
        repo = InvoiceRepository(db)
        i1 = repo.add(pid, "INV-A", 1000, 180, 1180, "2026-12-01")
        i2 = repo.add(pid, "INV-B", 2000, 360, 2360, "2026-12-01")
        repo.update_status(i1, "Paid")
        assert repo.total_earned() == pytest.approx(1180)
        assert repo.total_pending() == pytest.approx(2360)

    def test_get_overdue(self, db):
        pid = self._make_project(db)
        repo = InvoiceRepository(db)
        # Past due date, still Unpaid → overdue
        repo.add(pid, "INV-OLD", 1000, 180, 1180, "2020-01-01")
        # Future due date → not overdue
        repo.add(pid, "INV-NEW", 1000, 180, 1180, "2099-01-01")
        overdue = repo.get_overdue()
        assert len(overdue) == 1
        assert overdue[0]["invoice_number"] == "INV-OLD"


# ---------------------------------------------------------------------------
# Payments
# ---------------------------------------------------------------------------

class TestPaymentRepository:
    def test_total_paid_for_invoice(self, db):
        cid = ClientRepository(db).add("C", "c@x.com", "", "", "")
        pid = ProjectRepository(db).add(cid, "P", "Design", "", "2026-12-01", 0)
        inv_repo = InvoiceRepository(db)
        iid = inv_repo.add(pid, "INV-X", 1000, 180, 1180, "2026-12-01")

        pay_repo = PaymentRepository(db)
        pay_repo.add(iid, 500, "UPI", "ref-1")
        pay_repo.add(iid, 680, "Bank", "ref-2")
        assert pay_repo.total_paid_for_invoice(iid) == pytest.approx(1180)


# ---------------------------------------------------------------------------
# Time logs
# ---------------------------------------------------------------------------

class TestTimeLogRepository:
    def test_add_and_aggregate(self, db):
        cid = ClientRepository(db).add("C", "c@x.com", "", "", "")
        pid = ProjectRepository(db).add(cid, "P", "Design", "", "2026-12-01", 0)
        repo = TimeLogRepository(db)
        repo.add(pid, "2026-05-01T10:00:00", "2026-05-01T12:00:00", 2.0, "drafting")
        repo.add(pid, "2026-05-02T10:00:00", "2026-05-02T13:30:00", 3.5, "polishing")
        assert repo.total_hours_for_project(pid) == pytest.approx(5.5)
        assert len(repo.get_recent(10)) == 2


# ---------------------------------------------------------------------------
# Tasks
# ---------------------------------------------------------------------------

class TestTaskRepository:
    def test_add_toggle_count(self, db):
        cid = ClientRepository(db).add("C", "c@x.com", "", "", "")
        pid = ProjectRepository(db).add(cid, "P", "Design", "", "2026-12-01", 0)
        repo = TaskRepository(db)
        t1 = repo.add(pid, "Sketch", "2026-06-01")
        repo.add(pid, "Refine", "2026-06-05")
        assert repo.pending_count() == 2
        repo.toggle_complete(t1)
        assert repo.pending_count() == 1


# ---------------------------------------------------------------------------
# Contracts
# ---------------------------------------------------------------------------

class TestContractRepository:
    def test_add_and_get(self, db):
        cid = ClientRepository(db).add("C", "c@x.com", "", "", "")
        pid = ProjectRepository(db).add(cid, "P", "Design", "", "2026-12-01", 0)
        repo = ContractRepository(db)
        repo.add(
            project_id=pid,
            contract_text="sample text",
            hourly_rate=500,
            revision_rounds=2,
            timeline_days=14,
            risk_score=20,
            risk_level="LOW",
            findings="[]",
        )
        rows = repo.get_all()
        assert len(rows) == 1
        assert rows[0]["risk_level"] == "LOW"
