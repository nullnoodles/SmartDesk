# SmartDesk — AI-Powered Freelancer Management System

A desktop application for freelance creative professionals to manage clients, projects, invoices, time tracking, and get AI-powered business insights — all offline.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PySide6](https://img.shields.io/badge/GUI-PySide6-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

### Core Business Management
- **Client Management** — CRUD operations with search
- **Project Tracking** — Status lifecycle (Not Started → In Progress → Completed)
- **Invoice Generation** — Auto-numbered with 18% GST calculation
- **PDF Export** — Professional invoice PDFs with sender info, logo, and UPI QR codes
- **Payment Tracking** — Record and monitor payments
- **Time Tracking** — Live timer + manual entry per project
- **Settings** — Business profile, preferences, backup/restore, CSV export

### AI/ML Intelligence Layer
| Feature | Technology | Description |
|---------|-----------|-------------|
| **Smart Pricing Advisor** | NumPy + NLP | Suggests price ranges based on project complexity |
| **Payment Delay Predictor** | Random Forest (sklearn) | Predicts if invoices will be paid on time |
| **Income Forecaster** | ARIMA (statsmodels) | 3-month income projections |
| **Contract Risk Analyzer** | Rule-based + NLP | Scores contract risk factors |
| **Clause Classifier** | Sentence-transformers | Categorizes contract clauses |

### Additional Features
- **PDF Contract Analysis** — Upload PDF → extract text → classify clauses → risk report
- **UPI QR Codes** — Payment QR codes embedded on invoices (Indian market)
- **Backup & Restore** — Single-zip backup of database and exported PDFs
- **CSV Export** — Clients, projects, and invoices for accountants
- **Dark Theme** — Professional, eye-friendly interface
- **Offline-First** — No internet required, all data stored locally

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.10+ |
| GUI | PySide6 (Qt 6) |
| Database | SQLite3 |
| PDF Generation | ReportLab |
| PDF Parsing | pdfplumber |
| ML/NLP | scikit-learn, statsmodels |
| Charts | Matplotlib |
| Packaging | PyInstaller |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/nullnoodles/SmartDesk.git
cd SmartDesk

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# (Optional) Train NLP clause classifier model
python scripts/train_clause_model.py

# Run the app
python main.py
```

On first launch, SmartDesk shows a welcome dialog. Configure your business name,
GSTIN, and UPI ID under **Settings → Business Profile** so they appear on
generated invoices.

## Build Standalone Executable

```bash
# Build .exe (Windows)
.\build.bat

# Output: dist\SmartDesk\SmartDesk.exe
```

The PyInstaller spec is `smartdesk.spec` at the project root.

## Backup & Restore

Use **Settings → Backup & Restore** to:
- Create a portable `.zip` containing your database and exported PDFs.
- Restore a backup to migrate to a new machine or recover from data loss.

## Testing

```bash
pytest
```

Tests cover repositories, services, ML modules, and a UI smoke suite that
instantiates every page widget.

## Project Structure

```
SmartDesk/
├── main.py                    # Application entry point
├── smartdesk.spec             # PyInstaller spec
├── app/
│   ├── config.py              # Constants, paths, business rules
│   ├── data/
│   │   ├── database.py        # SQLite connection manager
│   │   ├── schema.sql         # Table definitions + indexes
│   │   ├── migrations.py      # Schema migration runner
│   │   └── repositories/      # Data access layer (one per table)
│   ├── core/
│   │   ├── invoice_service.py # Invoice business logic
│   │   ├── pdf_exporter.py    # PDF generation
│   │   ├── time_tracker.py    # Timer logic
│   │   ├── settings_service.py # User preferences and business profile
│   │   ├── backup_service.py  # Backup / restore
│   │   └── csv_exporter.py    # CSV export
│   ├── ml/                    # Pricing, payment predictor, forecaster, etc.
│   ├── ui/
│   │   ├── main_window.py
│   │   ├── styles/theme.py
│   │   ├── widgets/           # Reusable UI components, welcome dialog
│   │   └── pages/             # Dashboard, clients, projects, invoices, time,
│   │                          #   contracts, analytics, settings
│   └── utils/                 # Logger, UPI QR generator
├── scripts/                   # Build, seed_data, ML training
├── tests/                     # pytest suite
├── assets/                    # Icons, splash screen
├── data/                      # SQLite database + log file (gitignored)
└── exports/                   # Generated PDFs (gitignored)
```

## Architecture

SmartDesk follows a layered architecture:

```
┌─────────────────────────────────────┐
│           UI Layer (PySide6)        │
│  pages/ → widgets/ → styles/        │
├─────────────────────────────────────┤
│         Business Logic Layer        │
│  core/ (services) + ml/ (AI/ML)     │
├─────────────────────────────────────┤
│          Data Access Layer          │
│  repositories/ → database.py        │
├─────────────────────────────────────┤
│            SQLite Database          │
│         data/smartdesk.db           │
└─────────────────────────────────────┘
```

## Business Rules

- GST Rate: 18% (Indian tax)
- Invoice Format: `INV-YYYY-NNNN`
- Currency: ₹ (Indian Rupee)
- All data stored locally (offline-first)

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
