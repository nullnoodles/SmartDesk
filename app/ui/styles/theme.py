"""
SmartDesk — Soft Professional Theme
A clean, modern dark theme with soft pastel accents, smooth transitions,
and a professional feel. Colors are muted and calming.
"""
from __future__ import annotations

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor


# ─── Color Palette ───────────────────────────────────────────────────────────
# Soft dark backgrounds with warm undertones
class Colors:
    """Central color definitions for the soft professional theme."""
    # Backgrounds
    BG_DARKEST = "#12131a"      # Sidebar / deepest layer
    BG_DARK = "#1a1b26"         # Main background
    BG_CARD = "#222336"         # Card surfaces
    BG_ELEVATED = "#2a2b3d"     # Elevated elements (hover states, inputs)
    BG_HOVER = "#32334a"        # Hover overlays

    # Borders
    BORDER_SUBTLE = "#2e2f42"
    BORDER_DEFAULT = "#3b3c54"
    BORDER_FOCUS = "#7c8af4"

    # Text
    TEXT_PRIMARY = "#e2e4f0"
    TEXT_SECONDARY = "#9a9cb8"
    TEXT_MUTED = "#6b6d85"
    TEXT_INVERSE = "#1a1b26"

    # Accent colors — soft pastels
    ACCENT_PRIMARY = "#7c8af4"      # Soft lavender-blue (primary actions)
    ACCENT_PRIMARY_HOVER = "#9aa4f7"
    ACCENT_PRIMARY_PRESSED = "#6470e0"

    ACCENT_SUCCESS = "#7dd3a8"      # Soft mint green
    ACCENT_SUCCESS_HOVER = "#9ae3be"

    ACCENT_WARNING = "#f0c878"      # Soft amber
    ACCENT_WARNING_HOVER = "#f5d898"

    ACCENT_DANGER = "#e87c8a"       # Soft rose
    ACCENT_DANGER_HOVER = "#f09aa5"

    ACCENT_INFO = "#6ec5d4"         # Soft teal
    ACCENT_INFO_HOVER = "#8dd4e0"

    # Chart / graph colors (harmonious soft palette)
    CHART_1 = "#7c8af4"     # Lavender
    CHART_2 = "#7dd3a8"     # Mint
    CHART_3 = "#f0c878"     # Amber
    CHART_4 = "#e87c8a"     # Rose
    CHART_5 = "#6ec5d4"     # Teal
    CHART_6 = "#c49cf4"     # Soft purple
    CHART_7 = "#f4a87c"     # Soft coral

    # Gradients (for special elements)
    GRADIENT_PRIMARY_START = "#7c8af4"
    GRADIENT_PRIMARY_END = "#6ec5d4"


# ─── Main Stylesheet ─────────────────────────────────────────────────────────

DARK_STYLESHEET = f"""
/* ═══════════════════════════════════════════════════════════════════════════
   GLOBAL
   ═══════════════════════════════════════════════════════════════════════════ */

QMainWindow {{
    background-color: {Colors.BG_DARK};
}}

QWidget {{
    background-color: {Colors.BG_DARK};
    color: {Colors.TEXT_PRIMARY};
    font-family: "Segoe UI", "Inter", "SF Pro Display", sans-serif;
    font-size: 13px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════════════════════════════════════ */

#sidebar {{
    background-color: {Colors.BG_DARKEST};
    border-right: 1px solid {Colors.BORDER_SUBTLE};
}}

#sidebar QPushButton {{
    background-color: transparent;
    color: {Colors.TEXT_SECONDARY};
    border: none;
    border-radius: 10px;
    padding: 12px 16px;
    text-align: left;
    font-size: 13px;
    margin: 2px 0px;
}}

#sidebar QPushButton:hover {{
    background-color: {Colors.BG_HOVER};
    color: {Colors.TEXT_PRIMARY};
}}

#sidebar QPushButton:checked {{
    background-color: {Colors.BG_CARD};
    color: {Colors.ACCENT_PRIMARY};
    font-weight: 600;
    border-left: 3px solid {Colors.ACCENT_PRIMARY};
    padding-left: 13px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   CARDS
   ═══════════════════════════════════════════════════════════════════════════ */

.card, QFrame[class="card"] {{
    background-color: {Colors.BG_CARD};
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 14px;
    padding: 22px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   TABLES
   ═══════════════════════════════════════════════════════════════════════════ */

QTableWidget {{
    background-color: {Colors.BG_DARK};
    alternate-background-color: {Colors.BG_DARKEST};
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 10px;
    gridline-color: {Colors.BORDER_SUBTLE};
    selection-background-color: {Colors.BG_ELEVATED};
    selection-color: {Colors.TEXT_PRIMARY};
}}

QTableWidget::item {{
    padding: 10px 8px;
    border-bottom: 1px solid {Colors.BORDER_SUBTLE};
}}

QTableWidget::item:selected {{
    background-color: {Colors.BG_ELEVATED};
}}

QHeaderView::section {{
    background-color: {Colors.BG_CARD};
    color: {Colors.TEXT_SECONDARY};
    padding: 10px 8px;
    border: none;
    border-bottom: 2px solid {Colors.BORDER_DEFAULT};
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   BUTTONS — Animated feel via transitions (QSS supports basic states)
   ═══════════════════════════════════════════════════════════════════════════ */

QPushButton {{
    background-color: {Colors.ACCENT_PRIMARY};
    color: {Colors.TEXT_INVERSE};
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 600;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {Colors.ACCENT_PRIMARY_HOVER};
}}

QPushButton:pressed {{
    background-color: {Colors.ACCENT_PRIMARY_PRESSED};
    padding: 11px 22px 9px 22px;
}}

QPushButton:disabled {{
    background-color: {Colors.BG_ELEVATED};
    color: {Colors.TEXT_MUTED};
}}

QPushButton#danger {{
    background-color: {Colors.ACCENT_DANGER};
    color: {Colors.TEXT_INVERSE};
}}

QPushButton#danger:hover {{
    background-color: {Colors.ACCENT_DANGER_HOVER};
}}

QPushButton#success {{
    background-color: {Colors.ACCENT_SUCCESS};
    color: {Colors.TEXT_INVERSE};
}}

QPushButton#success:hover {{
    background-color: {Colors.ACCENT_SUCCESS_HOVER};
}}

QPushButton#secondary {{
    background-color: {Colors.BG_ELEVATED};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
}}

QPushButton#secondary:hover {{
    background-color: {Colors.BG_HOVER};
    border-color: {Colors.ACCENT_PRIMARY};
}}

/* ═══════════════════════════════════════════════════════════════════════════
   INPUTS
   ═══════════════════════════════════════════════════════════════════════════ */

QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
    background-color: {Colors.BG_ELEVATED};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 10px;
    padding: 9px 14px;
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.ACCENT_PRIMARY};
    selection-color: {Colors.TEXT_INVERSE};
}}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1.5px solid {Colors.ACCENT_PRIMARY};
    background-color: {Colors.BG_CARD};
}}

QLineEdit::placeholder {{
    color: {Colors.TEXT_MUTED};
}}

QComboBox::drop-down {{
    border: none;
    padding-right: 10px;
}}

QComboBox QAbstractItemView {{
    background-color: {Colors.BG_CARD};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 8px;
    selection-background-color: {Colors.BG_ELEVATED};
    padding: 4px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   LABELS
   ═══════════════════════════════════════════════════════════════════════════ */

QLabel {{
    background-color: transparent;
}}

QLabel#heading {{
    font-size: 24px;
    font-weight: 700;
    color: {Colors.TEXT_PRIMARY};
    letter-spacing: -0.5px;
}}

QLabel#subheading {{
    font-size: 14px;
    color: {Colors.TEXT_SECONDARY};
    font-weight: 400;
}}

QLabel#card_title {{
    font-size: 12px;
    color: {Colors.TEXT_SECONDARY};
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel#card_value {{
    font-size: 26px;
    font-weight: 700;
    color: {Colors.ACCENT_PRIMARY};
}}

/* ═══════════════════════════════════════════════════════════════════════════
   SCROLLBARS
   ═══════════════════════════════════════════════════════════════════════════ */

QScrollBar:vertical {{
    background-color: transparent;
    width: 8px;
    border-radius: 4px;
    margin: 4px 0;
}}

QScrollBar::handle:vertical {{
    background-color: {Colors.BORDER_DEFAULT};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {Colors.TEXT_MUTED};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: transparent;
    height: 8px;
    border-radius: 4px;
}}

QScrollBar::handle:horizontal {{
    background-color: {Colors.BORDER_DEFAULT};
    border-radius: 4px;
    min-width: 30px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   TAB WIDGET
   ═══════════════════════════════════════════════════════════════════════════ */

QTabWidget::pane {{
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 10px;
    background-color: {Colors.BG_DARK};
    top: -1px;
}}

QTabBar::tab {{
    background-color: transparent;
    color: {Colors.TEXT_SECONDARY};
    padding: 10px 22px;
    border-bottom: 2px solid transparent;
    font-weight: 500;
    margin-right: 4px;
}}

QTabBar::tab:hover {{
    color: {Colors.TEXT_PRIMARY};
    background-color: {Colors.BG_ELEVATED};
    border-radius: 8px 8px 0 0;
}}

QTabBar::tab:selected {{
    color: {Colors.ACCENT_PRIMARY};
    border-bottom: 2px solid {Colors.ACCENT_PRIMARY};
    font-weight: 600;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   PROGRESS BAR
   ═══════════════════════════════════════════════════════════════════════════ */

QProgressBar {{
    background-color: {Colors.BG_ELEVATED};
    border-radius: 8px;
    text-align: center;
    color: {Colors.TEXT_SECONDARY};
    font-size: 11px;
    min-height: 12px;
    max-height: 12px;
}}

QProgressBar::chunk {{
    background-color: {Colors.ACCENT_PRIMARY};
    border-radius: 8px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   STATUS BAR
   ═══════════════════════════════════════════════════════════════════════════ */

QStatusBar {{
    background-color: {Colors.BG_DARKEST};
    color: {Colors.TEXT_MUTED};
    border-top: 1px solid {Colors.BORDER_SUBTLE};
    font-size: 11px;
    padding: 4px 16px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   GROUP BOX
   ═══════════════════════════════════════════════════════════════════════════ */

QGroupBox {{
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 10px;
    margin-top: 14px;
    padding-top: 18px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: {Colors.ACCENT_PRIMARY};
}}

/* ═══════════════════════════════════════════════════════════════════════════
   TOOLTIPS
   ═══════════════════════════════════════════════════════════════════════════ */

QToolTip {{
    background-color: {Colors.BG_CARD};
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_DEFAULT};
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 12px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   DIALOGS
   ═══════════════════════════════════════════════════════════════════════════ */

QDialog {{
    background-color: {Colors.BG_DARK};
}}

QMessageBox {{
    background-color: {Colors.BG_DARK};
}}

QDialogButtonBox QPushButton {{
    min-width: 80px;
}}
"""


def apply_dark_theme(app: QApplication) -> None:
    """Apply the soft professional dark theme to the application."""
    app.setStyleSheet(DARK_STYLESHEET)
