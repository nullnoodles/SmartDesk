# SmartDesk — Project Structure

## Top-Level Layout

```
solodash/
├── main.py              # Application entry point (splash → DB init → main window)
├── requirements.txt     # Pinned Python dependencies
├── solodash.spec        # PyInstaller build spec
├── app/                 # Application source code
├── scripts/             # Dev/build utilities
├── assets/              # Icons, splash image
├── data/                # Runtime SQLite database (gitignored content)
├── exports/             # Generated PDF invoices
├── tests/               # pytest test suite
├── docs/                # Design documents (PRD, TRD, UI/UX, etc.)
├── build/               # PyInstaller build artifacts
└── dist/                # Packaged executable output
```

## `app/` — Source Code

### `app/config.py`
Central configuration: paths, constants, app metadata. Handles frozen (PyInstaller) vs development mode path resolution.

### `app/data/`
Data access layer.
- `database.py` — SQLite connection wrapper with query helpers (`execute`, `execute_returning_id`, `execute_many`)
- `schema.sql` — DDL for all tables (clients, projects, invoices, payments, time_logs, tasks, contracts, ml_predictions)
- `repositories/` — One repository class per table. Each takes a `Database` instance and exposes CRUD methods.

### `app/core/`
Business logic services.
- `invoice_service.py` — Invoice creation, GST calculation, status transitions
- `pdf_exporter.py` — ReportLab PDF generation for invoices
- `time_tracker.py` — Timer logic and time log management

### `app/ml/`
Machine learning and NLP modules.
- `clause_classifier.py` — Sentence-transformer based clause categorization
- `contract_parser.py` — PDF text extraction with pdfplumber
- `risk_analyzer.py` — Rule-based + text scanning risk scoring
- `payment_predictor.py` — Random Forest payment delay prediction
- `income_forecaster.py` — ARIMA / moving average forecasting
- `pricing_advisor.py` — Hybrid market + historical pricing
- `models/` — Serialized `.pkl` model files

### `app/ui/`
PySide6 GUI layer.
- `main_window.py` — QMainWindow with sidebar + QStackedWidget page navigation
- `styles/theme.py` — Dark theme stylesheet applied globally
- `widgets/` — Reusable UI components (sidebar, animated widgets)
- `pages/` — One module per screen (dashboard, clients, projects, invoices, time, contracts, analytics). Each page is a QWidget with a `refresh()` method.

### `app/utils/`
Standalone utilities (UPI QR code generation).

## Architecture Pattern

- **Repository pattern** for data access — each table has a dedicated repository class
- **Service layer** in `app/core/` for business logic above raw data access
- **Page-based UI** — each screen is a self-contained QWidget registered in a QStackedWidget
- **Dependency injection** — `Database` instance is created in `main.py` and passed down to pages/services
- **Offline-first** — no network calls, all data local to the machine
