"""Matplotlib chart widgets — embed in Qt with the project's dark theme.

Provides:
- IncomeTrendChart: monthly income line chart over the last 6 months
- ProjectTypeChart: horizontal bar chart of revenue per project type
"""
from __future__ import annotations

from datetime import date

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from app.data.database import Database
from app.ui.styles.theme import Colors


def _apply_dark_axes(ax) -> None:
    """Tune Matplotlib axes to match the Studio Graphite dark theme."""
    ax.set_facecolor(Colors.BG_CARD)
    ax.tick_params(colors=Colors.TEXT_SECONDARY, labelsize=10)
    for spine_name in ("top", "right"):
        ax.spines[spine_name].set_visible(False)
    for spine_name in ("bottom", "left"):
        ax.spines[spine_name].set_color(Colors.BORDER_SUBTLE)
    ax.title.set_color(Colors.TEXT_PRIMARY)
    ax.xaxis.label.set_color(Colors.TEXT_MUTED)
    ax.yaxis.label.set_color(Colors.TEXT_MUTED)
    ax.grid(True, axis="y", color=Colors.BORDER_SUBTLE, linewidth=0.5, alpha=0.4)


def _rupee_formatter(value, _pos):
    if abs(value) >= 1_00_000:
        return f"₹{value/1_00_000:.1f}L"
    if abs(value) >= 1_000:
        return f"₹{value/1_000:.0f}k"
    return f"₹{value:.0f}"


class _BaseChart(FigureCanvas):
    def __init__(self, parent=None, width: float = 6.0, height: float = 3.2):
        fig = Figure(figsize=(width, height), facecolor=Colors.BG_CARD)
        super().__init__(fig)
        self.setParent(parent)
        self.figure = fig
        self.ax = fig.add_subplot(111)
        _apply_dark_axes(self.ax)


class IncomeTrendChart(_BaseChart):
    """Monthly paid-invoice income for the last N months as a line chart."""

    def __init__(self, db: Database, parent=None, months: int = 6):
        super().__init__(parent, height=2.6)
        self.db = db
        self.months = months
        self.refresh()

    def refresh(self) -> None:
        try:
            rows = self.db.execute(
                """
                SELECT strftime('%Y-%m', date_issued) as month, SUM(total) as income
                FROM invoices
                WHERE status = 'Paid'
                GROUP BY month
                ORDER BY month
                """
            )
        except Exception:
            rows = []

        # Build last-N-month buckets (filling zeros)
        buckets = self._last_n_months(self.months)
        data = {row["month"]: float(row["income"]) for row in rows}
        values = [data.get(m, 0.0) for m in buckets]

        self.ax.clear()
        _apply_dark_axes(self.ax)
        self.ax.set_title("Income Trend", loc="left", fontsize=11, pad=10, fontweight="bold")

        if not any(values):
            self.ax.text(
                0.5, 0.5,
                "No paid invoices yet",
                ha="center", va="center",
                color=Colors.TEXT_MUTED, fontsize=11,
                transform=self.ax.transAxes,
            )
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        else:
            x = list(range(len(buckets)))
            self.ax.fill_between(
                x, values, 0,
                color=Colors.ACCENT_PRIMARY, alpha=0.15,
            )
            self.ax.plot(
                x, values,
                color=Colors.ACCENT_PRIMARY, linewidth=2.5,
                marker="o", markersize=5,
                markerfacecolor=Colors.ACCENT_PRIMARY_LIGHT,
                markeredgecolor=Colors.ACCENT_PRIMARY,
            )
            self.ax.set_xticks(x)
            self.ax.set_xticklabels([m[5:] for m in buckets])  # MM only
            self.ax.yaxis.set_major_formatter(FuncFormatter(_rupee_formatter))
            self.ax.set_ylim(bottom=0)

        self.figure.tight_layout()
        self.draw_idle()

    @staticmethod
    def _last_n_months(n: int) -> list[str]:
        today = date.today()
        months = []
        year, month = today.year, today.month
        for _ in range(n):
            months.append(f"{year:04d}-{month:02d}")
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        return list(reversed(months))


class ProjectTypeChart(_BaseChart):
    """Horizontal bar chart of total revenue grouped by project type."""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent, height=2.6)
        self.db = db
        self.refresh()

    def refresh(self) -> None:
        try:
            rows = self.db.execute(
                """
                SELECT p.type as type, SUM(i.total) as revenue
                FROM invoices i
                JOIN projects p ON i.project_id = p.id
                WHERE i.status = 'Paid'
                GROUP BY p.type
                ORDER BY revenue DESC
                """
            )
        except Exception:
            rows = []

        types = [row["type"] or "General" for row in rows]
        values = [float(row["revenue"] or 0) for row in rows]

        self.ax.clear()
        _apply_dark_axes(self.ax)
        self.ax.set_title("Revenue by Project Type", loc="left", fontsize=11, pad=10, fontweight="bold")
        self.ax.grid(False, axis="y")
        self.ax.grid(True, axis="x", color=Colors.BORDER_SUBTLE, linewidth=0.5, alpha=0.4)

        if not values:
            self.ax.text(
                0.5, 0.5, "No revenue yet — close some paid invoices",
                ha="center", va="center",
                color=Colors.TEXT_MUTED, fontsize=11,
                transform=self.ax.transAxes,
            )
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        else:
            palette = [
                Colors.CHART_1, Colors.CHART_2, Colors.CHART_3, Colors.CHART_4,
                Colors.CHART_5, Colors.CHART_6, Colors.CHART_7,
            ]
            colors = [palette[i % len(palette)] for i in range(len(types))]
            y = list(range(len(types)))
            self.ax.barh(y, values, color=colors, edgecolor="none", height=0.55)
            self.ax.set_yticks(y)
            self.ax.set_yticklabels(types, color=Colors.TEXT_SECONDARY)
            self.ax.invert_yaxis()
            self.ax.xaxis.set_major_formatter(FuncFormatter(_rupee_formatter))

        self.figure.tight_layout()
        self.draw_idle()
