from __future__ import annotations

import math
from pathlib import Path
import sys
import ctypes

def is_reduced_motion() -> bool:
    """Check if the user has requested reduced motion at the OS level (Windows)."""
    if sys.platform != "win32":
        return False
    try:
        enabled = ctypes.c_bool()
        # SPI_GETCLIENTAREAANIMATION = 0x1042
        if ctypes.windll.user32.SystemParametersInfoW(0x1042, 0, ctypes.byref(enabled), 0):
            return not enabled.value
    except Exception:
        pass
    return False


# Add project root to sys.path if run directly to support executing the file directly
_project_root = Path(__file__).resolve().parents[3]
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QEvent, Property
from datetime import date, timedelta
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap, QBrush, QFont, QFontDatabase, QLinearGradient, QPainterPath
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)



from app.config import ASSETS_DIR
from app.data.database import Database
from app.data.repositories.client_repo import ClientRepository
from app.data.repositories.invoice_repo import InvoiceRepository
from app.data.repositories.project_repo import ProjectRepository
from app.ui.styles.theme import Colors
from app.ui.widgets.stat_card import StatCard


_ICONS_DIR = ASSETS_DIR / "icons"


def _load_svg_icon(name: str, size: int = 16, color: str = "#bcc2ff") -> QPixmap:
    """Load an SVG, render at size, tint with color."""
    svg_path = _ICONS_DIR / f"{name}.svg"
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    if not svg_path.exists():
        return pixmap
    renderer = QSvgRenderer(str(svg_path))
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()
    return pixmap


def _format_short_currency(val: float) -> str:
    """Format large numbers in short format — ₹1,20,339 should show as ₹1.2L, ₹1,14,896 as ₹1.1L."""
    if not val:
        return "₹0"
    if val >= 100000:
        return f"₹{val/100000:.1f}L"
    elif val >= 1000:
        return f"₹{val/1000:.1f}K"
    else:
        return f"₹{val:,.0f}"


class DashboardStatCard(QFrame):
    def __init__(
        self,
        label: str,
        value: str = "—",
        icon: str = "",
        accent: str = Colors.ACCENT_PRIMARY,
        sub_text: str = "",
        sub_color: str | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setMinimumHeight(140)
        self.setMaximumHeight(140)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setStyleSheet("background-color: #222336; border-radius: 12px;")
        
        # Enable mouse tracking for hover effects
        self.setAttribute(Qt.WA_Hover, True)
        self.setMouseTracking(True)

        # Setup shadow effect for hover animation
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(0)
        self._shadow.setColor(QColor(124, 138, 244, 180))  # Purple glow with transparency
        self._shadow.setOffset(0, 0)
        self.setGraphicsEffect(self._shadow)
        
        # Create animation for blur radius
        self._shadow_animation = QPropertyAnimation(self._shadow, b"blurRadius")
        self._shadow_animation.setDuration(200 if not is_reduced_motion() else 0)  # 200ms animation
        self._shadow_animation.setEasingCurve(QEasingCurve.OutCubic)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(6)

        row1 = QHBoxLayout()
        row1.setSpacing(8)
        row1.setContentsMargins(0, 0, 0, 0)

        # Icon bubble - 24x24px
        self._icon_bubble = QLabel()
        self._icon_bubble.setObjectName("stat_card_icon_bubble")
        self._icon_bubble.setFixedSize(24, 24)
        self._icon_bubble.setAlignment(Qt.AlignCenter)
        
        # Determine background tint
        rgba_color = "rgba(124, 138, 244, 0.10)"
        if accent == Colors.ACCENT_PRIMARY_LIGHT:
            rgba_color = "rgba(188, 194, 255, 0.10)"
        elif accent == Colors.ACCENT_INFO:
            rgba_color = "rgba(125, 211, 227, 0.10)"
        elif accent == Colors.ACCENT_WARNING:
            rgba_color = "rgba(240, 200, 120, 0.10)"
        elif accent == Colors.ACCENT_SUCCESS:
            rgba_color = "rgba(130, 216, 172, 0.10)"
        self._icon_bubble.setStyleSheet(f"background-color: {rgba_color}; border-radius: 4px;")
        
        if icon and (_ICONS_DIR / f"{icon}.svg").exists():
            icon_pixmap = _load_svg_icon(icon, size=16, color=accent)
            self._icon_bubble.setPixmap(icon_pixmap)
        else:
            self._icon_bubble.setText(icon[:1] if icon else "")
        row1.addWidget(self._icon_bubble)

        # Label text
        label_title = QLabel(label.upper())
        label_title.setObjectName("stat_card_label")
        label_title.setFont(QFont("Inter", 11))
        label_title.setStyleSheet("color: #8B8FA8; background: transparent; border: none;")
        row1.addWidget(label_title, 1)
        self._label = label_title

        layout.addLayout(row1)

        # Row 2: large value text
        label_value = QLabel(value)
        label_value.setObjectName("stat_card_value")
        label_value.setFont(QFont("Inter", 24, QFont.Bold))
        label_value.setStyleSheet("color: #FFFFFF; background: transparent; border: none;")
        layout.addWidget(label_value)
        self._value = label_value

        # Row 3: subtitle text
        label_subtitle = QLabel(sub_text)
        label_subtitle.setObjectName("stat_card_subtext")
        label_subtitle.setMaximumHeight(16)
        label_subtitle.setFont(QFont("Inter", 8))
        label_subtitle.setStyleSheet("color: #6B7280; background: transparent; border: none;")
        if sub_color:
            label_subtitle.setStyleSheet(f"color: {sub_color}; background: transparent; border: none;")
        label_subtitle.setVisible(bool(sub_text))
        layout.addWidget(label_subtitle)
        self._sub = label_subtitle

    def enterEvent(self, event):
        """Mouse enter - animate shadow in and lighten background."""
        super().enterEvent(event)
        # Animate shadow blur from 0 to 20
        self._shadow_animation.setStartValue(self._shadow.blurRadius())
        self._shadow_animation.setEndValue(20 if not is_reduced_motion() else 0)
        self._shadow_animation.start()
        # Lighten background slightly
        self.setStyleSheet("background-color: #2a2c3e; border-radius: 12px;")
    
    def leaveEvent(self, event):
        """Mouse leave - animate shadow out and restore background."""
        super().leaveEvent(event)
        # Animate shadow blur from current to 0
        self._shadow_animation.setStartValue(self._shadow.blurRadius())
        self._shadow_animation.setEndValue(0)
        self._shadow_animation.start()
        # Restore original background
        self.setStyleSheet("background-color: #222336; border-radius: 12px;")

    def set_value(self, value: str) -> None:
        self._value.setText(value)

    def set_sub_text(self, text: str, color: str | None = None) -> None:
        self._sub.setText(text)
        self._sub.setVisible(bool(text))
        label_subtitle = self._sub
        label_subtitle.setFont(QFont("Inter", 10))
        label_subtitle.setStyleSheet("color: #6B7280; background: transparent; border: none;")
        if color:
            label_subtitle.setStyleSheet(f"color: {color}; background: transparent; border: none;")
        else:
            label_subtitle.setStyleSheet("background: transparent; border: none;")




# ─────────────────────────────────────────────────────────────────────────────
# Revenue line chart — custom QPainter widget
# ─────────────────────────────────────────────────────────────────────────────

class RevenueLineChart(QWidget):
    """Simple line chart matching the Stitch SVG revenue chart with smooth animation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Stitch data points (normalized 0-1, inverted for screen coords)
        self._data = [0.20, 0.47, 0.60, 0.53, 0.73, 0.87]
        self._months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
        self._raw_data = [0.0] * 6  # Store actual revenue values for Y-axis labels
        
        # Animation progress (0.0 to 1.0)
        self._animation_progress = 0.0
        
        # Create animation
        self._animation = QPropertyAnimation(self, b"animationProgress")
        self._animation.setDuration(300 if not is_reduced_motion() else 0)  # Snappy 300ms animation
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.setStartValue(0.0)
        self._animation.setEndValue(1.0)


        # Cached drawing resources to avoid dynamic allocations during paint events
        self._grid_pen = QPen(QColor("#333440"), 1, Qt.DotLine)
        self._line_pen = QPen(QColor("#bcc2ff"), 3, Qt.SolidLine, Qt.RoundCap)
        self._point_pen = QPen(QColor("#bcc2ff"), 2)
        self._point_brush = QBrush(QColor("#12131d"))
        
        self._label_font = QFont("Inter", 9)
        self._label_font.setWeight(QFont.Bold)
        
        self._y_axis_font = QFont("Inter", 8)
    
    def get_animation_progress(self):
        return self._animation_progress
    
    def set_animation_progress(self, value):
        self._animation_progress = value
        self.update()
    
    # Qt property for animation
    animationProgress = Property(float, get_animation_progress, set_animation_progress)

    def set_chart_data(self, data: list[float], months: list[str]) -> None:
        self._raw_data = data.copy() if data else [0.0]  # Store raw values for Y-axis
        max_val = max(data) if data else 0
        if max_val > 0:
            self._data = [float(val) / max_val for val in data]
        else:
            self._data = [0.0] * len(data)
        self._months = months
        
        # Start animation from beginning
        self._animation.stop()
        self._animation_progress = 0.0
        self._animation.start()
    
    def _format_currency(self, val: float) -> str:
        """Format currency for Y-axis labels - clean rounded values only."""
        if val >= 100000:
            return f"₹{val/100000:.0f}L"
        elif val >= 1000:
            return f"₹{val/1000:.0f}K"
        elif val == 0:
            return "₹0"
        else:
            return f"₹{int(val)}"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        margin_top = 20     # Added top margin for better vertical padding
        margin_bottom = 45  # Increased bottom margin to prevent overlapping labels
        margin_left = 60    # Increased from 36 to 60 to make room for Y-axis labels
        margin_right = 36   # Increased from 24 to 36 for better horizontal padding
        chart_h = h - (margin_top + margin_bottom)  # Account for both top and bottom margins
        chart_w = w - (margin_left + margin_right)

        if len(self._data) < 1:
            painter.end()
            return
        
        # Calculate max value for Y-axis with 30% padding, or default scale if no data
        max_raw_value = max(self._raw_data) if self._raw_data else 0.0
        if max_raw_value == 0:
            max_raw_value = 100000  # default scale ₹0 to ₹1L when no data
        else:
            max_raw_value = max_raw_value * 1.3  # 30% padding above highest point
            
        # Special handling for single data point - show as a point with base line
        if len(self._data) == 1:
            # Draw Y-axis labels
            painter.setFont(self._y_axis_font)
            painter.setPen(QColor("#6b6d85"))
            for i in range(4):
                y = margin_top + int(chart_h * i / 3)
                value = max_raw_value * (1.0 - i / 3.0)
                label = self._format_currency(value)
                painter.drawText(5, y + 4, label)
            
            # Draw a single point at the center (with animation)
            x = margin_left + chart_w // 2
            y = margin_top + int(chart_h * (1.0 - self._data[0]))
            
            # Animate point appearance
            if self._animation_progress > 0.8:
                scale = min(1.0, (self._animation_progress - 0.8) / 0.2)
                size = int(6 * scale)
                painter.setPen(self._point_pen)
                painter.setBrush(self._point_brush)
                painter.drawEllipse(x - size, y - size, size * 2, size * 2)
            
            # Draw month label
            painter.setFont(self._label_font)
            painter.setPen(QColor("#6b6d85"))
            painter.drawText(x - 12, h - 20, self._months[0].upper())  # Adjusted for bottom margin
            
            painter.end()
            return

        # Draw Y-axis labels (4 levels: 0%, 33%, 66%, 100%)
        painter.setFont(self._y_axis_font)
        painter.setPen(QColor("#6b6d85"))
        for i in range(4):
            y = margin_top + int(chart_h * i / 3)
            value = max_raw_value * (1.0 - i / 3.0)
            label = self._format_currency(value)
            painter.drawText(5, y + 4, label)

        # Draw subtle horizontal grid lines
        painter.setPen(self._grid_pen)
        for i in range(4):
            y = margin_top + int(chart_h * i / 3)  # Adjusted for top margin
            painter.drawLine(margin_left, y, w - margin_right, y)

        # Calculate points
        n = len(self._data)
        points = []
        for i, val in enumerate(self._data):
            x = margin_left + int(chart_w * i / (n - 1))
            y = margin_top + int(chart_h * (1.0 - val))  # Adjusted for top margin
            points.append((x, y))

        # Calculate how many segments to draw based on animation progress
        total_segments = len(points) - 1
        animated_segments = self._animation_progress * total_segments
        full_segments = int(animated_segments)
        partial_segment = animated_segments - full_segments

        # Draw filled area under line (with animation)
        if full_segments > 0 or partial_segment > 0:
            area_path = QPainterPath()
            area_path.moveTo(points[0][0], points[0][1])
            
            # Draw full segments
            for i in range(min(full_segments + 1, len(points))):
                if i < len(points):
                    area_path.lineTo(points[i][0], points[i][1])
            
            # Draw partial segment
            if full_segments < len(points) - 1 and partial_segment > 0:
                p1 = points[full_segments]
                p2 = points[full_segments + 1]
                partial_x = p1[0] + (p2[0] - p1[0]) * partial_segment
                partial_y = p1[1] + (p2[1] - p1[1]) * partial_segment
                area_path.lineTo(partial_x, partial_y)
                last_x, last_y = partial_x, partial_y
            else:
                last_x, last_y = points[min(full_segments, len(points) - 1)]
            
            # Close the path
            area_path.lineTo(last_x, margin_top + chart_h)
            area_path.lineTo(points[0][0], margin_top + chart_h)
            area_path.closeSubpath()

            gradient = QLinearGradient(margin_left, margin_top, margin_left, margin_top + chart_h)
            gradient.setColorAt(0, QColor(188, 194, 255, 25))
            gradient.setColorAt(1, QColor(18, 19, 29, 0))
            painter.fillPath(area_path, gradient)

        # Draw line segments (with animation)
        painter.setPen(self._line_pen)
        
        # Draw full segments
        for i in range(full_segments):
            painter.drawLine(points[i][0], points[i][1],
                           points[i + 1][0], points[i + 1][1])
        
        # Draw partial segment
        if full_segments < len(points) - 1 and partial_segment > 0:
            p1 = points[full_segments]
            p2 = points[full_segments + 1]
            partial_x = p1[0] + (p2[0] - p1[0]) * partial_segment
            partial_y = p1[1] + (p2[1] - p1[1]) * partial_segment
            painter.drawLine(p1[0], p1[1], int(partial_x), int(partial_y))

        # Draw data points (appear progressively)
        for idx, (px, py) in enumerate(points):
            # Calculate when this point should appear (staggered)
            point_progress = (idx / max(1, len(points) - 1)) * 0.8  # Spread across 80% of animation
            if self._animation_progress >= point_progress:
                # Scale point size based on how recently it appeared
                appearance_progress = min(1.0, (self._animation_progress - point_progress) / 0.2)
                scale = appearance_progress  # Smooth scale from 0 to 1
                size = int(4 * scale)
                
                if size > 0:
                    painter.setPen(self._point_pen)
                    painter.setBrush(self._point_brush)
                    painter.drawEllipse(px - size, py - size, size * 2, size * 2)

        # Draw month labels cleanly within the bottom margin area
        painter.setFont(self._label_font)
        painter.setPen(QColor("#6b6d85"))
        for i, month in enumerate(self._months):
            x = margin_left + int(chart_w * i / (n - 1))
            painter.drawText(x - 12, margin_top + chart_h + 24, month.upper())  # Adjusted for top margin

        painter.end()


# ─────────────────────────────────────────────────────────────────────────────
# Donut chart — Invoice Status (Native QPainter implementation)
# ─────────────────────────────────────────────────────────────────────────────

class DonutChart(QWidget):
    """Donut chart matching the Stitch Invoice Status design using QPainter with rotation animation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setParent(parent)
        self.setStyleSheet("background: transparent;")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(192, 192)
        
        # Animation properties
        self._rotation_angle = 0.0
        
        # Create rotation animation
        self._rotation_animation = QPropertyAnimation(self, b"rotationAngle")
        self._rotation_animation.setDuration(400 if not is_reduced_motion() else 0)  # Snappy 400ms spin
        self._rotation_animation.setEasingCurve(QEasingCurve.InOutCubic)

        
        # Initial segments: Paid (green), Unpaid (yellow), Overdue (red)
        # Matches reference proportions: Paid (45%), Unpaid (25%), Overdue (30%)
        self._paid = 45
        self._unpaid = 25
        self._overdue = 30
    
    def get_rotation_angle(self):
        return self._rotation_angle
    
    def set_rotation_angle(self, value):
        self._rotation_angle = value
        self.update()
    
    # Qt property for animation
    rotationAngle = Property(float, get_rotation_angle, set_rotation_angle)

    def set_data(self, paid: int, unpaid: int, overdue: int) -> None:
        self._paid = paid
        self._unpaid = unpaid
        self._overdue = overdue
        
        # Animate rotation: add 360 degrees for smooth spin
        self._target_rotation = self._rotation_angle + 360
        self._rotation_animation.stop()
        self._rotation_animation.setStartValue(self._rotation_angle)
        self._rotation_animation.setEndValue(self._target_rotation)
        self._rotation_animation.start()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect()
        margin = 12
        chart_rect = rect.adjusted(margin, margin, -margin, -margin)
        
        sizes = [self._paid, self._unpaid, self._overdue]
        colors = [QColor('#82d8ac'), QColor('#f0c878'), QColor('#e87c8a')]
        
        total = sum(sizes)
        if total <= 0:
            sizes = [1]
            colors = [QColor('#6b6d85')]
            total = 1
            
        pen_width = 24
        half_pen = pen_width / 2
        arc_rect = chart_rect.adjusted(half_pen, half_pen, -half_pen, -half_pen)
        
        start_angle = int((90 + self._rotation_angle) * 16)
        
        current_angle = start_angle
        for size, color in zip(sizes, colors):
            if size <= 0:
                continue
            span_angle = -int((size / total) * 360 * 16)
            
            pen = QPen(color, pen_width, Qt.SolidLine, Qt.FlatCap)
            painter.setPen(pen)
            painter.drawArc(arc_rect, current_angle, span_angle)
            
            current_angle += span_angle


# ─────────────────────────────────────────────────────────────────────────────
# Custom QTableWidget — Dynamic percentages and 48px rows
# ─────────────────────────────────────────────────────────────────────────────

class CustomTableWidget(QTableWidget):
    """QTableWidget subclass that dynamically calculates column widths by percentage on resize."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.NoFrame)
        self.setShowGrid(False)
        # Set default row height to match reference (48px)
        self.verticalHeader().setDefaultSectionSize(48)
        
        # Remove blue selection borders and enable subtle row highlighting
        self.setFocusPolicy(Qt.NoFocus)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # Apply scoped stylesheet for hover and selection effects
        self.setStyleSheet("""
            QTableWidget::item {
                border: none;
                padding: 8px 12px;
            }
            QTableWidget::item:selected {
                background-color: rgba(124, 138, 244, 0.12);
                border: none;
                color: white;
            }
            QTableWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.04);
                border: none;
            }
            QHeaderView::section {
                padding-left: 12px;
                padding-right: 12px;
            }
        """)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        width = self.viewport().width()
        # PROJECT: 24%, CLIENT: 18%, TYPE: 12%, STATUS: 16%, DEADLINE: 14%, BUDGET: remaining width
        self.setColumnWidth(0, int(width * 0.24))
        self.setColumnWidth(1, int(width * 0.18))
        self.setColumnWidth(2, int(width * 0.12))
        self.setColumnWidth(3, int(width * 0.16))
        self.setColumnWidth(4, int(width * 0.14))
        self.setColumnWidth(5, width - (self.columnWidth(0) + self.columnWidth(1) + self.columnWidth(2) + self.columnWidth(3) + self.columnWidth(4)))




# ─────────────────────────────────────────────────────────────────────────────
# Dashboard Page
# ─────────────────────────────────────────────────────────────────────────────

class DashboardPage(QWidget):
    """Main dashboard — Stitch 'Dashboard (Visual Analytics)' layout."""

    def __init__(self, db: Database):
        super().__init__()
        self.setObjectName("dashboard_page")
        self.db = db
        self.invoice_repo = InvoiceRepository(db)
        self.project_repo = ProjectRepository(db)
        self.client_repo = ClientRepository(db)
        
        # Initialize table filter state
        self._active_filter = "All"
        self._all_projects = []

        # Main page layout
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Content widget inside scroll
        content_widget = QWidget()
        content_widget.setObjectName("dashboard_content")
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(32, 32, 32, 32)  # Stitch: p-8 = 32px
        layout.setSpacing(24)  # Stitch: space-y-6 = 24px
        layout.setAlignment(Qt.AlignTop)

        # ═══════════════════════════════════════════════════════════════════
        # STAT CARDS ROW — 4 cards in QHBoxLayout
        # ═══════════════════════════════════════════════════════════════════
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(0, 0, 0, 0)

        self.card_revenue = DashboardStatCard(
            "Total Revenue", "—",
            icon="account_balance_wallet",
            accent=Colors.ACCENT_PRIMARY_LIGHT,
            sub_text="Loading...",
            sub_color=Colors.ACCENT_SUCCESS,
        )
        self.card_revenue.setObjectName("statCard")

        self.card_projects = DashboardStatCard(
            "Active Projects", "—",
            icon="task_alt",
            accent=Colors.ACCENT_INFO,
            sub_text="Loading...",
        )
        self.card_projects.setObjectName("statCard")

        self.card_pending = DashboardStatCard(
            "Pending Invoices", "—",
            icon="pending_actions",
            accent=Colors.ACCENT_WARNING,
            sub_text="Loading...",
        )
        self.card_pending.setObjectName("statCard")

        self.card_hours = DashboardStatCard(
            "Hours Tracked", "—",
            icon="schedule",
            accent=Colors.ACCENT_SUCCESS,
            sub_text="Loading...",
        )
        self.card_hours.setObjectName("statCard")

        for card in (self.card_revenue, self.card_projects, self.card_pending, self.card_hours):
            stats_layout.addWidget(card, 1)
        layout.addLayout(stats_layout)


        # ═══════════════════════════════════════════════════════════════════
        # CHARTS ROW — Revenue Overview (2:1) + Project Status (1:1)
        # ═══════════════════════════════════════════════════════════════════
        charts_row = QHBoxLayout()
        charts_row.setSpacing(24)

        # ─── Revenue Overview Card ────────────────────────────────────────
        revenue_card = QFrame()
        revenue_card.setObjectName("dashboard_chart_card")
        revenue_card.setStyleSheet("QFrame#dashboard_chart_card { background-color: #222336; border-radius: 12px; border: 1px solid #2d2e42; }")
        revenue_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        revenue_card.setMinimumHeight(400)
        revenue_card.setMinimumWidth(400)

        rev_layout = QVBoxLayout(revenue_card)
        rev_layout.setContentsMargins(24, 24, 24, 24)
        rev_layout.setSpacing(12)

        # Title row: "Revenue Overview" + period dropdown
        rev_header = QHBoxLayout()
        rev_title = QLabel("Revenue Overview")
        rev_title.setObjectName("chart_card_title")
        rev_header.addWidget(rev_title)
        rev_header.addStretch()

        self.period_combo = QComboBox()
        self.period_combo.addItems(["This Year", "All Time", "Past 30 Days", "Past 7 Days"])
        self.period_combo.setCurrentIndex(0)  # Default: This Year
        
        # Enable hover tracking for shadow animation
        self.period_combo.setAttribute(Qt.WA_Hover, True)
        self.period_combo.setMouseTracking(True)
        
        # Setup shadow effect for hover animation
        period_combo_shadow = QGraphicsDropShadowEffect(self.period_combo)
        period_combo_shadow.setBlurRadius(20)  # Test with static blur to verify shadow is visible
        period_combo_shadow.setColor(QColor(124, 138, 244, 200))  # Purple glow with higher opacity
        period_combo_shadow.setOffset(0, 0)
        self.period_combo.setGraphicsEffect(period_combo_shadow)
        self._period_combo_shadow = period_combo_shadow
        
        # Create animation for blur radius
        self._period_combo_shadow_animation = QPropertyAnimation(period_combo_shadow, b"blurRadius")
        self._period_combo_shadow_animation.setDuration(200)  # 200ms animation
        self._period_combo_shadow_animation.setEasingCurve(QEasingCurve.OutCubic)
        
        self.period_combo.setStyleSheet("""
            QComboBox {
                background-color: #222336;
                color: #e0e2f0;
                border: 1px solid rgba(255,255,255,0.10);
                border-radius: 8px;
                padding: 5px 18px 5px 12px;
                font-size: 12px;
                min-width: 50px;
                outline: none;
            }
            QComboBox:hover {
                border-color: rgba(124, 138, 244, 0.5);
                background-color: #2a2c3e;
            }
            QComboBox:focus {
                border: 1px solid rgba(124, 138, 244, 0.5);
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 24px;
            }
            QComboBox::down-arrow {
                image: none;
                width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #8b8fa8;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2c3e;
                color: #e0e2f0;
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 8px;
                selection-background-color: #3c3f5c;
                outline: none;
                padding: 2px;
            }
            QComboBox QAbstractItemView::item {
                min-height: 20px;
                max-height: 20px;
                padding: 0px 8px;
            }
        """)
        
        # Install event filter to catch hover events
        self.period_combo.installEventFilter(self)
        
        self.period_combo.currentTextChanged.connect(self.refresh)
        rev_header.addWidget(self.period_combo)
        rev_layout.addLayout(rev_header)

        # Line chart
        self.revenue_chart = RevenueLineChart()
        rev_layout.addWidget(self.revenue_chart, 1)

        # Stats row at bottom — separated by border-top with proper spacing to prevent overlap
        stats_separator = QFrame()
        stats_separator.setObjectName("stats_separator")
        stats_separator.setFrameShape(QFrame.HLine)
        stats_separator.setFixedHeight(1)
        
        rev_layout.addSpacing(28)
        rev_layout.addWidget(stats_separator)
        rev_layout.addSpacing(12)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(16)

        self.lbl_avg_value = QLabel("₹0")
        self.lbl_avg_value.setObjectName("chart_stat_value")
        self.lbl_on_time_rate = QLabel("0%")
        self.lbl_on_time_rate.setObjectName("chart_stat_value")
        self.lbl_active_invoices = QLabel("0")
        self.lbl_active_invoices.setObjectName("chart_stat_value")

        stat_configs = [
            ("Avg Project Value", self.lbl_avg_value),
            ("On-Time Rate", self.lbl_on_time_rate),
            ("Active Invoices", self.lbl_active_invoices),
        ]

        for stat_label, val_lbl in stat_configs:
            stat_col = QVBoxLayout()
            stat_col.setSpacing(4)
            lbl = QLabel(stat_label)
            lbl.setObjectName("chart_stat_label")
            stat_col.addWidget(lbl)
            stat_col.addWidget(val_lbl)
            stats_row.addLayout(stat_col, 1)

        rev_layout.addLayout(stats_row)
        charts_row.addWidget(revenue_card, 2)

        # ─── Invoice Status Card (Donut Chart) ───────────────────────────
        status_card = QFrame()
        status_card.setObjectName("dashboard_chart_card")
        status_card.setStyleSheet("QFrame#dashboard_chart_card { background-color: #222336; border-radius: 12px; border: 1px solid #2d2e42; }")
        status_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        status_card.setMinimumHeight(400)
        status_card.setMinimumWidth(280)

        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(24, 24, 24, 24)
        status_layout.setSpacing(16)

        # Title
        status_title = QLabel("Invoice Status")
        status_title.setObjectName("chart_card_title")
        status_layout.addWidget(status_title)

        # Donut chart centered inside layout-based container (no setGeometry or move)
        donut_container = QWidget()
        donut_container.setObjectName("donut_container")
        donut_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        donut_layout = QVBoxLayout(donut_container)
        donut_layout.setAlignment(Qt.AlignCenter)
        donut_layout.setContentsMargins(0, 0, 0, 0)

        # Donut with center text overlay using QGridLayout
        donut_wrapper = QWidget()
        donut_wrapper.setObjectName("donut_wrapper")
        donut_wrapper.setFixedSize(192, 192)
        wrapper_layout = QGridLayout(donut_wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)

        self.donut_chart = DonutChart()
        wrapper_layout.addWidget(self.donut_chart, 0, 0, Qt.AlignCenter)

        # Center text overlay
        center_widget = QWidget()
        center_widget.setObjectName("donut_center_widget")
        center_widget.setFixedSize(192, 192)
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setAlignment(Qt.AlignCenter)
        center_layout.setSpacing(4)

        self.donut_center_value = QLabel("100%")
        self.donut_center_value.setObjectName("donut_center_value")
        self.donut_center_value.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(self.donut_center_value)

        self.donut_center_label = QLabel("TOTAL")
        self.donut_center_label.setObjectName("donut_center_label")
        self.donut_center_label.setAlignment(Qt.AlignCenter)
        center_layout.addWidget(self.donut_center_label)

        wrapper_layout.addWidget(center_widget, 0, 0, Qt.AlignCenter)

        donut_layout.addWidget(donut_wrapper, 0, Qt.AlignCenter)
        status_layout.addWidget(donut_container, 1)

        # Legend row (QHBoxLayout) matching reference
        legend_row = QHBoxLayout()
        legend_row.setSpacing(12)
        legend_row.setContentsMargins(0, 0, 0, 0)
        legend_row.setAlignment(Qt.AlignCenter)

        legend_items = [
            ("Paid", "legend_dot_completed"),
            ("Unpaid", "legend_dot_review"),
            ("Overdue", "legend_dot_delayed"),
        ]

        for legend_label, dot_id in legend_items:
            item_widget = QWidget()
            item_widget.setObjectName("legend_item_widget")
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 0, 0, 0)
            item_layout.setSpacing(8)

            dot = QLabel()
            dot.setObjectName(dot_id)
            dot.setFixedSize(8, 8)
            item_layout.addWidget(dot)

            text = QLabel(legend_label)
            text.setObjectName("legend_text")
            item_layout.addWidget(text)

            legend_row.addWidget(item_widget)

        status_layout.addLayout(legend_row)
        charts_row.addWidget(status_card, 1)

        layout.addLayout(charts_row)

        # ═══════════════════════════════════════════════════════════════════
        # RECENT PROJECTS TABLE
        # ═══════════════════════════════════════════════════════════════════
        table_card = QFrame()
        table_card.setObjectName("dashboard_table_card")
        table_card.setStyleSheet("QFrame#dashboard_table_card { background-color: #222336; border-radius: 12px; border: 1px solid #2d2e42; }")
        table_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        table_card.setMinimumHeight(420)
        table_card.setMaximumHeight(620)

        table_card_layout = QVBoxLayout(table_card)
        table_card_layout.setContentsMargins(0, 0, 0, 0)
        table_card_layout.setSpacing(0)

        # ── Filter tabs + View All row ────────────────────────────────
        filter_bar = QWidget()
        filter_bar.setObjectName("table_filter_bar")
        filter_bar_layout = QHBoxLayout(filter_bar)
        filter_bar_layout.setContentsMargins(20, 14, 20, 12)
        filter_bar_layout.setSpacing(4)

        self._filter_tabs: list[QPushButton] = []
        self._active_filter = "All"
        filter_statuses = ["All", "Not Started", "In Progress", "Review", "On Hold", "Completed", "Cancelled"]

        for fs in filter_statuses:
            btn = QPushButton(fs)
            btn.setObjectName("table_filter_tab")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setChecked(fs == "All")
            btn.setStyleSheet("""
                QPushButton#table_filter_tab {
                    background: transparent;
                    color: #6b6d85;
                    border: 1px solid transparent;
                    border-radius: 8px;
                    padding: 4px 12px;
                    font-size: 12px;
                    font-weight: 500;
                    min-height: 28px;
                }
                QPushButton#table_filter_tab:checked {
                    background: transparent;
                    color: #82d8ac;
                    border-color: #82d8ac;
                }
                QPushButton#table_filter_tab:hover:!checked {
                    background: rgba(200, 203, 223, 0.08);
                    color: #ffffff;
                }
            """)
            btn.clicked.connect(lambda checked, s=fs: self._apply_filter(s))
            filter_bar_layout.addWidget(btn)
            self._filter_tabs.append(btn)

        filter_bar_layout.addStretch()

        view_all_btn = QPushButton("View All →")
        view_all_btn.setObjectName("table_card_link")
        view_all_btn.setCursor(Qt.PointingHandCursor)
        view_all_btn.setStyleSheet("""
            QPushButton#table_card_link {
                background: transparent;
                color: #7c8af4;
                border: 1px solid transparent;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                padding: 5px 10px;
            }
            QPushButton#table_card_link:hover {
                background: #7c8af4;
                color: #ffffff;
                border-color: #7c8af4;
            }
        """)
        view_all_btn.clicked.connect(self._navigate_to_projects)
        filter_bar_layout.addWidget(view_all_btn)

        table_card_layout.addWidget(filter_bar)

        # Table widget — 6 columns: PROJECT, CLIENT, TYPE, STATUS, DEADLINE, BUDGET
        # Wrap table in its own scroll area so only the table scrolls
        table_scroll = QScrollArea()
        table_scroll.setWidgetResizable(True)
        table_scroll.setFrameShape(QFrame.NoFrame)
        table_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        table_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table_scroll.setMinimumHeight(300)
        table_scroll.setMaximumHeight(500)
        
        self.table = CustomTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["PROJECT", "CLIENT", "TYPE", "STATUS", "DEADLINE", "BUDGET"])
        self.table.setAlternatingRowColors(False)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.verticalHeader().setVisible(False)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        from PySide6.QtWidgets import QHeaderView
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        
        # Set default alignment to left for all headers (including BUDGET)
        header.setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        for col in range(6):
            header.setSectionResizeMode(col, QHeaderView.Fixed)

        table_scroll.setWidget(self.table)
        table_card_layout.addWidget(table_scroll)

        layout.addWidget(table_card)

        # Set up scroll area
        scroll.setWidget(content_widget)
        page_layout.addWidget(scroll)

        # Load data
        QTimer.singleShot(50, self._initial_load)

        # Connect to auto refresh signal
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app and hasattr(app, "data_changed"):
            app.data_changed.signal.connect(self.refresh_dashboard)

    def _initial_load(self) -> None:
        self.refresh()

    def refresh_dashboard(self) -> None:
        self.refresh()
    
    def eventFilter(self, obj, event):
        """Handle hover events for the period combo box to trigger shadow animation."""
        if obj == self.period_combo:
            event_type = event.type()
            # Try both Enter and HoverEnter to ensure compatibility
            if event_type in (QEvent.Enter, QEvent.HoverEnter):
                # Mouse entered - animate shadow in
                print(f"[DEBUG] Hover ENTER detected on period_combo, event type: {event_type}")
                self._period_combo_shadow_animation.stop()
                self._period_combo_shadow_animation.setStartValue(self._period_combo_shadow.blurRadius())
                self._period_combo_shadow_animation.setEndValue(20)
                self._period_combo_shadow_animation.start()
                print(f"[DEBUG] Shadow animation started: {self._period_combo_shadow.blurRadius()} -> 20")
                return False
            elif event_type in (QEvent.Leave, QEvent.HoverLeave):
                # Mouse left - animate shadow out
                print(f"[DEBUG] Hover LEAVE detected on period_combo, event type: {event_type}")
                self._period_combo_shadow_animation.stop()
                self._period_combo_shadow_animation.setStartValue(self._period_combo_shadow.blurRadius())
                self._period_combo_shadow_animation.setEndValue(0)
                self._period_combo_shadow_animation.start()
                print(f"[DEBUG] Shadow animation started: {self._period_combo_shadow.blurRadius()} -> 0")
                return False
        return super().eventFilter(obj, event)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _navigate_to_projects(self) -> None:
        """Navigate to the Projects page via the MainWindow."""
        widget = self
        while widget is not None:
            if hasattr(widget, "show_page"):
                widget.show_page("projects")
                return
            widget = widget.parent()

    def _apply_filter(self, status: str) -> None:
        """Switch the active filter tab and re-render the table."""
        self._active_filter = status
        for tab in self._filter_tabs:
            tab.setChecked(tab.text() == status)

        if status == "All":
            filtered = self._all_projects
        else:
            filtered = [p for p in self._all_projects if p["status"] == status]
        
        self._render_projects_to_table(filtered)

    def _render_projects_to_table(self, projects: list) -> None:
        """Fill the 6-column table matching the reference layout."""
        # Properly clear the table before rendering
        self.table.clearContents()
        self.table.clearSpans()
        self.table.setRowCount(0)

        if not projects:
            self.table.setRowCount(1)
            self.table.setSpan(0, 0, 1, 6)
            msg = "No projects match this filter." if self._active_filter != "All" else \
                  "No projects yet. Add your first project to get started."
            empty_label = QLabel(msg)
            empty_label.setStyleSheet("color: #6B7280; font-size: 13px;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(0, 0, empty_label)
            return

        self.table.setRowCount(len(projects))

        for i, proj in enumerate(projects):
            # 0 — PROJECT (bold white)
            name_item = QTableWidgetItem(proj["name"])
            name_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            font = name_item.font()
            font.setWeight(QFont.DemiBold)
            name_item.setFont(font)
            self.table.setItem(i, 0, name_item)

            # 1 — CLIENT
            client_item = QTableWidgetItem(proj["client_name"] or "—")
            client_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 1, client_item)

            # 2 — TYPE
            project_type = proj["type"] if proj["type"] else ""
            # If type is empty, infer from project name for better UX
            if not project_type:
                name_lower = proj["name"].lower()
                if "website" in name_lower or "web" in name_lower:
                    project_type = "Website"
                elif "app" in name_lower or "mobile" in name_lower:
                    project_type = "Mobile App"
                elif "design" in name_lower or "branding" in name_lower:
                    project_type = "Design"
                elif "dashboard" in name_lower or "ui" in name_lower:
                    project_type = "UI/UX"
                elif "marketing" in name_lower:
                    project_type = "Marketing"
                elif "packaging" in name_lower:
                    project_type = "Packaging"
                else:
                    project_type = "General"
            
            type_item = QTableWidgetItem(project_type)
            type_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 2, type_item)

            # 3 — STATUS (outlined pill badge)
            self.table.setCellWidget(i, 3, self._create_status_badge(proj["status"]))

            # 4 — DEADLINE ("Aug 1, 2026" format, left-aligned)
            raw_deadline = proj["deadline"] or ""
            if raw_deadline:
                try:
                    from datetime import datetime as _dt
                    parsed_date = _dt.strptime(raw_deadline, "%Y-%m-%d")
                    day = parsed_date.day
                    formatted_deadline = parsed_date.strftime(f"%b {day}, %Y")
                except Exception:
                    formatted_deadline = raw_deadline
            else:
                formatted_deadline = "—"
            deadline_item = QTableWidgetItem(formatted_deadline)
            deadline_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 4, deadline_item)

            # 5 — BUDGET (left-aligned, Indian ₹ format)
            budget = proj["budget"]
            if budget is not None and budget > 0:
                budget_str = "₹" + self._format_indian(int(budget))
            else:
                budget_str = "₹0"
            budget_item = QTableWidgetItem(budget_str)
            budget_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            self.table.setItem(i, 5, budget_item)

    def _create_status_badge(self, status: str) -> QWidget:
        """Styled pill badge matching the Stitch design with outline and proper spacing."""
        border_colors: dict[str, tuple[str, str]] = {
            # (border-color, text-color)
            "Completed":   ("#82d8ac", "#82d8ac"),
            "In Progress": ("#7c8af4", "#bcc2ff"),
            "Not Started": ("#555770", "#8B8FA8"),
            "On Hold":     ("#f0c878", "#f0c878"),
            "Review":      ("#7dd3e3", "#7dd3e3"),
            "Cancelled":   ("#e87c8a", "#e87c8a"),
        }
        border, fg = border_colors.get(status, ("#555770", "#8B8FA8"))

        container = QWidget()
        container.setObjectName("table_status_container")
        container.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        badge = QLabel(status)
        badge.setObjectName("status_pill_badge")
        badge.setAlignment(Qt.AlignCenter)
        badge.setStyleSheet(
            f"QLabel#status_pill_badge {{"
            f"  background-color: transparent;"
            f"  color: {fg};"
            f"  border: 1px solid {border};"
            f"  border-radius: 10px;"
            f"  font-size: 11px;"
            f"  font-weight: 600;"
            f"  padding: 3px 12px;"
            f"  min-height: 20px;"
            f"}}"
        )
        lay.addWidget(badge)
        return container

    @staticmethod
    def _format_indian(n: int) -> str:
        """Format an integer with Indian comma grouping: 1,20,000."""
        s = str(n)
        if len(s) <= 3:
            return s
        last3 = s[-3:]
        rest = s[:-3]
        groups = []
        while rest:
            groups.append(rest[-2:])
            rest = rest[:-2]
        groups.reverse()
        return ",".join(groups) + "," + last3

    def _populate_recent_projects(self) -> None:
        try:
            recent_projects = self.db.execute("""
                SELECT p.name, c.name as client_name, p.type, p.status,
                       p.deadline, p.budget
                FROM projects p
                LEFT JOIN clients c ON p.client_id = c.id
                ORDER BY p.created_date DESC
                LIMIT 50
            """)
        except Exception:
            recent_projects = []

        # Store all rows so filter tabs can work client-side
        self._all_projects = list(recent_projects) if recent_projects else []

        # Re-render with whatever filter is currently active
        self._apply_filter(self._active_filter)

    def _load_and_filter_projects(self) -> None:
        """Load projects data and apply current filter. Used by refresh method."""
        try:
            recent_projects = self.db.execute("""
                SELECT p.name, c.name as client_name, p.type, p.status,
                       p.deadline, p.budget
                FROM projects p
                LEFT JOIN clients c ON p.client_id = c.id
                ORDER BY p.created_date DESC
                LIMIT 50
            """)
        except Exception:
            recent_projects = []

        # Store all rows so filter tabs can work client-side
        self._all_projects = list(recent_projects) if recent_projects else []

        # Re-render with whatever filter is currently active
        self._apply_filter(self._active_filter)

    # ------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        try:
            # Helper function for currency formatting
            def format_currency(value):
                if value >= 10000000:
                    return f"₹{value/10000000:.1f}Cr"
                elif value >= 100000:
                    return f"₹{value/100000:.1f}L"
                elif value >= 1000:
                    return f"₹{value/1000:.1f}K"
                else:
                    return f"₹{int(value)}"
            
            # 1. TOTAL REVENUE — compare this month vs last month
            res_current = self.db.execute("""
                SELECT SUM(amount) as val FROM invoices 
                WHERE status='Paid' 
                AND strftime('%m-%Y', date_issued) = strftime('%m-%Y', 'now')
            """)
            current_revenue = res_current[0]["val"] if res_current and res_current[0]["val"] is not None else 0.0
            
            res_last = self.db.execute("""
                SELECT SUM(amount) as val FROM invoices 
                WHERE status='Paid' 
                AND strftime('%m-%Y', date_issued) = strftime('%m-%Y', date('now','-1 month'))
            """)
            last_month_revenue = res_last[0]["val"] if res_last and res_last[0]["val"] is not None else 0.0
            
            # Calculate all-time revenue for display
            res_total = self.db.execute("SELECT SUM(amount) as val FROM invoices WHERE status='Paid'")
            total_revenue = res_total[0]["val"] if res_total and res_total[0]["val"] is not None else 0.0
            
            self.card_revenue.set_value(format_currency(total_revenue))
            
            # Set revenue subtitle with comparison
            if current_revenue > last_month_revenue and last_month_revenue > 0:
                pct_change = ((current_revenue - last_month_revenue) / last_month_revenue * 100)
                subtitle, color = f"▲ +{pct_change:.1f}% from last month", "#4ADE80"
            elif current_revenue == last_month_revenue or last_month_revenue == 0:
                subtitle, color = "→ Same as last month", "#8B8FA8"
            else:
                pct_change = abs((current_revenue - last_month_revenue) / last_month_revenue * 100) if last_month_revenue > 0 else 0
                subtitle, color = f"▼ {pct_change:.1f}% from last month", "#E53E5A"
            
            self.card_revenue.set_sub_text(subtitle, color)
            
            # 2. ACTIVE PROJECTS — measure by overdue and at-risk
            res_active = self.db.execute("""
                SELECT COUNT(*) as cnt FROM projects 
                WHERE status IN ('In Progress', 'Review', 'Not Started')
            """)
            active_projects = res_active[0]["cnt"] if res_active else 0
            
            res_overdue = self.db.execute("""
                SELECT COUNT(*) as cnt FROM projects
                WHERE deadline < date('now')
                AND status NOT IN ('Completed', 'Cancelled')
            """)
            overdue_projects = res_overdue[0]["cnt"] if res_overdue else 0
            
            res_at_risk = self.db.execute("""
                SELECT COUNT(*) as cnt FROM projects
                WHERE deadline BETWEEN date('now') AND date('now', '+7 days')
                AND status NOT IN ('Completed', 'Cancelled')
            """)
            at_risk_projects = res_at_risk[0]["cnt"] if res_at_risk else 0
            
            self.card_projects.set_value(str(active_projects))
            
            # Set projects subtitle based on risk
            if overdue_projects > 0:
                subtitle, color = f"✕ {overdue_projects} project(s) overdue", "#E53E5A"
            elif at_risk_projects > 0:
                subtitle, color = f"⚠ {at_risk_projects} due this week", "#8B8FA8"
            else:
                subtitle, color = "✓ All projects on track", "#4ADE80"
            
            self.card_projects.set_sub_text(subtitle, color)
            
            # 3. PENDING INVOICES — measure by overdue invoices
            res_pending = self.db.execute("SELECT SUM(amount) as val FROM invoices WHERE status='Unpaid'")
            pending_invoices = res_pending[0]["val"] if res_pending and res_pending[0]["val"] is not None else 0.0
            
            res_overdue_inv = self.db.execute("""
                SELECT COUNT(*) as cnt FROM invoices
                WHERE status='Unpaid'
                AND due_date < date('now')
            """)
            overdue_invoices = res_overdue_inv[0]["cnt"] if res_overdue_inv else 0
            
            res_pending_inv = self.db.execute("""
                SELECT COUNT(*) as cnt FROM invoices
                WHERE status='Unpaid'
                AND due_date >= date('now')
            """)
            pending_count = res_pending_inv[0]["cnt"] if res_pending_inv else 0
            
            self.card_pending.set_value(format_currency(pending_invoices))
            
            # Set pending invoices subtitle
            if overdue_invoices > 0:
                subtitle, color = f"✕ {overdue_invoices} overdue invoice(s)", "#E53E5A"
            elif pending_count > 0:
                subtitle, color = f"⚠ {pending_count} awaiting payment", "#8B8FA8"
            else:
                subtitle, color = "✓ No pending invoices", "#4ADE80"
            
            self.card_pending.set_sub_text(subtitle, color)
            
            # 4. HOURS TRACKED — compare this week vs last week
            res_this_week = self.db.execute("""
                SELECT SUM(duration_hours) as val FROM time_logs
                WHERE date(start_time) >= date('now', '-7 days')
            """)
            this_week_hours = res_this_week[0]["val"] if res_this_week and res_this_week[0]["val"] is not None else 0.0
            
            res_last_week = self.db.execute("""
                SELECT SUM(duration_hours) as val FROM time_logs
                WHERE date(start_time) BETWEEN date('now', '-14 days') AND date('now', '-7 days')
            """)
            last_week_hours = res_last_week[0]["val"] if res_last_week and res_last_week[0]["val"] is not None else 0.0
            
            # Get total hours for display
            res_total_hours = self.db.execute("SELECT SUM(duration_hours) as val FROM time_logs")
            total_hours = res_total_hours[0]["val"] if res_total_hours and res_total_hours[0]["val"] is not None else 0.0
            
            self.card_hours.set_value(f"{total_hours:.1f}h" if total_hours > 0 else "0h")
            
            # Set hours subtitle with weekly comparison
            if this_week_hours > last_week_hours:
                subtitle, color = f"▲ {this_week_hours:.1f}h this week", "#4ADE80"
            elif this_week_hours == last_week_hours or last_week_hours == 0:
                subtitle, color = f"→ {this_week_hours:.1f}h this week", "#8B8FA8"
            else:
                subtitle, color = f"▼ {this_week_hours:.1f}h this week", "#E53E5A"
            
            self.card_hours.set_sub_text(subtitle, color)

            # 2. REVENUE OVERVIEW LINE CHART — dynamic date range
            selected_period = self.period_combo.currentText()
            today = date.today()
            current_year = today.year

            if selected_period == "All Time":
                start_date = "2000-01-01"
                end_date = "2099-12-31"
                group_by = "month"
            elif selected_period == "This Year":
                start_date = f"{current_year}-01-01"
                end_date = f"{current_year}-12-31"
                group_by = "month"
            elif selected_period == "Past 30 Days":
                start_date = (today - timedelta(days=30)).isoformat()
                end_date = today.isoformat()
                group_by = "week"
            else:  # Past 7 Days
                start_date = (today - timedelta(days=7)).isoformat()
                end_date = today.isoformat()
                group_by = "day"

            if group_by == "month":
                if selected_period == "All Time":
                    # Aggregate by year-month across all data
                    chart_rows = self.db.execute("""
                        SELECT strftime('%Y-%m', date_issued) as period_key, SUM(amount) as total
                        FROM invoices
                        WHERE status='Paid'
                        AND date_issued >= ? AND date_issued <= ?
                        GROUP BY period_key
                        ORDER BY period_key
                    """, (start_date, end_date))
                    if chart_rows:
                        chart_data = [float(r["total"]) if r["total"] else 0.0 for r in chart_rows]
                        # Show only last 12 periods max for readability
                        chart_data = chart_data[-12:]
                        month_labels_raw = [r["period_key"] for r in chart_rows][-12:]
                        # Format as "Jan '24" style
                        month_labels = []
                        for ym in month_labels_raw:
                            yr, mo = ym.split("-")
                            import calendar
                            month_labels.append(calendar.month_abbr[int(mo)])
                    else:
                        chart_data = [0.0] * 6
                        month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
                else:  # This Year — show all 12 months
                    month_abbrs = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                    month_nums = [f"{m:02d}" for m in range(1, 13)]
                    chart_rows = self.db.execute("""
                        SELECT strftime('%m', date_issued) as month_num, SUM(amount) as total
                        FROM invoices
                        WHERE status='Paid'
                        AND date_issued >= ? AND date_issued <= ?
                        GROUP BY month_num
                    """, (start_date, end_date))
                    db_data = {r["month_num"]: float(r["total"]) for r in chart_rows if r["total"] is not None}
                    chart_data = [db_data.get(m, 0.0) for m in month_nums]
                    month_labels = month_abbrs

            elif group_by == "week":
                # Past 30 days — group by week, but ensure we get multiple data points
                # Create 4 week buckets over the 30-day period for better visualization
                week_buckets = []
                for i in range(4):
                    week_start = today - timedelta(days=30 - i * 7)
                    week_end = today - timedelta(days=30 - (i + 1) * 7) if i < 3 else today
                    week_buckets.append((week_start.isoformat(), week_end.isoformat(), f"Wk{i+1}"))
                
                chart_data = []
                month_labels = []
                
                for week_start, week_end, label in week_buckets:
                    week_rows = self.db.execute("""
                        SELECT SUM(amount) as total
                        FROM invoices
                        WHERE status='Paid'
                        AND date_issued >= ? AND date_issued <= ?
                    """, (week_start, week_end))
                    
                    total = float(week_rows[0]["total"]) if week_rows and week_rows[0]["total"] else 0.0
                    chart_data.append(total)
                    month_labels.append(label)
                
                # Fallback if no data
                if not any(chart_data):
                    chart_data = [0.0] * 4
                    month_labels = ["Wk1", "Wk2", "Wk3", "Wk4"]

            else:  # group_by == "day" — Past 7 Days
                day_abbrs = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
                days = [(today - timedelta(days=6 - i)) for i in range(7)]
                day_strs = [d.isoformat() for d in days]
                chart_rows = self.db.execute("""
                    SELECT date_issued as day, SUM(amount) as total
                    FROM invoices
                    WHERE status='Paid'
                    AND date_issued >= ? AND date_issued <= ?
                    GROUP BY day
                    ORDER BY day
                """, (start_date, end_date))
                db_data = {r["day"]: float(r["total"]) for r in chart_rows if r["total"] is not None}
                chart_data = [db_data.get(d, 0.0) for d in day_strs]
                month_labels = [day_abbrs[d.weekday()] for d in days]

            self.revenue_chart.set_chart_data(chart_data, month_labels)

            # 3. INVOICE STATUS DONUT CHART queries
            res_paid = self.db.execute("SELECT COUNT(*) as cnt FROM invoices WHERE status='Paid'")
            paid_cnt = res_paid[0]["cnt"] if res_paid else 0

            res_unpaid_dyn = self.db.execute("SELECT COUNT(*) as cnt FROM invoices WHERE status='Unpaid' AND due_date >= DATE('now')")
            unpaid_cnt = res_unpaid_dyn[0]["cnt"] if res_unpaid_dyn else 0

            res_overdue_db = self.db.execute("SELECT COUNT(*) as cnt FROM invoices WHERE status='Overdue'")
            overdue_db_cnt = res_overdue_db[0]["cnt"] if res_overdue_db else 0

            res_overdue_dyn = self.db.execute("SELECT COUNT(*) as cnt FROM invoices WHERE status='Unpaid' AND due_date < DATE('now')")
            overdue_dyn_cnt = res_overdue_dyn[0]["cnt"] if res_overdue_dyn else 0

            overdue_cnt = overdue_db_cnt + overdue_dyn_cnt
            total_invoices = paid_cnt + unpaid_cnt + overdue_cnt

            if total_invoices > 0:
                self.donut_chart.set_data(paid_cnt, unpaid_cnt, overdue_cnt)
                self.donut_center_value.setText("100%")
                self.donut_center_label.setText("TOTAL")
            else:
                self.donut_chart.set_data(0, 0, 0)
                self.donut_center_value.setText("")
                self.donut_center_label.setText("No invoices yet")

            # 5. AVG PROJECT VALUE, ON-TIME RATE, ACTIVE INVOICES — filtered by selected period
            res_avg = self.db.execute(
                "SELECT AVG(budget) as val FROM projects WHERE created_date >= ? AND created_date <= ?",
                (start_date, end_date)
            )
            avg_val = res_avg[0]["val"] if res_avg and res_avg[0]["val"] is not None else 0.0

            res_on_time = self.db.execute(
                "SELECT COUNT(*) as cnt FROM projects WHERE deadline >= date('now') AND status='Completed' AND created_date >= ? AND created_date <= ?",
                (start_date, end_date)
            )
            on_time = res_on_time[0]["cnt"] if res_on_time else 0

            res_tot_comp = self.db.execute(
                "SELECT COUNT(*) as cnt FROM projects WHERE status='Completed' AND created_date >= ? AND created_date <= ?",
                (start_date, end_date)
            )
            total_completed = res_tot_comp[0]["cnt"] if res_tot_comp else 0

            on_time_rate = (on_time / total_completed * 100) if total_completed > 0 else 0

            res_act_inv = self.db.execute(
                "SELECT COUNT(*) as cnt FROM invoices WHERE status='Unpaid' AND date_issued >= ? AND date_issued <= ?",
                (start_date, end_date)
            )
            active_invoices = res_act_inv[0]["cnt"] if res_act_inv else 0

            self.lbl_avg_value.setText(_format_short_currency(avg_val))
            self.lbl_on_time_rate.setText(f"{on_time_rate:.0f}%")
            self.lbl_active_invoices.setText(str(active_invoices))

            # 4. RECENT PROJECTS TABLE
            self._load_and_filter_projects()

        except Exception:
            # Use Stitch sample data on error
            self._populate_sample_projects()

    def _populate_recent_projects(self) -> None:
        try:
            recent_projects = self.db.execute("""
                SELECT p.name, c.name as client_name, p.type, p.status, p.budget, p.deadline
                FROM projects p
                LEFT JOIN clients c ON p.client_id = c.id
                ORDER BY p.created_date DESC
                LIMIT 20
            """)
        except Exception:
            recent_projects = []

        if not recent_projects:
            self.table.setRowCount(1)
            self.table.setSpan(0, 0, 1, 6)
            empty_label = QLabel("No projects yet. Add your first project to get started.")
            empty_label.setStyleSheet("color: #6B7280; font-size: 13px;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(0, 0, empty_label)
            return

        self.table.clearSpans()
        self.table.setRowCount(len(recent_projects))

        for i, proj in enumerate(recent_projects):
            # Project Name
            name_item = QTableWidgetItem(proj["name"])
            name_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            font = name_item.font()
            font.setWeight(QFont.Medium)
            name_item.setFont(font)
            self.table.setItem(i, 0, name_item)

            # Client
            client_item = QTableWidgetItem(proj["client_name"] or "—")
            client_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 1, client_item)

            # Type — inferred from name if empty/NULL in DB
            project_type = proj["type"]
            if not project_type:
                name_lower = proj["name"].lower()
                if "website" in name_lower or "web" in name_lower:
                    project_type = "Website"
                elif "app" in name_lower or "mobile" in name_lower:
                    project_type = "Mobile App"
                elif "design" in name_lower or "branding" in name_lower:
                    project_type = "Design"
                elif "dashboard" in name_lower or "ui" in name_lower:
                    project_type = "UI/UX"
                elif "marketing" in name_lower:
                    project_type = "Marketing"
                elif "packaging" in name_lower:
                    project_type = "Packaging"
                else:
                    project_type = "General"
            type_item = QTableWidgetItem(project_type)
            type_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 2, type_item)

            # Status — rounded QSS status badge widget
            status_text = proj["status"]
            status_widget = self._create_status_badge(status_text)
            self.table.setCellWidget(i, 3, status_widget)

            # Deadline
            deadline_item = QTableWidgetItem(proj["deadline"] or "—")
            deadline_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 4, deadline_item)

            # Value/Budget in INR
            value_item = QTableWidgetItem(
                f"₹{proj['budget']:,.0f}" if proj["budget"] is not None else "₹0"
            )
            value_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 5, value_item)

    def _populate_sample_projects(self) -> None:
        """Populate with Stitch sample data in INR."""
        self.donut_chart.set_data(45, 25, 30)
        self.donut_center_value.setText("100%")

        sample_data = [
            ("Rebranding Concept", "Nexus Tech", "Design", "In Progress", "Oct 12, 2024", "₹4,200"),
            ("Mobile App UI", "Vanguard Finance", "Mobile App", "Completed", "Sep 28, 2024", "₹8,500"),
            ("Marketing Website", "Elevate Studio", "Website", "Review", "Oct 05, 2024", "₹3,100"),
            ("Packaging Design", "Lumiere Organics", "Packaging", "On Hold", "Oct 01, 2024", "₹1,850"),
        ]

        self.table.setRowCount(len(sample_data))

        for i, (name, client, project_type, status, deadline, value) in enumerate(sample_data):
            # Project Name
            name_item = QTableWidgetItem(name)
            name_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            font = name_item.font()
            font.setWeight(QFont.Medium)
            name_item.setFont(font)
            self.table.setItem(i, 0, name_item)

            # Client
            client_item = QTableWidgetItem(client)
            client_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 1, client_item)

            # Type
            type_item = QTableWidgetItem(project_type)
            type_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 2, type_item)

            # Status — rounded QSS status badge widget
            status_widget = self._create_status_badge(status)
            self.table.setCellWidget(i, 3, status_widget)

            # Deadline
            deadline_item = QTableWidgetItem(deadline)
            deadline_item.setForeground(QColor(Colors.TEXT_SECONDARY))
            self.table.setItem(i, 4, deadline_item)

            # Value
            value_item = QTableWidgetItem(value)
            value_item.setForeground(QColor(Colors.TEXT_PRIMARY))
            value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(i, 5, value_item)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from app.data.database import Database
    from app.ui.styles.theme import apply_dark_theme

    app = QApplication(sys.argv)
    apply_dark_theme(app)

    db = Database()
    db.initialize()

    window = DashboardPage(db)
    window.setWindowTitle("Dashboard Page Test")
    window.resize(1200, 800)
    window.show()

    sys.exit(app.exec())


