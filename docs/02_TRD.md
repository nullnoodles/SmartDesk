# Technical Requirements Document (TRD)
## SoloDash — Freelancer Management System

---

## 1. System Architecture

### 1.1 Architectural Pattern

SoloDash follows a **Layered Architecture** with strict separation of concerns. Each layer depends only on the layer immediately below it.

```
┌──────────────────────────────────────────────────┐
│  PRESENTATION LAYER (PySide6 GUI)                │
│  • MainWindow, Sidebar, Pages, Dialogs           │
└──────────────────────────┬───────────────────────┘
                           │
┌──────────────────────────▼───────────────────────┐
│  BUSINESS LOGIC LAYER (Services)                 │
│  • InvoiceService, TimeTracker, PDFExporter      │
└──────────┬───────────────────────────┬───────────┘
           │                           │
┌──────────▼──────────┐    ┌───────────▼──────────┐
│  INTELLIGENCE LAYER │    │  DATA ACCESS LAYER   │
│  • ML / NLP Models  │    │  • Repositories      │
└──────────┬──────────┘    └───────────┬──────────┘
           │                           │
           └─────────────┬─────────────┘
                         │
┌────────────────────────▼─────────────────────────┐
│  PERSISTENCE LAYER (SQLite + File System)        │
│  • database.db, exports/, models/                │
└──────────────────────────────────────────────────┘
```

### 1.2 Module Dependencies

- **UI** depends on Services and Repositories (read-only)
- **Services** depend on Repositories
- **ML Modules** depend on Repositories (for training data)
- **Repositories** depend only on Database
- **No circular dependencies allowed**

## 2. Technology Stack

### 2.1 Core Stack

| Layer | Technology | Version | License |
|-------|-----------|---------|---------|
| Language | Python | 3.11+ | PSF |
| GUI Framework | PySide6 | 6.7.2 | LGPL |
| Database | SQLite3 | Built-in | Public Domain |
| ORM | Raw SQL via repository pattern | — | — |

### 2.2 ML / Intelligence Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| Tabular ML | scikit-learn 1.5 | Random Forest, Logistic Regression |
| Time Series | statsmodels 0.14 | ARIMA forecasting |
| NLP Embeddings | sentence-transformers 3.0 | MiniLM-L6-v2 for clause classification |
| Data Manipulation | pandas 2.2, numpy 1.26 | Feature engineering |
| Model Persistence | joblib 1.4 | .pkl serialization |

### 2.3 Document & Media Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| PDF Generation | reportlab 4.2 | Invoice PDFs |
| PDF Parsing | pdfplumber 0.11 | Contract text extraction |
| Image / OCR | Pillow, pytesseract | Receipt OCR (P2) |
| QR Codes | qrcode 7.4 | UPI payment links |
| Charts | matplotlib 3.9, pyqtgraph 0.13 | Dashboard visualizations |

### 2.4 Utility Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| Notifications | plyer 2.1 | Desktop notifications |
| Date Handling | python-dateutil 2.9 | Date arithmetic |
| Testing | pytest 8.3 | Unit tests |
| Packaging | PyInstaller 6.x | Windows .exe |

## 3. Module Specifications

### 3.1 Data Layer (`app/data/`)

#### `database.py`
- Single class `Database` wraps SQLite operations
- Initializes schema from `schema.sql` on first run
- Enforces foreign keys via `PRAGMA foreign_keys = ON`
- Uses `sqlite3.Row` for dict-like row access
- Connection pattern: open per query, close immediately (single-user app)

#### Repository Pattern
- One repository class per database table
- Each repo: `add()`, `get_by_id()`, `get_all()`, `update()`, `delete()`
- Specialized methods on each: e.g., `InvoiceRepository.get_overdue()`
- All queries parameterized to prevent SQL injection

### 3.2 Core Layer (`app/core/`)

#### `invoice_service.py`
- Generates sequential invoice numbers (INV-2026-NNNN)
- Calculates 18% GST automatically
- Sets due date (default: today + 14 days)
- Manages status transitions: Unpaid → Paid / Cancelled

#### `pdf_exporter.py`
- Uses ReportLab `SimpleDocTemplate` with A4 page size
- Standard layout: header → bill-to → table → footer
- Branded with project color (#2E75B6)
- Saves to `exports/{invoice_number}.pdf`

#### `time_tracker.py`
- Stateful: holds active session in memory
- `start(project_id, description)` → records start time
- `stop()` → calculates duration, persists to DB, returns hours
- `add_manual(project_id, hours, description)` → adds backdated entry

### 3.3 Intelligence Layer (`app/ml/`)

#### Model Architecture Summary

| Module | Algorithm | Input | Output | Training Data |
|--------|-----------|-------|--------|---------------|
| `risk_analyzer.py` | Rules + Regex | Contract metadata + text | Risk score (0-100), level (LOW/MED/HIGH) | None — deterministic rules |
| `clause_classifier.py` | sentence-transformers + LogisticRegression | Clause text | Category + confidence | 30+ labeled clauses |
| `payment_predictor.py` | RandomForestClassifier | (amount, days_to_due, type) | Class probabilities | Paid invoices in DB |
| `income_forecaster.py` | ARIMA(1,1,1) / WMA fallback | Monthly income series | Next-3-month forecast | 3+ months of payment data |
| `pricing_advisor.py` | Hybrid heuristic | (type, hours, description, revisions) | Price range + reasoning | Market rates + history |

#### Model Persistence
- Saved to `app/ml/models/*.pkl` via joblib
- Loaded lazily on first use (heavy embeddings only when needed)
- Re-trained on demand via the Analytics page

### 3.4 Presentation Layer (`app/ui/`)

#### Page Pattern
Every page is a `QWidget` subclass with:
- `__init__(db)` — receives Database instance via dependency injection
- `refresh()` — public method called when page becomes visible
- Internal action methods named `_action_name()`

#### Theme
- Dark Catppuccin-inspired stylesheet in `styles/theme.py`
- Applied globally via `QApplication.setStyleSheet()`
- Object names (`#sidebar`, `#heading`, `#danger`) for selective styling

## 4. API Contracts (Internal)

### 4.1 Database Manager
```python
class Database:
    def initialize(self) -> None
    def execute(self, query: str, params: tuple = ()) -> list[Row]
    def execute_returning_id(self, query: str, params: tuple) -> int
    def execute_many(self, query: str, param_list: list[tuple]) -> None
```

### 4.2 ML Module Contracts

```python
# Pricing Advisor
suggest_price(
    project_type: str,
    estimated_hours: float,
    description: str = "",
    revision_rounds: int = 2
) -> {
    "low": float, "mid": float, "high": float,
    "effective_hourly_rate": float,
    "estimated_hours": float,
    "reasoning": list[str]
}

# Payment Predictor
predict(
    amount: float,
    days_to_due: int,
    project_type: str
) -> {
    "prediction": "on_time" | "late" | "very_late" | "unknown",
    "confidence": float,  # 0-100
    "probabilities": dict[str, float]
}

# Income Forecaster
forecast(months_ahead: int = 3) -> {
    "method": "arima" | "moving_average" | "insufficient_data",
    "forecast": list[{"month": str, "predicted_income": float}],
    "historical": list[{"month": str, "income": float}]
}

# Risk Analyzer
full_analysis(
    hourly_rate: float,
    revisions: int,
    timeline_days: int,
    project_type: str = "General",
    contract_text: str = ""
) -> {
    "total_score": int,  # 0-100+
    "risk_level": "LOW" | "MEDIUM" | "HIGH",
    "findings": list[{"check": str, "result": str, "score": int}]
}
```

## 5. Performance Requirements

| Operation | Target | Rationale |
|-----------|--------|-----------|
| App startup | < 3 sec | User experience |
| Page switch | < 200 ms | Snappy navigation |
| PDF export | < 3 sec | One invoice |
| Database query | < 50 ms | For tables under 10k rows |
| ML training (Random Forest) | < 5 sec | On 100 samples |
| Clause classification | < 1 sec/clause | Single embedding + predict |
| Income forecast | < 2 sec | ARIMA fit |

## 6. Security Requirements

| Aspect | Implementation |
|--------|----------------|
| SQL Injection | Parameterized queries everywhere |
| Data Privacy | All data local; no network calls |
| Backup | User-initiated copy of `data/solodash.db` |
| Access Control | OS-level (single-user app) |

## 7. Testing Strategy

| Layer | Approach | Coverage Target |
|-------|----------|-----------------|
| Repositories | Unit tests with in-memory SQLite | 80%+ |
| Services | Unit tests + integration | 70%+ |
| ML Modules | Test trained model loads and predicts | Smoke tests |
| UI | Manual + screenshot comparison | Critical flows only |

## 8. Deployment

### 8.1 Build Command
```
pyinstaller --onefile --windowed --icon=assets/icon.ico ^
  --add-data "app/data/schema.sql;app/data" ^
  --add-data "app/ml/models;app/ml/models" ^
  main.py
```

### 8.2 Distribution
- Single `solodash.exe` file (~150MB with sentence-transformers)
- First-run creates `data/solodash.db` next to the executable
- All exports written to `exports/` next to the executable

## 9. Maintenance Considerations

- Schema changes require migration scripts in future versions
- ML models versioned via filename (e.g., `payment_predictor_v2.pkl`)
- Training data should grow over time; retrain monthly is recommended
