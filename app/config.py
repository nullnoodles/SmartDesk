
from __future__ import annotations
import os
import sys
from pathlib import Path

# --- App metadata ---
APP_NAME = "SmartDesk"
APP_VERSION = "1.0.0"
APP_AUTHOR = "N1rm"
APP_DESCRIPTION = "Intellitgent Freelancer Management System with Predictive Analytics"

# --- Paths ---
# Handle PyInstaller frozen mode
if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
    _INTERNAL_DIR = BASE_DIR / "_internal"
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    _INTERNAL_DIR = BASE_DIR

DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"
ASSETS_DIR = _INTERNAL_DIR / "assets"
ML_MODELS_DIR = _INTERNAL_DIR / "app" / "ml" / "models" if getattr(sys, "frozen", False) else Path(__file__).resolve().parent / "ml" / "models"

# Icon paths
ICON_PATH = ASSETS_DIR / "icon.ico"
ICON_PNG_PATH = ASSETS_DIR / "icon.png"
SPLASH_PATH = ASSETS_DIR / "splash.png"

# Ensure runtime directories exist
DATA_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
ML_MODELS_DIR.mkdir(parents=True, exist_ok=True)

# --- Database ---
DB_PATH = DATA_DIR / "smartdesk.db"

# --- Invoice ---
GST_RATE = 0.18
INVOICE_PREFIX = "INV"
CURRENCY_SYMBOL = "₹"

# --- ML ---
MIN_TRAINING_SAMPLES = 5
CLAUSE_MODEL_NAME = "all-MiniLM-L6-v2"

# --- Market rate benchmarks (INR/hour) ---
MARKET_RATES = {
    "Design": 600,
    "Video": 900,
    "Writing": 350,
    "Music": 700,
    "Development": 800,
    "General": 500,
}
