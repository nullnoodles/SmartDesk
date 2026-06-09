"""Stat card — KPI tile matching the Stitch Dashboard reference.

Layout: icon bubble (32x32, 4px radius) + uppercase label on top row,
big value below, optional sub-text at bottom. No hover animation on
the card itself. All styling via QSS #dashboard_stat_card.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout

from app.config import ASSETS_DIR
from app.ui.styles.theme import Colors

_ICONS_DIR = ASSETS_DIR / "icons"


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def _load_svg_icon(name: str, size: int = 20, color: str = "#bcc2ff") -> QPixmap:
    """Load an SVG icon, render at size, tint with color."""
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


class StatCard(QFrame):
    """Compact KPI tile: icon bubble + label, big value, sub-text.
    
    No hover animation on the card. setSizePolicy(Expanding, Fixed).
    """

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
        self.setObjectName("dashboard_stat_card")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumHeight(140)
        self.setMinimumWidth(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)  # Stitch: p-6 = 24px
        layout.setSpacing(8)

        # ─── Top row: icon bubble + label ─────────────────────────────────
        top_row = QHBoxLayout()
        top_row.setSpacing(12)  # Stitch: gap-3 = 12px

        # Icon bubble — 32x32, 4px radius, 10% tinted background
        self._icon_bubble = QLabel()
        self._icon_bubble.setObjectName("stat_card_icon_bubble")
        self._icon_bubble.setFixedSize(32, 32)
        self._icon_bubble.setAlignment(Qt.AlignCenter)

        # Try to load SVG icon, fall back to text
        if icon and (_ICONS_DIR / f"{icon}.svg").exists():
            icon_pixmap = _load_svg_icon(icon, size=20, color=accent)
            self._icon_bubble.setPixmap(icon_pixmap)
        else:
            self._icon_bubble.setText(icon[:1] if icon else "")
        top_row.addWidget(self._icon_bubble)

        # Label — label-caps style (11px, 700, uppercase)
        self._label = QLabel(label.upper())
        self._label.setObjectName("stat_card_label")
        top_row.addWidget(self._label, 1)
        layout.addLayout(top_row)

        layout.addSpacing(8)  # Stitch: mb-2 = 8px

        # ─── Value — headline-lg (24px, 700) ─────────────────────────────
        self._value = QLabel(value)
        self._value.setObjectName("stat_card_value")
        layout.addWidget(self._value)

        # ─── Sub-text — body-sm (13px, 400) ──────────────────────────────
        self._sub = QLabel(sub_text)
        self._sub.setObjectName("stat_card_subtext")
        self._sub.setVisible(bool(sub_text))
        layout.addWidget(self._sub)

    def set_value(self, value: str) -> None:
        self._value.setText(value)

    def set_sub_text(self, text: str, color: str | None = None) -> None:
        self._sub.setText(text)
        self._sub.setVisible(bool(text))
