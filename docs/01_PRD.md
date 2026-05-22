# Product Requirements Document (PRD)
## SoloDash — Freelancer Management System with Predictive Analytics

| Field | Value |
|-------|-------|
| Document Version | 1.0 |
| Author | Nirmal Kumar Mahto |
| Date | May 2026 |
| Project Type | BCA Final Year Project |
| Supervisor | Ms. Anu Thakur |

---

## 1. Executive Summary

SoloDash is an offline desktop application that centralizes business operations for freelance creative professionals — managing clients, projects, invoices, time tracking, and contracts. It embeds an intelligence layer powered by local machine learning models that provides pricing suggestions, payment delay prediction, income forecasting, and AI-powered contract risk analysis.

The application targets the Indian freelance market, with INR-first pricing, GST-compliant invoicing, and UPI payment integration.

## 2. Problem Statement

Freelance creative professionals (designers, writers, video editors, music producers) currently manage their business using fragmented tools — spreadsheets for finances, sticky notes for deadlines, and physical notebooks for client details. This causes:

- Lost or delayed payments due to lack of tracking
- Underpricing because of no historical reference
- Signing unfavorable contracts without proper risk evaluation
- Hours wasted on administrative work instead of creative output
- No visibility into profitability or financial health

Existing tools (FreshBooks, Bonsai, Wave) are subscription-based, cloud-only, and not optimized for the Indian market or single-user creative workflows.

## 3. Target Users

### Primary Persona: The Solo Freelance Creative
- **Profile:** Indian freelancer aged 22–35, working in design / video / writing / music
- **Income:** ₹3–15 lakh/year, 5–20 active clients at any time
- **Tech Comfort:** Moderate (uses smartphones daily, basic computer skills)
- **Pain Points:** Tracks finances manually, undercharges, misses payment follow-ups
- **Goals:** Spend less time on admin, charge fairly, get paid on time

### Secondary Personas
- Final-year design / arts students transitioning into freelancing
- Side-hustling professionals managing 2–5 clients alongside a day job

## 4. Goals and Success Metrics

| Goal | Metric | Target |
|------|--------|--------|
| Reduce admin time | Time to create an invoice | < 30 seconds |
| Improve pricing accuracy | Pricing advisor adoption | 70% of new projects use suggestion |
| Catch risky contracts | Contracts flagged before signing | 90% identification rate |
| Predict payment delays | Payment predictor accuracy | 75%+ on test data |
| User satisfaction | Survey rating from 8 freelancers | Average 4/5 or higher |

## 5. Functional Requirements

### 5.1 Must-Have (P0) — 8 weeks

#### FR1. Client Management
- Add new clients with name, email, phone, address, company, notes
- Edit existing client details
- Delete clients (cascades to related projects)
- Search clients by name, email, or company
- View list of all clients with pagination support

#### FR2. Project Management
- Create projects linked to existing clients
- Set project type (Design, Video, Writing, Music, Development, General)
- Track status across lifecycle (Not Started → In Progress → On Hold → Completed → Cancelled)
- Set deadlines and budgets
- Edit and delete projects

#### FR3. Invoice Generation
- Auto-generate invoice numbers (format: INV-YYYY-NNNN)
- Create invoices linked to projects
- Auto-calculate GST at 18%
- Mark invoices as Paid, Unpaid, or Cancelled
- Set custom due dates (default 14 days)

#### FR4. PDF Invoice Export
- Generate professional A4 PDF invoices
- Include client details, project name, line items, GST, total
- Save to `exports/` folder with invoice number as filename
- Render in under 3 seconds

#### FR5. Time Tracking
- Live timer with start/stop for active projects
- Manual time entry (specify hours retroactively)
- View time logs grouped by project
- Calculate total hours per project

#### FR6. Dashboard
- Display total earnings, pending amount, active projects, total clients
- Show recent projects table (latest 10)
- Refresh data when navigating to dashboard

### 5.2 Should-Have (P1) — 8 weeks (intelligence layer)

#### FR7. Contract Risk Analyzer
- Score contracts based on hourly rate vs. market benchmarks
- Score based on revision rounds and timeline tightness
- Scan contract text for risky clauses (regex-based fallback)
- Classify risk as LOW / MEDIUM / HIGH
- Display findings with individual scores

#### FR8. Contract PDF Upload (WOW Feature)
- Upload a PDF contract from disk
- Extract text using pdfplumber
- Auto-populate the contract analysis form
- Run analysis on extracted text

#### FR9. NLP Clause Classifier (WOW Feature)
- Train classifier on labeled contract clauses (30+ examples)
- Categorize clauses: ip_transfer, payment_terms, termination, liability, revisions, safe
- Use sentence-transformers for embeddings + logistic regression
- Display per-clause classification with confidence score

#### FR10. Smart Pricing Advisor
- Suggest price range (low/mid/high) for new projects
- Factor in: project type, estimated hours, complexity keywords, revision rounds
- Blend market rates with user's historical data when available
- Show reasoning for the suggestion

#### FR11. Payment Delay Predictor
- Train Random Forest classifier on user's payment history
- Predict invoice timing: on_time / late / very_late
- Display confidence scores and class probabilities
- Trigger automatically when creating new invoices

#### FR12. Income Forecaster
- Forecast next 3 months of income
- Use ARIMA when 12+ months of data available
- Fall back to weighted moving average otherwise
- Display historical and predicted values

### 5.3 Nice-to-Have (P2) — Stretch goals

- UPI QR code on invoice PDFs
- Email invoice directly via SMTP
- Receipt OCR using Tesseract
- Charts on dashboard (income trend, profitability by project type)
- Auto follow-up email drafts for overdue invoices

### 5.4 Out of Scope

- Multi-user support
- Cloud sync / online backup
- Mobile app
- Multi-currency support
- Tax filing / ITR integration
- Real-time collaboration

## 6. Non-Functional Requirements

| Category | Requirement |
|----------|-------------|
| **Performance** | App startup < 3 seconds, page navigation < 200ms |
| **Reliability** | No data loss on crash; SQLite ACID guarantees |
| **Usability** | Single-window app, no learning curve for basic CRUD |
| **Privacy** | Fully offline, no telemetry, no external API calls |
| **Compatibility** | Windows 10/11, Python 3.11+ |
| **Storage** | < 500MB installer including ML models |
| **Maintainability** | Layered architecture, < 200 LOC per module |

## 7. Assumptions and Constraints

### Assumptions
- Users have basic computer literacy
- Users will manually enter all client/project data initially
- Internet only required for one-time download of sentence-transformer model

### Constraints
- 2-month development timeline (single developer)
- BCA-level technical complexity
- Must demonstrate core CS principles: databases, ML, NLP, software architecture
- Must work offline once installed

## 8. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ML accuracy poor due to small datasets | High | Start with rule-based, layer ML on top; use synthetic seed data |
| sentence-transformers too heavy for installer | Medium | Make NLP feature optional; lazy-load model |
| User study with 8 freelancers may not happen | Medium | Build a sample dataset / case study as backup |
| Scope creep | High | Lock features at end of Week 2; freeze additions |

## 9. Release Plan

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| Alpha | End of Week 4 | Core CRUD complete; PDF export working |
| Beta | End of Week 6 | All ML features integrated |
| RC | End of Week 7 | Polish, bug fixes, packaging |
| Final | End of Week 8 | .exe installer, documentation, viva-ready |
