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

    def __init__(self, label: str, color: str = Colors.ACCENT_PRIMARY, bg_color: str | None = None, parent=None):
        super().__init__(parent)
        bg = bg_color if bg_color is not None else _hex_to_rgba(color, 0.12)
        self.setStyleSheet(
            f"background-color: {bg}; border-radius: 999px;"
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(7)

        dot = QLabel("●")
        dot.setAlignment(Qt.AlignVCenter)
        dot.setStyleSheet(
            f"background: transparent; color: {color}; font-size: 9px;"
        )
        layout.addWidget(dot)

        text = QLabel(label.upper())
        text.setAlignment(Qt.AlignVCenter)
        text.setStyleSheet(
            f"background: transparent; color: {color}; "
            f"font-size: 10px; font-weight: 700; letter-spacing: 0.04em;"
        )
        layout.addWidget(text)
        layout.addStretch()
