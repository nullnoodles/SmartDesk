"""Page header — large title, subtitle, optional count pill, action slot.

Used at the top of every page to give consistent rhythm across screens.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.ui.styles.theme import Colors


class PageHeader(QWidget):
    """Title + subtitle + optional count chip + right-side action slot."""

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        count_text: str = "",
        parent=None,
    ):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # Left: stacked title + subtitle
        left = QVBoxLayout()
        left.setSpacing(4)

        title_row = QHBoxLayout()
        title_row.setSpacing(12)

        self._title = QLabel(title)
        self._title.setStyleSheet(
            f"color: {Colors.TEXT_PRIMARY}; background: transparent; "
            f"font-size: 32px; font-weight: 700; letter-spacing: -0.02em;"
        )
        title_row.addWidget(self._title, 0)

        self._count = QLabel(count_text)
        self._count.setVisible(bool(count_text))
        self._count.setAlignment(Qt.AlignVCenter)
        self._count.setStyleSheet(
            f"background-color: {Colors.BG_ELEVATED}; "
            f"border: 1px solid {Colors.BORDER_SUBTLE}; "
            f"border-radius: 999px; padding: 4px 12px; "
            f"color: {Colors.ACCENT_PRIMARY_LIGHT}; "
            f"font-size: 12px; font-weight: 600;"
        )
        title_row.addWidget(self._count, 0)
        title_row.addStretch()
        left.addLayout(title_row)

        self._subtitle = QLabel(subtitle)
        self._subtitle.setVisible(bool(subtitle))
        self._subtitle.setStyleSheet(
            f"color: {Colors.TEXT_SECONDARY}; background: transparent; "
            f"font-size: 14px; font-weight: 500;"
        )
        left.addWidget(self._subtitle)

        layout.addLayout(left, 1)

        # Right: actions container (caller adds buttons via add_action)
        self._actions_row = QHBoxLayout()
        self._actions_row.setSpacing(10)
        layout.addLayout(self._actions_row, 0)

    def set_count(self, text: str) -> None:
        self._count.setText(text)
        self._count.setVisible(bool(text))

    def set_subtitle(self, text: str) -> None:
        self._subtitle.setText(text)
        self._subtitle.setVisible(bool(text))

    def add_action(self, widget: QWidget) -> None:
        self._actions_row.addWidget(widget)
