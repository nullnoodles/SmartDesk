"""Tiny avatar circle — colored background with initials. Used in tables."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from app.ui.styles.theme import Colors


# Soft palette to vary avatar colors deterministically based on the name
_AVATAR_COLORS = [
    Colors.ACCENT_PRIMARY,
    Colors.ACCENT_SUCCESS,
    Colors.ACCENT_WARNING,
    Colors.ACCENT_DANGER,
    Colors.ACCENT_INFO,
    Colors.ACCENT_PRIMARY_LIGHT,
]


def _initials(name: str) -> str:
    parts = [p for p in (name or "").split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def _color_for(name: str) -> str:
    seed = sum(ord(c) for c in (name or ""))
    return _AVATAR_COLORS[seed % len(_AVATAR_COLORS)]


class Avatar(QLabel):
    """Circular avatar with auto-generated initials and color from the name."""

    def __init__(self, name: str = "", size: int = 30, parent=None):
        super().__init__(parent)
        bg = _color_for(name)
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.setText(_initials(name))
        radius = size // 2
        font_size = max(10, size // 3)
        self.setStyleSheet(
            f"background-color: {bg}; color: {Colors.TEXT_ON_PRIMARY}; "
            f"border-radius: {radius}px; font-size: {font_size}px; font-weight: 700;"
        )
