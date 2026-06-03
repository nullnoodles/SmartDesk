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
    def __init__(self, parent=None, width: float = 8.0, height: float = 4.5):  # Fix: Larger default size
        fig = Figure(figsize=(width, height), facecolor=Colors.BG_CARD, dpi=100)  # Fix: Added DPI
        super().__init__(fig)
        self.setParent(parent)
        self.figure = fig
        self.ax = fig.add_subplot(111)
        _apply_dark_axes(self.ax)
        self.setMinimumSize(400, 280)  # Fix: Set minimum widget size


class IncomeTrendChart(_BaseChart):
    """Monthly paid-invoice income for the last N months as a line chart."""

    def __init__(self, db: Database, parent=None, months: int = 6):
        super().__init__(parent, width=8.5, height=4.8)  # Fix: Larger chart
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
        # Fix: Remove duplicate title since card now has title
        # self.ax.set_title("Income Trend", loc="left", fontsize=11, pad=10, fontweight="bold")

        if not any(values):
            self.ax.text(
                0.5, 0.5,
                "No paid invoices yet\n\nCreate and mark invoices as paid to see income trends",
                ha="center", va="center",
                color=Colors.TEXT_MUTED, fontsize=12,
                transform=self.ax.transAxes,
                multialignment="center",
            )
            self.ax.set_xticks([])
            self.ax.set_yticks([])
        else:
            x = list(range(len(buckets)))
            # Fix: Larger area fill
            self.ax.fill_between(
                x, values, 0,
                color=Colors.ACCENT_PRIMARY, alpha=0.2,
            )
            # Fix: Thicker line, larger markers
            self.ax.plot(
                x, values,
                color=Colors.ACCENT_PRIMARY, linewidth=3.5,
                marker="o", markersize=8,
                markerfacecolor=Colors.ACCENT_PRIMARY_LIGHT,
                markeredgecolor=Colors.ACCENT_PRIMARY,
                markeredgewidth=2,
            )
            self.ax.set_xticks(x)
            # Fix: Better month labels (show full month-year for better context)
            month_labels = []
            for m in buckets:
                year, month = m.split('-')
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                month_labels.append(f"{month_names[int(month)-1]}\n'{year[2:]}")
            self.ax.set_xticklabels(month_labels, fontsize=10)
            self.ax.yaxis.set_major_formatter(FuncFormatter(_rupee_formatter))
            self.ax.tick_params(axis='y', labelsize=11)  # Fix: Larger tick labels
            self.ax.set_ylim(bottom=0)
            # Fix: Add axis labels for context
            self.ax.set_xlabel("Month", fontsize=11, color=Colors.TEXT_SECONDARY, labelpad=10)
            self.ax.set_ylabel("Revenue", fontsize=11, color=Colors.TEXT_SECONDARY, labelpad=10)

        self.figure.tight_layout(pad=1.5)  # Fix: More padding
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
        super().__init__(parent, width=7.5, height=4.8)  # Fix: Larger chart
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
        # Fix: Remove duplicate title since card now has title
        # self.ax.set_title("Revenue by Project Type", loc="left", fontsize=11, pad=10, fontweight="bold")
        self.ax.grid(False, axis="y")
        self.ax.grid(True, axis="x", color=Colors.BORDER_SUBTLE, linewidth=0.6, alpha=0.5)  # Fix: Thicker grid

        if not values:
            self.ax.text(
                0.5, 0.5, 
                "No revenue data yet\n\nCreate projects and mark invoices as paid\nto see revenue breakdown by type",
                ha="center", va="center",
                color=Colors.TEXT_MUTED, fontsize=12,
                transform=self.ax.transAxes,
                multialignment="center",
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
            # Fix: Taller bars with better spacing
            self.ax.barh(y, values, color=colors, edgecolor="none", height=0.7)
            self.ax.set_yticks(y)
            # Fix: Larger, bolder labels
            self.ax.set_yticklabels(types, color=Colors.TEXT_PRIMARY, fontsize=11, fontweight=600)
            self.ax.invert_yaxis()
            self.ax.xaxis.set_major_formatter(FuncFormatter(_rupee_formatter))
            self.ax.tick_params(axis='x', labelsize=11)  # Fix: Larger tick labels
            # Fix: Add axis labels for context
            self.ax.set_xlabel("Total Revenue", fontsize=11, color=Colors.TEXT_SECONDARY, labelpad=10)
            
            # Fix: Add value labels on bars for better readability
            for i, (bar_y, value) in enumerate(zip(y, values)):
                if value > 0:
                    self.ax.text(
                        value + max(values) * 0.02, bar_y, 
                        _rupee_formatter(value, None),
                        va='center', ha='left',
                        color=Colors.TEXT_SECONDARY, fontsize=10, fontweight=600
                    )

        self.figure.tight_layout(pad=1.5)  # Fix: More padding
        self.draw_idle()
