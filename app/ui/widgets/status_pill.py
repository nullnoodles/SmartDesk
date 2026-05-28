"""Status pill — colored dot + label, used in list tables and analytics."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from app.ui.styles.theme import Colors


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


class StatusPill(QWidget):
    """Pill-shaped tag with a colored dot prefix."""

    def __init__(self, label: str, color: str = Colors.ACCENT_PRIMARY, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        bg = _hex_to_rgba(color, 0.12)
        inner = QLabel(f"●  {label.upper()}")
        inner.setAlignment(Qt.AlignVCenter)
        inner.setStyleSheet(
            f"background-color: {bg}; color: {color}; "
            f"border-radius: 999px; padding: 3px 10px; "
            f"font-size: 10px; font-weight: 700; letter-spacing: 0.04em;"
        )
        layout.addWidget(inner)
        layout.addStretch()
