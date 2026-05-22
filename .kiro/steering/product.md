# SmartDesk — Product Overview

SmartDesk is an offline desktop application for freelance creative professionals. It manages clients, projects, invoices, time tracking, contracts, and provides AI-powered business insights.

## Target User

Indian freelance creatives (designers, video editors, writers, musicians, developers). The app is tailored for the Indian market with INR currency, GST tax calculation, and UPI QR code payment support.

## Key Capabilities

- **Client Management** — CRUD, search, contact details
- **Project Tracking** — Status lifecycle (Not Started → In Progress → Completed), budgets, deadlines
- **Invoicing** — Auto-numbered invoices with 18% GST, PDF export, payment tracking
- **Time Tracking** — Live timer and manual entry per project
- **Contract Analysis** — PDF upload, clause classification via NLP, risk scoring
- **Predictive Analytics** — Payment delay prediction, income forecasting (ARIMA), smart pricing advice

## Business Rules

- GST rate is fixed at 18%
- Invoice numbers follow the format `INV-YYYY-NNNN`
- Currency symbol is ₹ (Indian Rupee)
- All data is stored locally (offline-first, no cloud dependency)
- ML features degrade gracefully when models are unavailable
