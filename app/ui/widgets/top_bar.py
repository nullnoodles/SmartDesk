"""Top bar — matches the Stitch Dashboard header.

Simplified layout: "Overview" title on the left, notification button +
"New Project" button on the right. No search bar, no mode pill, no help
button, no user block.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from app.config import ASSETS_DIR
from app.ui.styles.theme import Colors

_ICONS_DIR = ASSETS_DIR / "icons"


def _load_svg_icon(name: str, size: int = 20, color: str = "#9a9cb8") -> QPixmap:
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


class TopBar(QWidget):
    """Top header — page title + notification + new project button."""

    # Keep signal for backward compat even though search is removed
    search_changed = Signal(str)

    def __init__(self, user_name: str = "Freelancer", role: str = "OFFLINE WORKSPACE", parent=None):
        super().__init__(parent)
        self.setFixedHeight(64)  # Stitch: h-16 = 64px
        self.setObjectName("top_bar")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(32, 0, 32, 0)  # Stitch: px-8 = 32px
        layout.setSpacing(16)

        # ─── Left: Page title (Removed per user request) ──────────────────
        self._title = QLabel("")
        self._title.setObjectName("top_bar_title")
        self._title.hide()

        layout.addStretch()

        # ─── Right: Notification button + User Profile ────────────────────
        # Notification icon button
        notif_btn = QPushButton()
        notif_btn.setObjectName("top_bar_notification_btn")
        notif_btn.setFixedSize(40, 40)
        notif_btn.setCursor(Qt.PointingHandCursor)
        notif_btn.setToolTip("Notifications")
        notif_icon = _load_svg_icon("notifications", size=20, color=Colors.TEXT_SECONDARY)
        if not notif_icon.isNull():
            notif_btn.setIcon(QIcon(notif_icon))
            notif_btn.setIconSize(notif_icon.size())
        layout.addWidget(notif_btn)

        # User profile block
        user_profile = QWidget()
        user_profile.setObjectName("top_bar_user_profile")
        user_profile_layout = QHBoxLayout(user_profile)
        user_profile_layout.setContentsMargins(8, 0, 0, 0)
        user_profile_layout.setSpacing(8)

        # Avatar
        tb_avatar = QLabel("AM")
        tb_avatar.setObjectName("top_bar_avatar")
        tb_avatar.setFixedSize(32, 32)
        tb_avatar.setAlignment(Qt.AlignCenter)
        user_profile_layout.addWidget(tb_avatar)

        # Name
        tb_name = QLabel("Alex Mercer")
        tb_name.setObjectName("top_bar_user_name")
        user_profile_layout.addWidget(tb_name)

        layout.addWidget(user_profile)

    def set_title(self, title: str) -> None:
        """Update the page title shown in the top bar."""
        self._title.setText(title)

    def set_user(self, name: str, role: str = "") -> None:
        """Backward compatibility — no-op since user block was removed."""
        pass
