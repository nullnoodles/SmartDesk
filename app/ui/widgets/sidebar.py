"""Sidebar navigation widget — soft professional design with smooth transitions."""
from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QButtonGroup, QFrame,
)
from PySide6.QtCore import Signal, Qt

from app.config import APP_VERSION
from app.ui.styles.theme import Colors


class Sidebar(QWidget):
    """Persistent left sidebar with animated navigation buttons."""

    page_changed = Signal(str)

    PAGES = [
        ("dashboard", "📊", "Dashboard"),
        ("clients", "👥", "Clients"),
        ("projects", "📁", "Projects"),
        ("invoices", "🧾", "Invoices"),
        ("time", "⏱️", "Time Log"),
        ("contracts", "📝", "Contracts"),
        ("analytics", "🤖", "AI Analytics"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(230)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 24, 16, 24)
        layout.setSpacing(4)

        # App branding
        brand_layout = QVBoxLayout()
        brand_layout.setSpacing(2)

        title = QLabel("SmartDesk")
        title.setObjectName("heading")
        title.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 700;
            color: {Colors.ACCENT_PRIMARY};
            background: transparent;
            letter-spacing: -0.5px;
        """)
        brand_layout.addWidget(title)

        subtitle = QLabel("Freelancer Hub")
        subtitle.setObjectName("subheading")
        subtitle.setStyleSheet(f"""
            font-size: 12px;
            color: {Colors.TEXT_MUTED};
            background: transparent;
        """)
        brand_layout.addWidget(subtitle)
        layout.addLayout(brand_layout)

        # Separator
        layout.addSpacing(20)
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {Colors.BORDER_SUBTLE}; max-height: 1px;")
        layout.addWidget(sep)
        layout.addSpacing(16)

        # Navigation section label
        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet(f"""
            font-size: 10px;
            font-weight: 600;
            color: {Colors.TEXT_MUTED};
            letter-spacing: 1px;
            background: transparent;
            padding-left: 4px;
        """)
        layout.addWidget(nav_label)
        layout.addSpacing(8)

        # Navigation buttons
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.buttons: dict[str, QPushButton] = {}

        for page_id, icon, label in self.PAGES:
            btn = QPushButton(f"  {icon}   {label}")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, pid=page_id: self.page_changed.emit(pid))
            self.button_group.addButton(btn)
            self.buttons[page_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # Bottom section — version + status
        bottom_sep = QFrame()
        bottom_sep.setFrameShape(QFrame.HLine)
        bottom_sep.setStyleSheet(f"background-color: {Colors.BORDER_SUBTLE}; max-height: 1px;")
        layout.addWidget(bottom_sep)
        layout.addSpacing(12)

        status_row = QLabel(f"● Online")
        status_row.setStyleSheet(f"""
            font-size: 11px;
            color: {Colors.ACCENT_SUCCESS};
            background: transparent;
            padding-left: 4px;
        """)
        layout.addWidget(status_row)

        version_label = QLabel(f"v{APP_VERSION}")
        version_label.setStyleSheet(f"""
            color: {Colors.TEXT_MUTED};
            font-size: 10px;
            background: transparent;
            padding-left: 4px;
        """)
        layout.addWidget(version_label)

        # Default selection
        self.buttons["dashboard"].setChecked(True)

    def set_active(self, page_id: str) -> None:
        if page_id in self.buttons:
            self.buttons[page_id].setChecked(True)
