"""Income forecasting using ARIMA / simple moving average.

Predicts next 3 months of income based on historical payment data.
Falls back to moving average if insufficient data for ARIMA.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.data.database import Database


class IncomeForecaster:
    """Forecasts future income from historical payment patterns."""

    def __init__(self, db: Database):
        self.db = db

    def _get_monthly_income(self) -> pd.DataFrame:
        """Get monthly income totals from paid invoices."""
        rows = self.db.execute("""
            SELECT i.total, i.date_issued
            FROM invoices i
            WHERE i.status = 'Paid'
            ORDER BY i.date_issued
        """)
        if not rows:
            return pd.DataFrame(columns=["month", "income"])

        data = [{"date": row["date_issued"], "income": row["total"]} for row in rows]
        df = pd.DataFrame(data)
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.to_period("M")

        monthly = df.groupby("month")["income"].sum().reset_index()
        monthly["month"] = monthly["month"].dt.to_timestamp()
        return monthly

    def forecast(self, months_ahead: int = 3) -> dict[str, Any]:
        """
        Forecast income for the next N months.
        Uses ARIMA if enough data (12+ months), else simple moving average.
        """
        monthly = self._get_monthly_income()

        if len(monthly) < 3:
            return {
                "method": "insufficient_data",
                "forecast": [],
                "message": "Need at least 3 months of payment history.",
            }

        # Try ARIMA for 12+ data points
        if len(monthly) >= 12:
            return self._arima_forecast(monthly, months_ahead)

        # Fallback: weighted moving average
        return self._moving_average_forecast(monthly, months_ahead)

    def _arima_forecast(self, monthly: pd.DataFrame, months_ahead: int) -> dict[str, Any]:
        """ARIMA-based forecast."""
        try:
            from statsmodels.tsa.arima.model import ARIMA

            series = monthly.set_index("month")["income"]
            model = ARIMA(series, order=(1, 1, 1))
            fitted = model.fit()
            pred = fitted.forecast(steps=months_ahead)

            forecast_months = pd.date_range(
                start=monthly["month"].iloc[-1] + pd.DateOffset(months=1),
                periods=months_ahead,
                freq="MS",
            )

            return {
                "method": "arima",
                "forecast": [
                    {"month": m.strftime("%Y-%m"), "predicted_income": round(float(v), 2)}
                    for m, v in zip(forecast_months, pred)
                ],
                "historical": [
                    {"month": row["month"].strftime("%Y-%m"), "income": round(float(row["income"]), 2)}
                    for _, row in monthly.iterrows()
                ],
            }
        except Exception:
            return self._moving_average_forecast(monthly, months_ahead)

    def _moving_average_forecast(self, monthly: pd.DataFrame, months_ahead: int) -> dict[str, Any]:
        """Simple weighted moving average fallback."""
        recent = monthly["income"].tail(6).values
        weights = np.arange(1, len(recent) + 1, dtype=float)
        weights /= weights.sum()
        avg = float(np.dot(recent, weights))

        forecast_months = pd.date_range(
            start=monthly["month"].iloc[-1] + pd.DateOffset(months=1),
            periods=months_ahead,
            freq="MS",
        )

        return {
            "method": "moving_average",
            "forecast": [
                {"month": m.strftime("%Y-%m"), "predicted_income": round(avg, 2)}
                for m in forecast_months
            ],
            "historical": [
                {"month": row["month"].strftime("%Y-%m"), "income": round(float(row["income"]), 2)}
                for _, row in monthly.iterrows()
            ],
        }
