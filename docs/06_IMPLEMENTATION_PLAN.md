# Implementation Plan
## SoloDash — Freelancer Management System

---

## 1. Overview

| Property | Value |
|----------|-------|
| Duration | 8 weeks (56 days) |
| Developer | 1 (solo) |
| Hours/week | ~25–30 hours |
| Total effort | ~200–240 hours |
| Methodology | Modified Waterfall (sequential phases, iterative within each) |

## 2. Phase Breakdown

```
Week 1─2 ──── PHASE 1: Foundation & Core CRUD
Week 3─4 ──── PHASE 2: Business Logic & PDF
Week 5─6 ──── PHASE 3: Intelligence Layer (ML/AI)
Week 7   ──── PHASE 4: WOW Features & Polish
Week 8   ──── PHASE 5: Packaging, Testing & Documentation
```

---

## 3. PHASE 1: Foundation & Core CRUD (Week 1–2)

### Week 1: Project Setup + Database + Client/Project CRUD

| Day | Task | Deliverable | Hours |
|-----|------|-------------|-------|
| 1 | Set up venv, install deps, verify PySide6 runs | Empty window launches | 3 |
| 2 | Implement Database class + schema.sql | DB creates all 8 tables | 3 |
| 3 | Build repository classes (client, project) | CRUD operations work | 4 |
| 4 | Build MainWindow + Sidebar + page switching | Navigation works | 4 |
| 5 | Build ClientsPage (table + add/edit/delete dialogs) | Full client CRUD | 5 |
| 6 | Build ProjectsPage (table + dialog + status) | Full project CRUD | 5 |
| 7 | Apply dark theme, fix styling issues | App looks professional | 3 |

**Week 1 Milestone:** Can add clients, create projects, navigate between pages.

### Week 2: Invoices + Time Tracking + Dashboard

| Day | Task | Deliverable | Hours |
|-----|------|-------------|-------|
| 8 | Build InvoiceRepository + InvoiceService | Invoice creation logic | 4 |
| 9 | Build InvoicesPage (table + create dialog) | Create/view invoices | 5 |
| 10 | Build TimeLogRepository + TimeTracker service | Timer logic works | 3 |
| 11 | Build TimePage (live timer + manual entry + log table) | Time tracking works | 5 |
| 12 | Build TaskRepository + basic task UI (within projects) | Task checklist | 3 |
| 13 | Build DashboardPage (summary cards + recent projects) | Dashboard shows data | 4 |
| 14 | Integration testing: full flow client → project → invoice | End-to-end works | 3 |

**Week 2 Milestone:** Complete CRUD for all entities. Dashboard shows real data. Timer works.

---

## 4. PHASE 2: Business Logic & PDF (Week 3–4)

### Week 3: PDF Export + Payment Tracking + Polish

| Day | Task | Deliverable | Hours |
|-----|------|-------------|-------|
| 15 | Implement PDFExporter with ReportLab | PDF generates correctly | 4 |
| 16 | Wire PDF export to InvoicesPage button | Click → PDF saved | 3 |
| 17 | Build PaymentRepository + payment recording UI | Record payments | 4 |
| 18 | Invoice status auto-update (mark paid when fully paid) | Status transitions | 3 |
| 19 | Add overdue detection (highlight overdue invoices) | Visual indicators | 3 |
| 20 | UPI QR code generation (utils/upi_qr.py) | QR image generates | 3 |
| 21 | Embed QR code in PDF invoice (optional section) | PDF has QR code | 3 |

**Week 3 Milestone:** Professional PDF invoices with UPI QR. Payment tracking complete.

### Week 4: Risk Analyzer + Contract Page

| Day | Task | Deliverable | Hours |
|-----|------|-------------|-------|
| 22 | Implement RiskAnalyzer (rule-based scoring) | Risk analysis works | 4 |
| 23 | Implement ContractParser (pdfplumber text extraction) | PDF → text works | 3 |
| 24 | Build ContractsPage UI (upload + form + results) | Full contract page | 5 |
| 25 | Wire analyzer to page, display findings table | End-to-end flow | 4 |
| 26 | ContractRepository: save analysis results to DB | Persist analyses | 3 |
| 27 | Add more regex patterns, test with sample contracts | Better detection | 3 |
| 28 | Bug fixes, UI alignment, edge cases | Stable build | 3 |

**Week 4 Milestone:** Contract upload → text extraction → risk analysis → results displayed. Saved to DB.

---

## 5. PHASE 3: Intelligence Layer (Week 5–6)

### Week 5: NLP Clause Classifier + Payment Predictor

| Day | Task | Deliverable | Hours |
|-----|------|-------------|-------|
| 29 | Install sentence-transformers, test embedding | Model loads | 3 |
| 30 | Expand training data (50+ examples across 6 categories) | Rich dataset | 4 |
| 31 | Implement ClauseClassifier.train() + save model | Model trains | 4 |
| 32 | Implement ClauseClassifier.classify_contract() | Clauses classified | 4 |
| 33 | Wire clause results into ContractsPage (per-clause display) | UI shows categories | 4 |
| 34 | Implement PaymentPredictor (train + predict) | Predictions work | 4 |
| 35 | Create seed_data.py script (populate DB for ML training) | 40+ sample invoices | 4 |

**Week 5 Milestone:** NLP classifier works end-to-end. Payment predictor trained on seed data.

### Week 6: Income Forecaster + Pricing Advisor + Analytics Page

| Day | Task | Deliverable | Hours |
|-----|------|-------------|-------|
| 36 | Implement IncomeForecaster (ARIMA + fallback) | Forecast generates | 4 |
| 37 | Implement PricingAdvisor (hybrid logic) | Price suggestions work | 4 |
| 38 | Build AnalyticsPage — Smart Pricing tab | Pricing UI complete | 4 |
| 39 | Build AnalyticsPage — Payment Predictor tab | Prediction UI complete | 4 |
| 40 | Build AnalyticsPage — Income Forecast tab | Forecast UI complete | 4 |
| 41 | Add Matplotlib charts to dashboard (income trend) | Chart renders | 4 |
| 42 | Integration test: all ML features with seed data | Everything works | 3 |

**Week 6 Milestone:** All 5 ML/AI features functional. Analytics page complete with 3 tabs.

---

## 6. PHASE 4: WOW Features & Polish (Week 7)

| Day | Task | Deliverable | Hours |
|-----|------|-------------|-------|
| 43 | Add profitability-by-type chart (Matplotlib) | Bar chart on dashboard | 3 |
| 44 | Add top-clients chart | Horizontal bar chart | 3 |
| 45 | Empty state messages for all pages | Better UX | 2 |
| 46 | Form validation (required fields, email format) | No crashes on bad input | 3 |
| 47 | Error handling (try/except on all DB operations) | Graceful failures | 3 |
| 48 | UI polish: alignment, spacing, scroll behavior | Professional look | 4 |
| 49 | Performance: lazy-load ML models, optimize queries | Fast startup | 3 |

**Week 7 Milestone:** App is polished, handles errors gracefully, looks professional.

---

## 7. PHASE 5: Packaging, Testing & Documentation (Week 8)

| Day | Task | Deliverable | Hours |
|-----|------|-------------|-------|
| 50 | Write unit tests for repositories (pytest) | 10+ tests pass | 4 |
| 51 | Write unit tests for services + ML modules | 15+ tests pass | 4 |
| 52 | PyInstaller build: create .exe | Standalone executable | 4 |
| 53 | Test .exe on clean Windows machine | Works without Python | 3 |
| 54 | Take screenshots for report (all 7 pages) | 10+ screenshots | 2 |
| 55 | Write final report sections (methodology, results, discussion) | Report draft | 5 |
| 56 | Prepare viva demo script + backup plan | Ready for defense | 3 |

**Week 8 Milestone:** Packaged .exe, test suite, screenshots, report complete.

---

## 8. Task Dependencies

```
                    ┌─────────────┐
                    │ DB + Schema │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Clients  │ │ Projects │ │  Theme   │
        └────┬─────┘ └────┬─────┘ └──────────┘
             │             │
             └──────┬──────┘
                    ▼
        ┌───────────────────────┐
        │ Invoices + Payments   │
        └───────────┬───────────┘
                    │
        ┌───────────┼───────────────┐
        ▼           ▼               ▼
  ┌──────────┐ ┌──────────┐  ┌──────────────┐
  │ PDF      │ │ Time     │  │ Risk         │
  │ Export   │ │ Tracking │  │ Analyzer     │
  └──────────┘ └──────────┘  └──────┬───────┘
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
            ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
            │ Clause       │ │ Payment      │ │ Income       │
            │ Classifier   │ │ Predictor    │ │ Forecaster   │
            └──────────────┘ └──────────────┘ └──────────────┘
                    │                │                │
                    └────────────────┼────────────────┘
                                     ▼
                            ┌────────────────┐
                            │ Analytics Page │
                            └────────────────┘
                                     │
                                     ▼
                            ┌────────────────┐
                            │ Polish + Build │
                            └────────────────┘
```

## 9. Risk Mitigation Plan

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| sentence-transformers too slow to load | Medium | Medium | Lazy-load; show "Loading model..." spinner |
| ML accuracy poor on small data | High | Medium | Use seed data; frame as "advisory" not "definitive" |
| PyInstaller build fails | Medium | High | Test build at Week 6 (not Week 8); have fallback plan |
| PySide6 styling inconsistencies | Low | Low | Test on Windows 10 + 11 early |
| Scope creep (adding features) | High | High | Feature freeze after Week 6; only bug fixes after |
| PDF generation edge cases | Low | Low | Test with long names, special characters |
| pdfplumber fails on some PDFs | Medium | Low | Show error message; allow manual text paste |

## 10. Definition of Done (per feature)

A feature is "done" when:
- [ ] Code written and follows project conventions
- [ ] No crashes on normal use
- [ ] Edge cases handled (empty inputs, missing data)
- [ ] UI displays correctly in dark theme
- [ ] Data persists after app restart
- [ ] Feature accessible from sidebar navigation

## 11. Tools & Environment

| Tool | Purpose |
|------|---------|
| VS Code / Kiro | IDE |
| Git | Version control |
| Python 3.11 | Runtime |
| venv | Virtual environment |
| pytest | Testing |
| PyInstaller | Packaging |
| SQLite Browser | DB inspection during dev |

## 12. Git Strategy

```
main          ← stable, always runs
├── feature/clients-crud
├── feature/invoices-pdf
├── feature/ml-clause-classifier
├── feature/analytics-page
└── feature/polish-packaging
```

- Commit after each completed task (daily)
- Merge to main after each phase milestone
- Tag releases: `v0.1-alpha`, `v0.5-beta`, `v1.0-final`

## 13. Viva Demo Script (5 minutes)

1. **Open app** — show dark dashboard with summary cards (30s)
2. **Add a client** — demonstrate CRUD (30s)
3. **Create a project** — link to client, set deadline (30s)
4. **Generate invoice** — show auto GST, export PDF, open PDF file (45s)
5. **Start timer** — show live tracking, stop, log appears (30s)
6. **Upload contract PDF** — extract text, run analysis, show risk score (60s) ← WOW moment
7. **AI Analytics** — show pricing suggestion with reasoning (30s)
8. **Income forecast** — show 3-month prediction (30s)
9. **Wrap up** — mention tech stack, architecture, future scope (15s)

## 14. Deliverables Checklist

| # | Deliverable | Format | Status |
|---|-------------|--------|--------|
| 1 | Working desktop application | .exe + source | ⬜ |
| 2 | Source code (GitHub repository) | Git repo | ⬜ |
| 3 | Project report (synopsis + full) | PDF / Word | ⬜ |
| 4 | Screenshots (all pages) | PNG files | ⬜ |
| 5 | Database schema diagram | In report | ⬜ |
| 6 | DFD (Level 0, 1, 2) | In report | ⬜ |
| 7 | Test report | In report | ⬜ |
| 8 | User manual | In report | ⬜ |
| 9 | Presentation slides | PPT | ⬜ |
| 10 | Demo video (optional) | MP4, 3–5 min | ⬜ |

## 15. Weekly Checkpoints

| Week | Checkpoint Question | Pass Criteria |
|------|---------------------|---------------|
| 1 | Can I add a client and see it in the table? | Yes |
| 2 | Can I create an invoice and see it on dashboard? | Yes |
| 3 | Can I export a PDF invoice and open it? | Yes |
| 4 | Can I upload a contract and see risk analysis? | Yes |
| 5 | Does the clause classifier produce results? | Yes |
| 6 | Do all 3 analytics tabs show predictions? | Yes |
| 7 | Does the app handle errors without crashing? | Yes |
| 8 | Does the .exe run on a clean machine? | Yes |
