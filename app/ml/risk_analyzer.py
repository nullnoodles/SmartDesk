"""Contract risk analyzer — rule-based scoring + NLP clause classification.

Two-layer analysis:
  Layer 1: Rule-based scoring on rate, revisions, timeline
  Layer 2: Clause classifier on contract text (uses clause_classifier.py)
"""
from __future__ import annotations

import re
from typing import Any

from app.config import MARKET_RATES


class RiskAnalyzer:
    """Analyzes contract terms and produces a risk score + findings."""

    # Regex patterns for risky clauses (fallback when classifier not trained)
    RISKY_PATTERNS = [
        (r"unlimited revision", "Unlimited revisions clause", 30),
        (r"all rights?\s*(transfer|assigned)", "Full IP rights transfer", 25),
        (r"no\s*(kill|cancellation)\s*fee", "No cancellation protection", 20),
        (r"payment.{0,20}(60|90|120)\s*days", "Long payment delay clause", 15),
        (r"non.?compete", "Non-compete restriction", 20),
        (r"work.?for.?hire", "Work-for-hire (IP loss)", 20),
        (r"indemnif", "Indemnification clause", 15),
        (r"penalty.{0,15}(late|delay)", "Late delivery penalty", 15),
    ]

    def analyze_rate(self, rate: float, project_type: str = "General") -> tuple[int, str]:
        market = MARKET_RATES.get(project_type, 500)
        if rate < market * 0.6:
            return 25, "Rate severely below market"
        elif rate < market * 0.85:
            return 15, "Rate slightly below market"
        return 0, "Rate acceptable"

    def analyze_revisions(self, rounds: int) -> tuple[int, str]:
        if rounds == 0 or rounds > 5:
            return 25, "Unlimited or excessive revisions"
        elif rounds > 3:
            return 10, "Above average revision count"
        return 0, "Revision count acceptable"

    def analyze_timeline(self, days: int) -> tuple[int, str]:
        if days < 3:
            return 25, "Extremely tight deadline"
        elif days < 7:
            return 15, "Tight deadline"
        return 0, "Timeline acceptable"

    def scan_text(self, contract_text: str) -> list[dict[str, Any]]:
        """Scan contract text for risky patterns using regex."""
        flags = []
        text_lower = contract_text.lower()
        for pattern, message, score in self.RISKY_PATTERNS:
            if re.search(pattern, text_lower):
                flags.append({"clause": message, "score": score})
        return flags

    def full_analysis(
        self,
        hourly_rate: float,
        revisions: int,
        timeline_days: int,
        project_type: str = "General",
        contract_text: str = "",
    ) -> dict[str, Any]:
        """Run complete risk analysis. Returns score, level, and findings."""
        total = 0
        findings = []

        # Rate check
        rs, rm = self.analyze_rate(hourly_rate, project_type)
        total += rs
        findings.append({"check": "Rate", "result": rm, "score": rs})

        # Revisions check
        vs, vm = self.analyze_revisions(revisions)
        total += vs
        findings.append({"check": "Revisions", "result": vm, "score": vs})

        # Timeline check
        ts, tm = self.analyze_timeline(timeline_days)
        total += ts
        findings.append({"check": "Timeline", "result": tm, "score": ts})

        # Text scan
        if contract_text:
            for flag in self.scan_text(contract_text):
                total += flag["score"]
                findings.append({"check": "Clause", "result": flag["clause"], "score": flag["score"]})

        level = "HIGH" if total >= 50 else "MEDIUM" if total >= 25 else "LOW"

        return {
            "total_score": total,
            "risk_level": level,
            "findings": findings,
        }
