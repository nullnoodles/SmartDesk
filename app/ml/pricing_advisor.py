"""Smart pricing advisor — hybrid rule-based + data-driven pricing suggestions.

Combines market benchmarks, project complexity scoring, and user's historical data
to suggest a price RANGE with reasoning.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from app.config import MARKET_RATES
from app.data.database import Database


class PricingAdvisor:
    """Suggests project pricing based on market rates, complexity, and history."""

    # Keywords that indicate higher complexity / urgency
    COMPLEXITY_KEYWORDS = {
        "urgent": 1.3,
        "rush": 1.4,
        "complex": 1.2,
        "enterprise": 1.3,
        "rebrand": 1.2,
        "animation": 1.3,
        "3d": 1.4,
        "custom": 1.15,
        "revision": 0.9,
        "simple": 0.8,
        "template": 0.7,
        "basic": 0.75,
    }

    def __init__(self, db: Database):
        self.db = db

    def suggest_price(
        self,
        project_type: str,
        estimated_hours: float,
        description: str = "",
        revision_rounds: int = 2,
    ) -> dict[str, Any]:
        """
        Suggest a price range for a new project.

        Returns: low, mid, high estimates with reasoning.
        """
        base_rate = MARKET_RATES.get(project_type, MARKET_RATES["General"])

        # 1. Complexity multiplier from description keywords
        complexity_mult = self._complexity_score(description)

        # 2. Revision adjustment
        revision_mult = 1.0 + max(0, (revision_rounds - 2)) * 0.08

        # 3. Historical rate from user's own data
        historical_rate = self._get_historical_rate(project_type)

        # Blend: 60% market, 40% historical (if available)
        if historical_rate:
            effective_rate = (base_rate * 0.6) + (historical_rate * 0.4)
        else:
            effective_rate = base_rate

        # Calculate range
        adjusted_rate = effective_rate * complexity_mult * revision_mult
        base_price = adjusted_rate * estimated_hours

        low = round(base_price * 0.85, -2)   # round to nearest 100
        mid = round(base_price, -2)
        high = round(base_price * 1.2, -2)

        reasoning = []
        reasoning.append(f"Market rate for {project_type}: ₹{base_rate}/hr")
        if historical_rate:
            reasoning.append(f"Your historical rate: ₹{historical_rate:.0f}/hr")
        if complexity_mult != 1.0:
            reasoning.append(f"Complexity adjustment: {complexity_mult:.2f}x")
        if revision_rounds > 2:
            reasoning.append(f"Extra revisions (+{revision_rounds - 2}): {revision_mult:.2f}x")

        return {
            "low": max(low, 500),
            "mid": max(mid, 1000),
            "high": max(high, 1500),
            "effective_hourly_rate": round(adjusted_rate, 2),
            "estimated_hours": estimated_hours,
            "reasoning": reasoning,
        }

    def _complexity_score(self, description: str) -> float:
        """Score project complexity from description keywords."""
        if not description:
            return 1.0
        desc_lower = description.lower()
        multipliers = [
            mult for keyword, mult in self.COMPLEXITY_KEYWORDS.items()
            if keyword in desc_lower
        ]
        if not multipliers:
            return 1.0
        return float(np.mean(multipliers))

    def _get_historical_rate(self, project_type: str) -> float | None:
        """Get user's average effective hourly rate for this project type."""
        rows = self.db.execute("""
            SELECT i.total, t.total_hours
            FROM invoices i
            JOIN projects p ON i.project_id = p.id
            LEFT JOIN (
                SELECT project_id, SUM(duration_hours) as total_hours
                FROM time_logs GROUP BY project_id
            ) t ON p.id = t.project_id
            WHERE i.status = 'Paid' AND p.type = ? AND t.total_hours > 0
        """, (project_type,))

        if not rows or len(rows) < 2:
            return None

        rates = [row["total"] / row["total_hours"] for row in rows if row["total_hours"] > 0]
        return float(np.mean(rates)) if rates else None
