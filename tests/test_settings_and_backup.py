"""Tests for the settings service, backup/restore, CSV exporter, and migrations."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from app.core.backup_service import BackupService
from app.core.csv_exporter import CSVExporter
from app.core.settings_service import BusinessProfile, SettingsService
from app.data.database import Database
from app.data.repositories.client_repo import ClientRepository
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.project_repo import ProjectRepository


# ---------------------------------------------------------------------------
# Migrations / settings table
# ---------------------------------------------------------------------------

class TestMigrations:
    def test_app_settings_table_exists_after_initialize(self, db):
        rows = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='app_settings'"
        )
        assert len(rows) == 1

    def test_schema_version_is_recorded(self, db):
        rows = db.execute("SELECT MAX(version) as v FROM schema_version")
        assert rows[0]["v"] >= 1


# ---------------------------------------------------------------------------
# Settings service
# ---------------------------------------------------------------------------

class TestSettingsService:
    def test_first_run_flag_round_trip(self, db):
        s = SettingsService(db)
        assert s.is_first_run() is True
        s.mark_first_run_done()
        assert s.is_first_run() is False

    def test_save_and_load_business_profile(self, db):
        s = SettingsService(db)
        profile = BusinessProfile(
            name="Acme Studio",
            email="hello@acme.in",
            phone="+91 90000 00000",
            address="Mumbai",
            gstin="22AAAAA0000A1Z5",
            upi_id="acme@upi",
            upi_name="Acme Studio",
        )
        s.save_business(profile)

        loaded = s.get_business()
        assert loaded.name == "Acme Studio"
        assert loaded.email == "hello@acme.in"
        assert loaded.gstin == "22AAAAA0000A1Z5"
        assert loaded.is_configured is True

    def test_business_export_returns_dict(self, db):
        s = SettingsService(db)
        s.save_business(BusinessProfile(name="X", upi_id="x@upi"))
        d = s.export_business_as_dict()
        assert d["name"] == "X"
        assert d["upi_id"] == "x@upi"

    def test_default_due_days_round_trip(self, db):
        s = SettingsService(db)
        assert s.get_default_due_days() == 14
        s.set_default_due_days(30)
        assert s.get_default_due_days() == 30

    def test_default_due_days_invalid_value_falls_back(self, db):
        s = SettingsService(db)
        # Manually corrupt the setting
        s.repo.set("default_due_days", "abc")
        assert s.get_default_due_days(fallback=21) == 21


# ---------------------------------------------------------------------------
# CSV exporter
# ---------------------------------------------------------------------------

class TestCSVExporter:
    def test_export_clients(self, db, tmp_path):
        ClientRepository(db).add("Alice", "a@x.com", "9999", "Mumbai", "Acme")
        out = tmp_path / "clients.csv"
        CSVExporter(db).export_clients(out)

        with open(out, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        # Header + 1 data row
        assert len(rows) == 2
        assert "name" in rows[0]
        assert rows[1][rows[0].index("name")] == "Alice"

    def test_export_invoices(self, db, tmp_path):
        cid = ClientRepository(db).add("C", "c@x.com", "", "", "")
        pid = ProjectRepository(db).add(cid, "P", "Design", "", "2026-12-01", 0)
        InvoiceRepository(db).add(pid, "INV-A", 1000, 180, 1180, "2026-12-01")

        out = tmp_path / "invoices.csv"
        CSVExporter(db).export_invoices(out)

        with open(out, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
        assert len(rows) == 2
        assert rows[1][rows[0].index("invoice_number")] == "INV-A"


# ---------------------------------------------------------------------------
# Backup / restore
# ---------------------------------------------------------------------------

class TestBackupService:
    def test_create_backup_writes_zip(self, tmp_path, monkeypatch):
        # Use an isolated DB path so we don't touch the real one
        db_path = tmp_path / "test.db"
        from app.config import DATA_DIR  # noqa: F401  (ensures init)
        import app.core.backup_service as backup_module
        import app.config as cfg

        monkeypatch.setattr(cfg, "DB_PATH", db_path, raising=False)
        monkeypatch.setattr(backup_module, "DB_PATH", db_path, raising=False)

        db = Database(db_path)
        db.initialize()
        ClientRepository(db).add("Backup Tester", "b@x.com", "", "", "")

        backup = BackupService(db)
        zip_path = tmp_path / "out.zip"
        result = backup.create_backup(zip_path)
        assert result.exists()
        assert result.stat().st_size > 0

        # Manifest exists inside the zip
        import zipfile
        with zipfile.ZipFile(result) as zf:
            assert "smartdesk_manifest.txt" in zf.namelist()

    def test_restore_invalid_file_raises(self, tmp_path, db):
        bad = tmp_path / "not-a-backup.zip"
        # Create an empty/garbage zip
        import zipfile
        with zipfile.ZipFile(bad, "w") as zf:
            zf.writestr("random.txt", "hello")

        with pytest.raises(ValueError):
            BackupService(db).restore_backup(bad)
