# Application Flow Document
## SoloDash — Freelancer Management System

---

## 1. High-Level Application Flow

```
                    ┌──────────────────┐
                    │   Launch App     │
                    │  (python main.py)│
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Initialize DB   │
                    │ (run schema.sql) │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Apply Theme     │
                    │  Build Window    │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  Show Dashboard  │
                    │   (default page) │
                    └────────┬─────────┘
                             │
                             ▼
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
      ┌──────────┐    ┌──────────┐    ┌──────────┐
      │  CRUD    │    │   AI     │    │  Export  │
      │  Flows   │    │  Flows   │    │  Flows   │
      └──────────┘    └──────────┘    └──────────┘
```

## 2. Core CRUD Flows

### 2.1 Add Client Flow

```
Dashboard
   │
   │ User clicks "Clients" in sidebar
   ▼
Clients Page (list view)
   │
   │ User clicks "+ Add Client"
   ▼
Client Dialog (modal)
   │
   │ User fills: name, email, phone, address, company
   │ User clicks "OK"
   ▼
Validation
   │
   ├── Invalid? → Show error, stay in dialog
   │
   └── Valid?
       │
       ▼
   ClientRepository.add()
       │
       │ INSERT INTO clients (...)
       ▼
   Refresh client list
       │
       ▼
   Dialog closes
```

### 2.2 Create Project Flow

```
Clients Page
   │
   │ User has at least one client
   │ User navigates to Projects
   ▼
Projects Page
   │
   │ User clicks "+ New Project"
   ▼
Project Dialog (modal)
   │
   │ User selects:
   │   - Client (from dropdown)
   │   - Project name
   │   - Type
   │   - Description
   │   - Deadline
   │   - Budget
   ▼
Validation (name required)
   │
   ▼
ProjectRepository.add()
   │
   │ INSERT INTO projects (...)
   │ FK references client
   ▼
Refresh projects list
```

### 2.3 Create Invoice Flow

```
Projects Page (existing project)
   │
   │ User navigates to Invoices
   ▼
Invoices Page
   │
   │ User clicks "+ Create Invoice"
   ▼
Invoice Dialog
   │
   │ User selects project
   │ User enters amount
   │ User sets due-in days (default 14)
   ▼
InvoiceService.create_invoice()
   │
   ├── Generate invoice number
   │   (next from COUNT + 1)
   │
   ├── Calculate GST (amount × 0.18)
   │
   ├── Calculate total (amount + tax)
   │
   ├── Calculate due_date (today + N days)
   │
   └── INSERT INTO invoices
        │
        ▼
   Refresh invoice list
   New row appears with status "Unpaid"
```

### 2.4 Export Invoice as PDF Flow

```
Invoices Page
   │
   │ User selects an invoice row
   │ User clicks "Export PDF"
   ▼
Fetch full invoice data
   │
   │ JOIN invoices, projects, clients
   ▼
PDFExporter.export_invoice()
   │
   ├── Build A4 document
   │
   ├── Add header (INVOICE — INV-2026-0001)
   │
   ├── Add bill-to section
   │
   ├── Build line items table
   │   (description, amount, GST, total)
   │
   ├── Apply branded styling
   │
   └── doc.build()
        │
        ▼
   Save to exports/INV-2026-0001.pdf
        │
        ▼
   Show success message with file path
```

### 2.5 Time Tracking Flow

```
Time Log Page
   │
   │ User selects project from dropdown
   │ User types description (optional)
   ▼
   ┌─────────────────────────┐
   │  Click "▶ Start"        │
   ▼
TimeTracker.start()
   │
   │ Records start_time = now()
   │ Sets _active_session
   ▼
QTimer starts (ticks every 1s)
   │
   │ UI shows: 00:00:01, 00:00:02, ...
   │
   │ (User works on project)
   │
   ▼
   ┌─────────────────────────┐
   │  Click "⏹ Stop"         │
   ▼
TimeTracker.stop()
   │
   ├── Compute duration
   │   (now - start_time)
   │
   └── INSERT INTO time_logs
        │
        ▼
   Show "Logged X.XX hours" message
   Reset timer display
   Refresh log table
```

## 3. AI / Intelligence Flows

### 3.1 Contract Risk Analysis Flow (WOW)

```
Contracts Page
   │
   │ User has a contract PDF from a client
   ▼
   ┌─────────────────────────┐
   │ Click "📄 Upload PDF"   │
   ▼
QFileDialog opens
   │
   │ User picks PDF file
   ▼
ContractParser.extract_text()
   │
   │ pdfplumber reads each page
   │ Concatenates all text
   ▼
Text appears in QTextEdit
   │
   ▼
User fills:
   - Project (dropdown)
   - Hourly rate
   - Revision rounds
   - Timeline days
   - Project type
   │
   ▼
   ┌─────────────────────────┐
   │ Click "🔍 Analyze Risk" │
   ▼
RiskAnalyzer.full_analysis()
   │
   ├── analyze_rate(rate, type)
   │   → score 0-25, message
   │
   ├── analyze_revisions(rounds)
   │   → score 0-25, message
   │
   ├── analyze_timeline(days)
   │   → score 0-25, message
   │
   └── scan_text(contract_text)
       │
       │ For each regex pattern:
       │   if match → add finding
       │
       ▼
   total_score = sum(all scores)
       │
       ▼
   risk_level =
       HIGH   if score >= 50
       MEDIUM if score >= 25
       LOW    otherwise
       │
       ▼
   Return findings list
       │
       ▼
   UI Updates:
     - Color-coded risk label
     - Progress bar fills to score
     - Findings table populated
       │
       ▼
   ContractRepository.add()
   (persist analysis to DB)
```

### 3.2 NLP Clause Classifier Flow (Optional Deep Dive)

```
Contract text extracted
   │
   ▼
ClauseClassifier.classify_contract()
   │
   ├── _split_into_clauses(text)
   │   - Split on "1.", "2)", "•", or sentence boundaries
   │   - Filter clauses < 20 chars
   │
   └── For each clause:
       │
       │ classify_clause(text)
       │   │
       │   ├── embedder.encode(text)
       │   │   → 384-dim vector
       │   │
       │   ├── classifier.predict_proba(embedding)
       │   │   → probability per category
       │   │
       │   └── Return:
       │       {category, confidence, text}
       │
       ▼
   List of classified clauses
       │
       ▼
   Categories highlighted in UI:
     - ip_transfer    → red (risky)
     - payment_terms  → yellow (caution)
     - termination    → yellow
     - liability      → yellow
     - revisions      → orange
     - safe           → green
```

### 3.3 Smart Pricing Advisor Flow

```
AI Analytics Page → Smart Pricing tab
   │
   │ User fills:
   │   - Project type
   │   - Estimated hours
   │   - Description (optional)
   │   - Revision rounds
   │
   ▼
   ┌──────────────────────────┐
   │ Click "Get Price Sugg." │
   ▼
PricingAdvisor.suggest_price()
   │
   ├── base_rate = MARKET_RATES[type]
   │
   ├── complexity_mult = analyze description
   │   keywords (urgent, complex, simple, etc.)
   │
   ├── revision_mult = 1 + (rounds-2) × 0.08
   │
   ├── historical_rate = query own DB
   │   if data: blend 60% market + 40% historical
   │
   ├── adjusted_rate = effective × complexity × revision
   │
   ├── base_price = adjusted_rate × hours
   │
   └── Return:
       low  = base × 0.85
       mid  = base
       high = base × 1.20
       reasoning list
       │
       ▼
   UI displays:
     "Suggested Range:
       Low: ₹2,500 | Mid: ₹3,000 | High: ₹3,600
      Reasoning:
       - Market rate Design: ₹600/hr
       - Your historical: ₹550/hr
       - Complexity: 1.2× (urgent)"
```

### 3.4 Payment Delay Predictor Flow

```
AI Analytics → Payment Predictor tab
   │
   │ User fills invoice details
   ▼
   ┌──────────────────────────┐
   │ Click "Predict Timing"  │
   ▼
PaymentPredictor.predict()
   │
   ├── If model not trained:
   │   _load_training_data()
   │   if rows < 5: return "unknown"
   │   else: train()
   │
   ├── Build feature vector:
   │   [amount, days_to_due, type_encoded]
   │
   ├── model.predict_proba(X)
   │   → [p_on_time, p_late, p_very_late]
   │
   └── Return prediction with highest probability
        │
        ▼
   UI displays:
     "On Time" (green) — 73% confidence
     Probabilities:
        On Time: 73%  |  Late: 22%  |  Very Late: 5%
```

### 3.5 Income Forecast Flow

```
AI Analytics → Income Forecast tab
   │
   ▼
   ┌──────────────────────────┐
   │ Click "Generate Forecast"│
   ▼
IncomeForecaster.forecast()
   │
   ├── _get_monthly_income()
   │   Query paid invoices
   │   Group by month
   │
   ├── If < 3 months: return "insufficient_data"
   │
   ├── If >= 12 months: use ARIMA(1,1,1)
   │
   └── Else: weighted moving average
        │
        ▼
   UI displays:
     "Method: ARIMA
      Forecast:
        2026-06: ₹45,000
        2026-07: ₹52,000
        2026-08: ₹48,000"
```

## 4. Cross-Cutting Flows

### 4.1 Page Switching

```
User clicks sidebar button
   │
   ▼
Sidebar.page_changed signal emitted
   │
   ▼
MainWindow._switch_page(page_id)
   │
   ├── stack.setCurrentWidget(page)
   │
   └── If page has refresh(): call it
        │
        ▼
   Page reloads its data from DB
   Tables / cards update
```

### 4.2 First-Run Database Initialization

```
main() called
   │
   ▼
Database() created with path
   │
   ▼
Database.initialize()
   │
   ├── Read schema.sql
   │
   ├── conn.executescript(schema)
   │   - Creates all tables IF NOT EXISTS
   │   - Sets foreign_keys = ON
   │
   └── Close connection
        │
        ▼
   data/solodash.db now exists
```

### 4.3 ML Model Training Flow

```
User runs:
   python scripts/train_clause_model.py
   │
   ▼
Loads TRAINING_DATA list
   (texts + labels, 30+ examples)
   │
   ▼
ClauseClassifier()
   │
   ├── If first run:
   │   Downloads sentence-transformer model
   │   (~80MB, one-time)
   │
   └── Lazy-load embedder
        │
        ▼
   embedder.encode(texts)
   → matrix of (N, 384) embeddings
        │
        ▼
   LabelEncoder fits on labels
   LogisticRegression.fit(X, y)
        │
        ▼
   Save to:
     - app/ml/models/clause_classifier.pkl
     - app/ml/models/clause_encoder.pkl
        │
        ▼
   Print accuracy + sample predictions
```

## 5. Error and Edge Case Flows

### 5.1 Empty Database States

```
User opens analytics
   │
   ▼
ML module check:
   │
   ├── No paid invoices?
   │   → "Need at least 5 paid invoices to predict."
   │
   ├── No projects?
   │   → "Add projects first."
   │
   └── Insufficient data for ARIMA?
       → Fall back to moving average
```

### 5.2 PDF Parsing Failures

```
User uploads non-PDF or corrupt file
   │
   ▼
ContractParser.extract_text()
   │
   ├── pdfplumber raises exception
   │
   └── try/except shows:
       QMessageBox: "Could not read PDF: {error}"
```

### 5.3 Cascade Delete Behavior

```
User deletes a client
   │
   ▼
ClientRepository.delete()
   │
   │ DELETE FROM clients WHERE id = ?
   ▼
SQLite enforces FK CASCADE:
   │
   ├── Related projects deleted
   │
   ├── Their invoices deleted
   │
   ├── Time logs deleted
   │
   ├── Tasks deleted
   │
   └── Contracts deleted
        │
        ▼
   Confirm dialog shown before delete
   "Delete this client and all related data?"
```

## 6. Background / Async Considerations

Most operations are synchronous and fast (< 1s). Long operations:

| Operation | Duration | Strategy |
|-----------|----------|----------|
| First sentence-transformer load | 5–10s | Lazy load on first use, show "Loading..." |
| Initial NLP model download | 30s–2min | One-time, separate training script |
| ARIMA fit on large series | 1–3s | Synchronous (acceptable) |
| PDF generation | 1–3s | Synchronous |
| PDF text extraction (large files) | 1–5s | Synchronous; consider QThread for V2 |

For V1, keep all operations synchronous. Only move to threading if user complaints arise.
