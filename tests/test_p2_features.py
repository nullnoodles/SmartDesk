"""Tests for P2 stretch goal features: SMTP service, receipt OCR, charts."""
from __future__ import annotations

import os

import pytest

from app.core.email_service import EmailService, SMTPConfig
from app.core.receipt_ocr import ReceiptOCR


# ---------------------------------------------------------------------------
# Email service
# ---------------------------------------------------------------------------

class TestEmailService:
    def test_config_round_trip(self, db):
        svc = EmailService(db)
        cfg = SMTPConfig(
            host="smtp.example.com",
            port=587,
            username="me@example.com",
            password="secret",
            from_addr="me@example.com",
            use_tls=True,
        )
        svc.save_config(cfg)
        loaded = svc.get_config()
        assert loaded.host == "smtp.example.com"
        assert loaded.port == 587
        assert loaded.username == "me@example.com"
        assert loaded.password == "secret"
        assert loaded.from_addr == "me@example.com"
        assert loaded.use_tls is True

    def test_default_config_is_unconfigured(self, db):
        svc = EmailService(db)
        cfg = svc.get_config()
        assert cfg.is_configured is False

    def test_invalid_port_falls_back(self, db):
        svc = EmailService(db)
        # Manually corrupt port
        svc.repo.set("smtp_port", "abc")
        cfg = svc.get_config()
        assert cfg.port == 587

    def test_send_without_config_raises(self, db):
        svc = EmailService(db)
        with pytest.raises(RuntimeError):
            svc.send("test@example.com", "subject", "body")

    def test_invoice_template(self):
        subject = EmailService.invoice_subject("INV-2026-0001", "Acme Studio")
        assert "INV-2026-0001" in subject
        assert "Acme Studio" in subject

        body = EmailService.invoice_body(
            client_name="Priya",
            invoice_number="INV-2026-0001",
            total=1180.0,
            due_date="2026-12-01",
            business_name="Acme Studio",
        )
        assert "Priya" in body
        assert "INV-2026-0001" in body
        assert "1,180.00" in body
        assert "Acme Studio" in body

    def test_overdue_template(self):
        subject = EmailService.overdue_subject("INV-2026-0042")
        assert "INV-2026-0042" in subject
        assert "overdue" in subject.lower()

        body = EmailService.overdue_body(
            client_name="Rahul",
            invoice_number="INV-2026-0042",
            total=5000.0,
            due_date="2026-01-01",
            days_overdue=15,
            business_name="Acme",
        )
        assert "Rahul" in body
        assert "15" in body
        assert "overdue" in body.lower()


# ---------------------------------------------------------------------------
# Receipt OCR
# ---------------------------------------------------------------------------

class TestReceiptOCR:
    def test_amount_extraction_from_text(self):
        ocr = ReceiptOCR()
        # Internal heuristic, no Tesseract needed
        assert ocr._guess_amount("Subtotal: 100\nTotal: ₹1,250.00") == 1250.0
        assert ocr._guess_amount("Grand Total $99.99") == 99.99
        assert ocr._guess_amount("Amount Paid 250") == 250.0
        assert ocr._guess_amount("No total here") is None

    def test_date_extraction(self):
        ocr = ReceiptOCR()
        assert ocr._guess_date("Bill date: 12/05/2026") == "12/05/2026"
        assert ocr._guess_date("Date 2026-05-12") == "2026-05-12"
        assert ocr._guess_date("12 May 2026") == "12 May 2026"
        assert ocr._guess_date("nothing") is None

    def test_extract_missing_file(self, tmp_path):
        ocr = ReceiptOCR()
        result = ocr.extract(tmp_path / "missing.png")
        assert result["success"] is False
        assert "not found" in result["error"].lower()


# ---------------------------------------------------------------------------
# Charts (smoke — instantiate against an empty in-memory DB)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication.instance() or QApplication(sys.argv)
    yield app


class TestCharts:
    def test_income_chart_builds_with_no_data(self, db, qapp):
        from app.ui.widgets.charts import IncomeTrendChart

        chart = IncomeTrendChart(db)
        chart.refresh()
        assert chart.figure is not None

    def test_project_type_chart_builds_with_no_data(self, db, qapp):
        from app.ui.widgets.charts import ProjectTypeChart

        chart = ProjectTypeChart(db)
        chart.refresh()
        assert chart.figure is not None
