"""
SmartDesk — Studio Graphite Theme
Professional dark palette tuned for long focus sessions. Soft pastels for
status, deep neutrals layered for spatial hierarchy.

Loads the Inter font family via QFontDatabase and applies the external
style.qss stylesheet.
"""
from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication


# ─── Asset paths ──────────────────────────────────────────────────────────
_HERE = Path(__file__).resolve().parent
_QSS_PATH = _HERE / "style.qss"
_FONTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "assets" / "fonts"


# ─── Color Palette ───────────────────────────────────────────────────────
class Colors:
    """Central color definitions for the Studio Graphite palette.

    These constants are used by Python code that needs dynamic color
    references (charts, per-instance accent colours, etc.).
    All *structural* styling lives in style.qss.
    """

    BG_DARKEST = "#12131d"       # Sidebar — anchored / deepest layer
    BG_DARK = "#12131d"          # Main canvas
    BG_CARD = "#1a1b26"          # Card surfaces (Level 2)
    BG_ELEVATED = "#1e1f2a"      # Inputs / table headers (Level 1.5)
    BG_HOVER = "#383844"         # Hover overlays
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
    ACCENT_SUCCESS = "#7dd3a8"           # secondary — mint
    ACCENT_SUCCESS_HOVER = "#9ae3be"
    ACCENT_WARNING = "#f0c878"           # status-warning — amber
    ACCENT_WARNING_HOVER = "#f5d898"
    ACCENT_DANGER = "#e87c8a"            # status-danger — rose
    ACCENT_DANGER_HOVER = "#f09aa5"
    ACCENT_INFO = "#6ec5d4"              # tertiary — teal
    ACCENT_INFO_HOVER = "#8dd4e0"

    # Chart colors (harmonious soft palette)
    CHART_1 = "#7c8af4"     # Lavender
    CHART_2 = "#7dd3a8"     # Mint
    CHART_3 = "#f0c878"     # Amber
    CHART_4 = "#e87c8a"     # Rose
    CHART_5 = "#6ec5d4"     # Teal
    CHART_6 = "#bcc2ff"     # Light lavender
    CHART_7 = "#f4a87c"     # Soft coral

    # Gradients
    GRADIENT_PRIMARY_START = "#7c8af4"
    GRADIENT_PRIMARY_END = "#bcc2ff"


# ─── Font loading ────────────────────────────────────────────────────────

def _load_inter_fonts() -> None:
    """Load bundled Inter TTF files into QFontDatabase."""
    if not _FONTS_DIR.is_dir():
        return

    for ttf in _FONTS_DIR.glob("Inter-*.ttf"):
        font_id = QFontDatabase.addApplicationFont(str(ttf))
        if font_id < 0:
            print(f"[theme] WARNING: Failed to load font: {ttf.name}")


# ─── QSS loading ─────────────────────────────────────────────────────────

def _load_qss() -> str:
    """Read the external QSS stylesheet from disk."""
    if _QSS_PATH.is_file():
        return _QSS_PATH.read_text(encoding="utf-8")
    print(f"[theme] WARNING: QSS file not found at {_QSS_PATH}")
    return ""


# ─── Public API ──────────────────────────────────────────────────────────

def apply_dark_theme(app: QApplication) -> None:
    """Load Inter fonts, read the QSS file, and apply the Studio Graphite
    dark theme to the entire application."""

    # 1. Register bundled Inter font files
    _load_inter_fonts()

    # 2. Set Inter as the default application font
    font = QFont("Inter", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    app.setFont(font)

    # 3. Load and apply the external QSS stylesheet
    qss = _load_qss()
    app.setStyleSheet(qss)
