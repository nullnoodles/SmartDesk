"""Stat card — KPI tile matching the Studio Graphite reference.

Layout: small uppercase label on the left, big value below; circular emoji
icon bubble on the right, optional trend sub-line at the bottom.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout

from app.ui.styles.theme import Colors


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


class StatCard(QFrame):
    """Compact KPI tile: label, big value, accent icon bubble, optional trend."""

    def __init__(
        self,
        label: str,
        value: str = "—",
        icon: str = "•",
        accent: str = Colors.ACCENT_PRIMARY,
        sub_text: str = "",
        sub_color: str | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("stat_card")
        # Fix: Use Expanding for both to allow proper card growth
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(150)  # Fix: Increased minimum height
        self.setMinimumWidth(200)   # Fix: Add minimum width to prevent compression
        self.setCursor(Qt.ArrowCursor)
        self._accent = accent
        self._default_sub_color = sub_color or Colors.TEXT_MUTED

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 22)  # Fix: Increased padding (min 12px)
        layout.setSpacing(12)  # Fix: Increased spacing

        # Top row — uppercase label + circular icon bubble
        top_row = QHBoxLayout()
        top_row.setSpacing(12)  # Fix: Increased spacing

        self._label = QLabel(label.upper())
        self._label.setWordWrap(True)  # Fix: Allow text wrapping
        self._label.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; "
            f"font-size: 11px; font-weight: 700; letter-spacing: 0.06em; "
            f"padding: 2px;"  # Fix: Add padding to prevent cutoff
        )
        self._label.setMinimumHeight(16)  # Fix: Ensure minimum height
        top_row.addWidget(self._label, 1)

        self._icon = QLabel(icon)
        self._icon.setFixedSize(40, 40)
        self._icon.setAlignment(Qt.AlignCenter)
        bubble_bg = _hex_to_rgba(accent, 0.12)
        self._icon.setStyleSheet(
            f"background-color: {bubble_bg}; "
            f"border-radius: 20px; color: {accent}; "
            f"font-size: 18px;"
        )
        top_row.addWidget(self._icon, 0)
        layout.addLayout(top_row)

        layout.addSpacing(6)  # Fix: Increased spacing

        # Value (tabular numbers)
        self._value = QLabel(value)
        self._value.setWordWrap(False)  # Fix: Prevent value wrapping
        self._value.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 30px; font-weight: 800; letter-spacing: -0.02em; "
            f"padding: 4px 0px;"  # Fix: Add vertical padding
        )
        self._value.setMinimumHeight(42)  # Fix: Increased minimum height
        layout.addWidget(self._value)

        layout.addSpacing(4)  # Fix: Add spacing before subtext

        # Sub-line / trend
        self._sub = QLabel(sub_text)
        self._sub.setVisible(bool(sub_text))
        self._sub.setWordWrap(True)  # Fix: Allow wrapping for long text
        self._sub.setStyleSheet(
            f"color: {self._default_sub_color}; background: transparent; "
            f"font-size: 12px; font-weight: 500; padding: 2px;"  # Fix: Add padding
        )
        self._sub.setMinimumHeight(16)  # Fix: Minimum height
        layout.addWidget(self._sub)

        layout.addStretch()

    def set_value(self, value: str) -> None:
        self._value.setText(value)

    def set_sub_text(self, text: str, color: str | None = None) -> None:
        self._sub.setText(text)
        self._sub.setVisible(bool(text))
        if color is not None:
            self._sub.setStyleSheet(
                f"color: {color}; background: transparent; "
                f"font-size: 12px; font-weight: 500; padding: 2px;"  # Fix: Maintain padding
            )
