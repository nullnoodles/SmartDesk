"""
SmartDesk — Studio Graphite Theme
Professional dark palette tuned for long focus sessions. Soft pastels for
status, deep neutrals layered for spatial hierarchy.
"""
from __future__ import annotations

from PySide6.QtWidgets import QApplication


# ─── Color Palette ───────────────────────────────────────────────────────────
class Colors:
    """Central color definitions for the Studio Graphite palette."""

    # Backgrounds (3 tiers of dark neutrals)
    BG_DARKEST = "#12131a"       # Sidebar — anchored / deepest layer
    BG_DARK = "#1a1b26"          # Main canvas
    BG_CARD = "#222336"           # Card surfaces (Level 2)
    BG_ELEVATED = "#1e1f2a"      # Inputs / table headers (Level 1.5)
    BG_HOVER = "#28293c"         # Hover overlays
    BG_DEEPEST = "#0c0d18"       # Sub-card / contextual deep

    # Borders
    BORDER_SUBTLE = "#2d2e42"
    BORDER_DEFAULT = "#454652"
    BORDER_FOCUS = "#7c8af4"

    # Text
    TEXT_PRIMARY = "#e2e4f0"
    TEXT_SECONDARY = "#9a9cb8"
    TEXT_MUTED = "#6b6d85"
    TEXT_INVERSE = "#0f208b"     # Used on primary-container buttons
    TEXT_ON_PRIMARY = "#061987"

    # Accent — primary (lavender-blue family)
    ACCENT_PRIMARY = "#7c8af4"           # primary-container — for buttons
    ACCENT_PRIMARY_HOVER = "#9aa4f7"
    ACCENT_PRIMARY_PRESSED = "#6470e0"
    ACCENT_PRIMARY_LIGHT = "#bcc2ff"     # primary — for active text/icons

    # Accent — semantic statuses
    ACCENT_SUCCESS = "#82d8ac"           # secondary — mint
    ACCENT_SUCCESS_HOVER = "#9ae3be"
    ACCENT_WARNING = "#f0c878"           # status-warning — amber
    ACCENT_WARNING_HOVER = "#f5d898"
    ACCENT_DANGER = "#e87c8a"            # status-danger — rose
    ACCENT_DANGER_HOVER = "#f09aa5"
    ACCENT_INFO = "#7dd3e3"              # tertiary — teal
    ACCENT_INFO_HOVER = "#8dd4e0"

    # Chart colors (harmonious soft palette)
    CHART_1 = "#7c8af4"     # Lavender
    CHART_2 = "#82d8ac"     # Mint
    CHART_3 = "#f0c878"     # Amber
    CHART_4 = "#e87c8a"     # Rose
    CHART_5 = "#7dd3e3"     # Teal
    CHART_6 = "#bcc2ff"     # Light lavender
    CHART_7 = "#f4a87c"     # Soft coral

    # Gradients
    GRADIENT_PRIMARY_START = "#7c8af4"
    GRADIENT_PRIMARY_END = "#bcc2ff"


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
    font-family: "Inter", "Segoe UI", "SF Pro Display", sans-serif;
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
    border-left: 3px solid transparent;
    border-radius: 0px;
    padding: 11px 16px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
    margin: 1px 8px;
}}

#sidebar QPushButton:hover {{
    background-color: {Colors.BG_HOVER};
    color: {Colors.TEXT_PRIMARY};
    border-radius: 8px;
    border-left: 3px solid transparent;
}}

#sidebar QPushButton:checked {{
    background-color: rgba(124, 138, 244, 0.10);
    color: {Colors.ACCENT_PRIMARY_LIGHT};
    font-weight: 700;
    border-left: 3px solid {Colors.ACCENT_PRIMARY};
    border-radius: 0px 8px 8px 0px;
    margin-left: 0px;
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

QFrame#stat_card {{
    background-color: {Colors.BG_CARD};
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 14px;
}}

QFrame#stat_card:hover {{
    background-color: {Colors.BG_HOVER};
    border: 1px solid {Colors.BORDER_DEFAULT};
}}

/* ═══════════════════════════════════════════════════════════════════════════
   TABLES — clean style, no vertical grid, row dividers via item border
   ═══════════════════════════════════════════════════════════════════════════ */

QTableWidget {{
    background-color: {Colors.BG_CARD};
    alternate-background-color: {Colors.BG_ELEVATED};
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 14px;
    gridline-color: transparent;
    selection-background-color: {Colors.BG_HOVER};
    selection-color: {Colors.TEXT_PRIMARY};
}}

QTableWidget::item {{
    padding: 12px 8px;
    border: none;
    border-bottom: 1px solid {Colors.BORDER_SUBTLE};
}}

QTableWidget::item:selected {{
    background-color: {Colors.BG_HOVER};
    color: {Colors.TEXT_PRIMARY};
}}

QHeaderView::section {{
    background-color: {Colors.BG_ELEVATED};
    color: {Colors.TEXT_PRIMARY};
    padding: 12px 8px;
    border: none;
    border-bottom: 1px solid {Colors.BORDER_SUBTLE};
    font-weight: 700;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

QHeaderView::section:first {{
    border-top-left-radius: 14px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 14px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════════════════════════════ */

QPushButton {{
    background-color: {Colors.ACCENT_PRIMARY};
    color: {Colors.TEXT_ON_PRIMARY};
    border: none;
    border-radius: 10px;
    padding: 10px 22px;
    font-weight: 700;
    font-size: 13px;
}}

QPushButton:hover {{
    background-color: {Colors.ACCENT_PRIMARY_HOVER};
}}

QPushButton:pressed {{
    background-color: {Colors.ACCENT_PRIMARY_PRESSED};
}}

QPushButton:disabled {{
    background-color: {Colors.BG_ELEVATED};
    color: {Colors.TEXT_MUTED};
}}

QPushButton#danger {{
    background-color: {Colors.ACCENT_DANGER};
    color: #1a1b26;
}}

QPushButton#danger:hover {{
    background-color: {Colors.ACCENT_DANGER_HOVER};
}}

QPushButton#success {{
    background-color: {Colors.ACCENT_SUCCESS};
    color: #1a1b26;
}}

QPushButton#success:hover {{
    background-color: {Colors.ACCENT_SUCCESS_HOVER};
}}

QPushButton#secondary {{
    background-color: transparent;
    color: {Colors.TEXT_PRIMARY};
    border: 1px solid {Colors.BORDER_SUBTLE};
}}

QPushButton#secondary:hover {{
    background-color: {Colors.BG_HOVER};
    border: 1px solid {Colors.ACCENT_PRIMARY};
    color: {Colors.ACCENT_PRIMARY_LIGHT};
}}

QPushButton#ghost {{
    background-color: transparent;
    color: {Colors.TEXT_SECONDARY};
    border: none;
}}

QPushButton#ghost:hover {{
    background-color: {Colors.BG_HOVER};
    color: {Colors.TEXT_PRIMARY};
}}

/* ═══════════════════════════════════════════════════════════════════════════
   INPUTS
   ═══════════════════════════════════════════════════════════════════════════ */

QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
    background-color: {Colors.BG_ELEVATED};
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 10px;
    padding: 9px 14px;
    color: {Colors.TEXT_PRIMARY};
    selection-background-color: {Colors.ACCENT_PRIMARY};
    selection-color: {Colors.TEXT_ON_PRIMARY};
}}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
    border: 1px solid {Colors.ACCENT_PRIMARY};
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
    border-radius: 10px;
    selection-background-color: {Colors.BG_HOVER};
    padding: 4px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   LABELS
   ═══════════════════════════════════════════════════════════════════════════ */

QLabel {{
    background-color: transparent;
}}

QLabel#heading {{
    font-size: 32px;
    font-weight: 700;
    color: {Colors.TEXT_PRIMARY};
    letter-spacing: -0.02em;
}}

QLabel#heading-lg {{
    font-size: 24px;
    font-weight: 700;
    color: {Colors.TEXT_PRIMARY};
    letter-spacing: -0.01em;
}}

QLabel#subheading {{
    font-size: 14px;
    color: {Colors.TEXT_SECONDARY};
    font-weight: 400;
}}

QLabel#card_title {{
    font-size: 11px;
    color: {Colors.TEXT_MUTED};
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}}

QLabel#card_value {{
    font-size: 28px;
    font-weight: 700;
    color: {Colors.TEXT_PRIMARY};
    letter-spacing: -0.01em;
}}

QLabel#caps {{
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: {Colors.TEXT_MUTED};
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
    background-color: {Colors.BORDER_SUBTLE};
    border-radius: 4px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {Colors.BORDER_DEFAULT};
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
    background-color: {Colors.BORDER_SUBTLE};
    border-radius: 4px;
    min-width: 30px;
}}

/* ═══════════════════════════════════════════════════════════════════════════
   TAB WIDGET
   ═══════════════════════════════════════════════════════════════════════════ */

QTabWidget::pane {{
    border: 1px solid {Colors.BORDER_SUBTLE};
    border-radius: 14px;
    background-color: {Colors.BG_CARD};
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
    color: {Colors.ACCENT_PRIMARY_LIGHT};
    border-bottom: 2px solid {Colors.ACCENT_PRIMARY};
    font-weight: 700;
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
    border-radius: 14px;
    margin-top: 14px;
    padding-top: 18px;
    font-weight: 700;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: {Colors.ACCENT_PRIMARY_LIGHT};
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
    """Apply the Studio Graphite dark theme to the application."""
    app.setStyleSheet(DARK_STYLESHEET)
