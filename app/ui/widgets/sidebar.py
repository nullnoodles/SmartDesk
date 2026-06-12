"""Sidebar navigation — Studio Graphite design.

Layout matches the Stitch reference: brand block with logo, nav buttons
with SVG icons, and footer user card. No NAVIGATION label.
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.config import APP_VERSION, ASSETS_DIR
from app.ui.styles.theme import Colors

# Icon directory
_ICONS_DIR = ASSETS_DIR / "icons"


def _load_svg_icon(name: str, size: int = 20, color: str = "#9a9cb8") -> QPixmap:
    """Load an SVG icon, render it at the given size, and tint it."""
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


class Sidebar(QWidget):
    """Persistent left sidebar with brand, nav buttons, and footer card."""

    page_changed = Signal(str)

    PAGES = [
        ("dashboard", "grid_view", "Dashboard"),
        ("clients", "group", "Clients"),
        ("projects", "folder_open", "Projects"),
        ("invoices", "receipt_long", "Invoices"),
        ("time", "timer", "Time Log"),
        ("contracts", "description", "Contracts"),
        ("analytics", "smart_toy", "AI Analytics"),
        ("settings", "settings", "Settings"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)  # Stitch spec: 240px
        self.setStyleSheet(f"""
            QWidget#sidebar {{
                background-color: #12131d;
                border-radius: 14px;
            }}
            QPushButton {{
                background-color: transparent;
                color: #9a9cb8;
                border: none;
                border-radius: 8px;
                padding: 4px 12px;
                margin: 1px 12px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
                min-height: 30px;
            }}
            QPushButton:hover {{
                background-color: #383844;
                color: #e2e4f0;
            }}
            QPushButton:checked {{
                background-color: rgba(124, 138, 244, 0.15);
                color: #7c8af4;
                border-left: 3px solid #7c8af4;
                padding-left: 9px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 24)
        layout.setSpacing(0)

        # ─── Brand header ─────────────────────────────────────────────────
        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(24, 20, 24, 20)
        brand_row.setSpacing(12)

        # Logo icon — "S" on primary-container background
        logo = QLabel("S")
        logo.setObjectName("sidebar_logo_icon")
        logo.setFixedSize(32, 32)
        logo.setAlignment(Qt.AlignCenter)
        brand_row.addWidget(logo)

        title = QLabel("SmartDesk")
        title.setObjectName("sidebar_logo_text")
        brand_row.addWidget(title)

        brand_row.addStretch()
        layout.addLayout(brand_row)

        layout.addSpacing(16)

        # ─── Navigation buttons (NO NAVIGATION label) ─────────────────────
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.buttons: dict[str, QPushButton] = {}

        for page_id, icon_name, label in self.PAGES:
            btn = self._make_nav_button(page_id, icon_name, label)
            self.button_group.addButton(btn)
            self.buttons[page_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # ─── Footer user card ─────────────────────────────────────────────
        user_row = QHBoxLayout()
        user_row.setContentsMargins(16, 16, 16, 0)
        user_row.setSpacing(12)

        # User avatar
        avatar = QLabel()
        avatar.setObjectName("sidebar_avatar")
        avatar.setFixedSize(40, 40)
        avatar.setAlignment(Qt.AlignCenter)
        avatar.setText("AM")
        user_row.addWidget(avatar)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)

        name_lbl = QLabel("Alex Mercer")
        name_lbl.setObjectName("sidebar_user_name")
        text_col.addWidget(name_lbl)

        role_lbl = QLabel("Freelance Designer")
        role_lbl.setObjectName("sidebar_user_role")
        text_col.addWidget(role_lbl)

        user_row.addLayout(text_col)
        user_row.addStretch()
        layout.addLayout(user_row)

        # Default selection
        if "dashboard" in self.buttons:
            self.buttons["dashboard"].setChecked(True)

    def _make_nav_button(self, page_id: str, icon_name: str, label: str) -> QPushButton:
        btn = QPushButton(f"  {label}")
        btn.setCheckable(True)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setToolTip(label)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Load SVG icon
        icon_pixmap = _load_svg_icon(icon_name, size=20, color=Colors.TEXT_SECONDARY)
        if not icon_pixmap.isNull():
            btn.setIcon(QIcon(icon_pixmap))
            btn.setIconSize(icon_pixmap.size())

        btn.clicked.connect(lambda _checked=False, pid=page_id: self.page_changed.emit(pid))
        return btn

    def set_active(self, page_id: str) -> None:
        if page_id in self.buttons:
            self.buttons[page_id].setChecked(True)
