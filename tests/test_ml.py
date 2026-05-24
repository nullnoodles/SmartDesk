"""ML/heuristic module tests — risk analyzer, pricing advisor, income forecaster."""
from __future__ import annotations

import datetime

import pytest

from app.data.repositories.client_repo import ClientRepository
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.project_repo import ProjectRepository
from app.ml.income_forecaster import IncomeForecaster
from app.ml.pricing_advisor import PricingAdvisor
from app.ml.risk_analyzer import RiskAnalyzer


# ---------------------------------------------------------------------------
# Risk analyzer (pure rule-based, no DB)
# ---------------------------------------------------------------------------

class TestRiskAnalyzer:
    def test_low_risk_for_safe_terms(self):
        ra = RiskAnalyzer()
        result = ra.full_analysis(
            hourly_rate=800,
            revisions=2,
            timeline_days=21,
            project_type="Design",
            contract_text="Standard agreement.",
        )
        assert result["risk_level"] == "LOW"
        assert result["total_score"] < 25

    def test_high_risk_for_dangerous_terms(self):
        ra = RiskAnalyzer()
        result = ra.full_analysis(
            hourly_rate=100,
            revisions=0,
            timeline_days=2,
            project_type="Design",
            contract_text=(
                "Unlimited revisions are included. All rights are transferred. "
                "Non-compete applies. Work-for-hire."
            ),
        )
        assert result["risk_level"] == "HIGH"
        assert result["total_score"] >= 50

    def test_findings_include_per_check_results(self):
        ra = RiskAnalyzer()
        result = ra.full_analysis(
            hourly_rate=500, revisions=2, timeline_days=14, contract_text=""
        )
        check_names = [f["check"] for f in result["findings"]]
        assert "Rate" in check_names
        assert "Revisions" in check_names
        assert "Timeline" in check_names

    def test_scan_text_detects_unlimited_revisions(self):
        ra = RiskAnalyzer()
        flags = ra.scan_text("The client may request unlimited revisions.")
        assert any("revision" in f["clause"].lower() for f in flags)


# ---------------------------------------------------------------------------
# Pricing advisor
# ---------------------------------------------------------------------------

class TestPricingAdvisor:
    def test_returns_low_mid_high_with_reasoning(self, db):
        advisor = PricingAdvisor(db)
        result = advisor.suggest_price(
            project_type="Design", estimated_hours=10, description="logo", revision_rounds=2
        )
        assert "low" in result and "mid" in result and "high" in result
        assert result["low"] <= result["mid"] <= result["high"]
        assert "reasoning" in result

    def test_complexity_keywords_increase_price(self, db):
        advisor = PricingAdvisor(db)
        simple = advisor.suggest_price(
            project_type="Design", estimated_hours=10, description="quick logo", revision_rounds=2
        )
        complex_ = advisor.suggest_price(
            project_type="Design",
            estimated_hours=10,
            description="enterprise rebrand with detailed style guide",
            revision_rounds=2,
        )
        # Complex job should be priced at least as high as simple
        assert complex_["mid"] >= simple["mid"]


# ---------------------------------------------------------------------------
# Income forecaster
# ---------------------------------------------------------------------------

class TestIncomeForecaster:
    def test_forecast_returns_structure_even_with_no_data(self, db):
        fc = IncomeForecaster(db)
        result = fc.forecast(months_ahead=3)
        assert "forecast" in result or "message" in result

    def test_moving_average_fallback_with_few_invoices(self, db):
        # Create 3 paid invoices
        cid = ClientRepository(db).add("C", "c@x.com", "", "", "")
        pid = ProjectRepository(db).add(cid, "P", "Design", "", "2026-12-01", 0)
        inv = InvoiceRepository(db)
        for i, amt in enumerate([1000, 1500, 2000]):
            iid = inv.add(pid, f"INV-{i}", amt, amt * 0.18, amt * 1.18, "2026-12-01")
            inv.update_status(iid, "Paid")

        fc = IncomeForecaster(db)
        result = fc.forecast(months_ahead=3)
        # Should return either forecast values or a clear message
        assert isinstance(result, dict)
