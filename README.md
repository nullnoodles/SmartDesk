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
- **PDF Export** — Professional invoice PDFs with UPI QR codes
- **Payment Tracking** — Record and monitor payments
- **Time Tracking** — Live timer + manual entry per project

### AI/ML Intelligence Layer (~25% of codebase)
| Feature | Technology | Description |
|---------|-----------|-------------|
| **Smart Pricing Advisor** | NumPy + NLP | Suggests price ranges based on project complexity |
| **Payment Delay Predictor** | Random Forest (sklearn) | Predicts if invoices will be paid on time |
| **Income Forecaster** | ARIMA (statsmodels) | 3-month income projections |
| **Contract Risk Analyzer** | Rule-based + NLP | Scores contract risk factors |
| **Clause Classifier** | Sentence-transformers | Categorizes contract clauses |

### Additional Features
- **PDF Contract Analysis** — Upload PDF → extract text → classify clauses → risk report
- **UPI QR Codes** — Payment QR codes on invoices (Indian market)
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
git clone https://github.com/yourusername/smartdesk.git
cd smartdesk

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Train ML model (first time only)
python scripts/train_clause_model.py

# Run the app
python main.py
```

## Build Standalone Executable

```bash
# Build .exe (Windows)
.\build.bat

# Output: dist\SmartDesk\SmartDesk.exe
```

## Project Structure

```
smartdesk/
├── main.py                    # Application entry point
├── app/
│   ├── config.py              # Constants, paths, business rules
│   ├── data/
│   │   ├── database.py        # SQLite connection manager
│   │   ├── schema.sql         # Table definitions + indexes
│   │   └── repositories/      # Data access layer (one per table)
│   ├── core/
│   │   ├── invoice_service.py # Invoice business logic
│   │   ├── pdf_exporter.py    # PDF generation
│   │   └── time_tracker.py    # Timer logic
│   ├── ml/
│   │   ├── pricing_advisor.py # Smart pricing suggestions
│   │   ├── payment_predictor.py # Payment delay prediction
│   │   ├── income_forecaster.py # ARIMA forecasting
│   │   ├── risk_analyzer.py   # Contract risk scoring
│   │   ├── clause_classifier.py # NLP clause categorization
│   │   ├── contract_parser.py # PDF text extraction
│   │   └── models/            # Serialized .pkl models
│   ├── ui/
│   │   ├── main_window.py     # Root window + navigation
│   │   ├── styles/theme.py    # Dark theme stylesheet
│   │   ├── widgets/           # Reusable UI components
│   │   └── pages/             # One module per screen
│   └── utils/
│       └── upi_qr.py          # UPI QR code generation
├── scripts/
│   ├── build.py               # Build automation
│   ├── seed_data.py           # Sample data generator
│   └── train_clause_model.py  # ML model training
├── assets/                    # Icons, splash screen
├── data/                      # SQLite database (gitignored)
├── exports/                   # Generated PDFs (gitignored)
└── tests/                     # Test suite
```

## Architecture

SmartDesk follows a **layered architecture**:

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

## Screenshots

*Coming soon*

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
