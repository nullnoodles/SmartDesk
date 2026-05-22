# SmartDesk — Tech Stack & Build

## Core Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.x |
| GUI | PySide6 (Qt 6) |
| Database | SQLite3 (stdlib) |
| PDF Generation | ReportLab |
| PDF Parsing | pdfplumber |
| ML/NLP | scikit-learn, sentence-transformers, statsmodels |
| Charts | Matplotlib, pyqtgraph |
| Packaging | PyInstaller |
| Testing | pytest |

## Key Libraries

- `pandas` / `numpy` — data manipulation
- `joblib` — model serialization (.pkl files)
- `qrcode` — UPI QR code generation
- `Pillow` — image processing
- `pytesseract` — OCR (receipt scanning)
- `plyer` — desktop notifications
- `python-dateutil` — date parsing

## Common Commands

```bash
# Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Run the app
python main.py

# Train ML model (first time or after data changes)
python scripts/train_clause_model.py

# Build standalone .exe
python scripts/build.py

# Run tests
pytest

# Syntax check
python scripts/check_syntax.py
```

## Build Notes

- PyInstaller config is in `solodash.spec` at project root
- Build output goes to `dist/SmartDesk/`
- The build script auto-generates the icon and trains ML models if missing
- Frozen mode (PyInstaller) uses `sys.executable` parent as BASE_DIR and looks for assets in `_internal/`

## Code Conventions

- Use `from __future__ import annotations` at the top of every module
- Module-level docstrings describe purpose
- Type hints on function signatures (return types, parameters)
- Classes use PascalCase, functions/methods use snake_case
- Constants are UPPER_SNAKE_CASE in `app/config.py`
- SQL queries use parameterized `?` placeholders (never string interpolation)
- PySide6 signals/slots for UI event handling
- Each page widget exposes a `refresh()` method for data reload on navigation
