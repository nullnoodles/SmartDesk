"""Stat card — compact metric tile used at the top of list pages.

Layout matches the Studio Graphite reference: small uppercase label, large
tabular-numbers value, accent icon bubble in the top-right, optional trend
sub-line below the value.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout

from app.ui.styles.theme import Colors


class StatCard(QFrame):
    """Compact KPI tile with icon bubble, label, value, and optional sub-line."""

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
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(120)
        self._accent = accent
        self._sub_color = sub_color or Colors.TEXT_MUTED

        layout = QVBoxLayout(self)
        layout.setContentsMargins(22, 20, 22, 20)
        layout.setSpacing(10)

        # Top row — label on left, icon bubble on right
        top_row = QHBoxLayout()
        top_row.setSpacing(8)

        self._label = QLabel(label.upper())
        self._label.setObjectName("caps")
        self._label.setStyleSheet(
            f"color: {Colors.TEXT_MUTED}; background: transparent; "
            f"font-size: 11px; font-weight: 700; letter-spacing: 0.05em;"
        )
        top_row.addWidget(self._label, 1)

        self._icon = QLabel(icon)
        self._icon.setFixedSize(36, 36)
        self._icon.setAlignment(Qt.AlignCenter)
        self._icon.setStyleSheet(
            f"background-color: rgba(124, 138, 244, 0.10); "
            f"border-radius: 10px; color: {accent}; font-size: 16px;"
        )
        top_row.addWidget(self._icon, 0)
        layout.addLayout(top_row)

        # Value
        self._value = QLabel(value)
        self._value.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 28px; font-weight: 700; letter-spacing: -0.01em;"
        )
        layout.addWidget(self._value)

        # Sub-line
        self._sub = QLabel(sub_text)
        self._sub.setStyleSheet(
            f"color: {self._sub_color}; background: transparent; "
            f"font-size: 12px; font-weight: 500;"
        )
        self._sub.setVisible(bool(sub_text))
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
                f"font-size: 12px; font-weight: 500;"
            )
