# Backend Schema Document
## SoloDash — Freelancer Management System

---

## 1. Database Overview

| Property | Value |
|----------|-------|
| Engine | SQLite 3 (stdlib) |
| File | `data/solodash.db` |
| Encoding | UTF-8 |
| Foreign Keys | Enforced (`PRAGMA foreign_keys = ON`) |
| Journal Mode | WAL (default SQLite) |
| Max Expected Size | < 50 MB for 5 years of use |

## 2. Entity-Relationship Diagram (ERD)

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────────┐
│   clients    │       │    projects      │       │    invoices      │
├──────────────┤       ├──────────────────┤       ├──────────────────┤
│ PK id        │──┐    │ PK id            │──┐    │ PK id            │
│    name      │  │    │ FK client_id ────│──┘    │ FK project_id ───│──┐
│    email     │  │    │    name          │       │    invoice_number│  │
│    phone     │  └───▶│    type          │       │    amount        │  │
│    address   │       │    description   │       │    tax           │  │
│    company   │       │    status        │       │    total         │  │
│    notes     │       │    deadline      │       │    date_issued   │  │
│    created   │       │    budget        │       │    due_date      │  │
└──────────────┘       │    created       │       │    status        │  │
                       └──────────────────┘       │    notes         │  │
                              │                   └──────────────────┘  │
                              │                                         │
              ┌───────────────┼───────────────┐                         │
              │               │               │                         │
              ▼               ▼               ▼                         ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐ ┌──────────────────┐
│   time_logs      │ │    tasks     │ │   contracts      │ │    payments      │
├──────────────────┤ ├──────────────┤ ├──────────────────┤ ├──────────────────┤
│ PK id            │ │ PK id        │ │ PK id            │ │ PK id            │
│ FK project_id    │ │ FK project_id│ │ FK project_id    │ │ FK invoice_id    │
│    start_time    │ │    title     │ │    contract_text │ │    amount_paid   │
│    end_time      │ │    due_date  │ │    hourly_rate   │ │    payment_date  │
│    duration_hours│ │    completed │ │    revision_rnd  │ │    payment_mode  │
│    description   │ │    created   │ │    timeline_days │ │    reference     │
└──────────────────┘ └──────────────┘ │    risk_score    │ └──────────────────┘
                                      │    risk_level    │
                                      │    findings      │
                                      │    analyzed_date │
                                      └──────────────────┘

                       ┌──────────────────┐
                       │  ml_predictions  │
                       ├──────────────────┤
                       │ PK id            │
                       │ FK project_id    │  (nullable)
                       │    pred_type     │
                       │    input_data    │
                       │    result        │
                       │    confidence    │
                       │    model_version │
                       │    created       │
                       └──────────────────┘
```

## 3. Table Definitions

### 3.1 `clients`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK AUTOINCREMENT | Unique client ID |
| name | TEXT | NOT NULL | Full name |
| email | TEXT | UNIQUE | Email address |
| phone | TEXT | — | Phone number |
| address | TEXT | — | Mailing address |
| company | TEXT | — | Company / brand name |
| notes | TEXT | — | Free-form notes |
| created_date | TEXT | DEFAULT DATE('now') | ISO date of creation |

**Indexes:**
- `idx_clients_name` on `name` (for search)
- `idx_clients_email` on `email` (unique constraint)

**Relationships:**
- One client → many projects (1:N)

---

### 3.2 `projects`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK AUTOINCREMENT | Unique project ID |
| client_id | INTEGER | NOT NULL, FK → clients(id) ON DELETE CASCADE | Owning client |
| name | TEXT | NOT NULL | Project title |
| type | TEXT | — | Category (Design, Video, Writing, Music, Development, General) |
| description | TEXT | — | Brief / scope |
| status | TEXT | DEFAULT 'Not Started' | Lifecycle state |
| deadline | TEXT | — | ISO date |
| budget | REAL | — | Agreed budget in INR |
| created_date | TEXT | DEFAULT DATE('now') | ISO date of creation |

**Valid `status` values:**
- `Not Started`
- `In Progress`
- `On Hold`
- `Completed`
- `Cancelled`

**Valid `type` values:**
- `Design`, `Video`, `Writing`, `Music`, `Development`, `General`

**Indexes:**
- `idx_projects_client` on `client_id`
- `idx_projects_status` on `status`

**Relationships:**
- One project → many invoices (1:N)
- One project → many time_logs (1:N)
- One project → many tasks (1:N)
- One project → many contracts (1:N)

---

### 3.3 `invoices`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK AUTOINCREMENT | Unique invoice ID |
| project_id | INTEGER | NOT NULL, FK → projects(id) ON DELETE CASCADE | Related project |
| invoice_number | TEXT | UNIQUE NOT NULL | Format: INV-YYYY-NNNN |
| amount | REAL | NOT NULL | Base amount before tax |
| tax | REAL | DEFAULT 0 | GST amount (18% of amount) |
| total | REAL | NOT NULL | amount + tax |
| date_issued | TEXT | DEFAULT DATE('now') | Issue date |
| due_date | TEXT | — | Payment due date |
| status | TEXT | DEFAULT 'Unpaid' | Payment status |
| notes | TEXT | — | Additional notes |

**Valid `status` values:**
- `Unpaid`
- `Paid`
- `Cancelled`

**Derived status (computed in app, not stored):**
- `Overdue` = Unpaid AND due_date < today

**Indexes:**
- `idx_invoices_project` on `project_id`
- `idx_invoices_status` on `status`
- `idx_invoices_due` on `due_date`

**Relationships:**
- One invoice → many payments (1:N)

---

### 3.4 `payments`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK AUTOINCREMENT | Unique payment ID |
| invoice_id | INTEGER | NOT NULL, FK → invoices(id) ON DELETE CASCADE | Related invoice |
| amount_paid | REAL | NOT NULL | Amount received |
| payment_date | TEXT | DEFAULT DATE('now') | When payment was received |
| payment_mode | TEXT | — | UPI / Bank Transfer / Cash / Cheque |
| reference | TEXT | — | Transaction ID or reference |

**Indexes:**
- `idx_payments_invoice` on `invoice_id`

**Notes:**
- Supports partial payments (multiple payments per invoice)
- Invoice marked "Paid" when SUM(amount_paid) >= invoice.total

---

### 3.5 `time_logs`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK AUTOINCREMENT | Unique log ID |
| project_id | INTEGER | NOT NULL, FK → projects(id) ON DELETE CASCADE | Related project |
| start_time | TEXT | NOT NULL | ISO datetime |
| end_time | TEXT | — | ISO datetime (null if still running) |
| duration_hours | REAL | — | Computed: (end - start) in hours |
| description | TEXT | — | What was worked on |

**Indexes:**
- `idx_timelogs_project` on `project_id`
- `idx_timelogs_start` on `start_time`

**Computed Values (in app):**
- Effective hourly rate = invoice.total / SUM(duration_hours) for project
- Total hours per project = SUM(duration_hours) WHERE project_id = ?

---

### 3.6 `tasks`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK AUTOINCREMENT | Unique task ID |
| project_id | INTEGER | NOT NULL, FK → projects(id) ON DELETE CASCADE | Related project |
| title | TEXT | NOT NULL | Task description |
| due_date | TEXT | — | ISO date |
| is_completed | INTEGER | DEFAULT 0 | Boolean (0 = pending, 1 = done) |
| created_date | TEXT | DEFAULT DATE('now') | ISO date of creation |

**Indexes:**
- `idx_tasks_project` on `project_id`

---

### 3.7 `contracts`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK AUTOINCREMENT | Unique analysis ID |
| project_id | INTEGER | NOT NULL, FK → projects(id) ON DELETE CASCADE | Related project |
| contract_text | TEXT | — | Extracted / pasted contract text (max 5000 chars stored) |
| hourly_rate | REAL | — | Rate used in analysis |
| revision_rounds | INTEGER | — | Revisions agreed |
| timeline_days | INTEGER | — | Project timeline |
| risk_score | INTEGER | — | Computed total risk score (0–100+) |
| risk_level | TEXT | — | LOW / MEDIUM / HIGH |
| findings | TEXT | — | JSON array of findings |
| analyzed_date | TEXT | DEFAULT DATETIME('now') | When analysis was run |

**Indexes:**
- `idx_contracts_project` on `project_id`

**Notes:**
- `findings` stored as JSON string: `[{"check": "Rate", "result": "...", "score": 25}, ...]`
- Multiple analyses per project allowed (history)

---

### 3.8 `ml_predictions`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK AUTOINCREMENT | Unique prediction ID |
| project_id | INTEGER | FK → projects(id) ON DELETE SET NULL, nullable | Related project (optional) |
| prediction_type | TEXT | NOT NULL | Type: pricing / payment / forecast / clause |
| input_data | TEXT | — | JSON of input parameters |
| result | TEXT | — | JSON of prediction output |
| confidence | REAL | — | Confidence score (0–100) |
| model_version | TEXT | — | Model version identifier |
| created_date | TEXT | DEFAULT DATETIME('now') | When prediction was made |

**Indexes:**
- `idx_predictions_type` on `prediction_type`
- `idx_predictions_project` on `project_id`

**Notes:**
- Audit trail for all ML predictions
- Useful for evaluating model accuracy over time
- `project_id` is nullable (forecasts aren't project-specific)

---

## 4. Relationships Summary

| Parent | Child | Cardinality | On Delete |
|--------|-------|-------------|-----------|
| clients | projects | 1:N | CASCADE |
| projects | invoices | 1:N | CASCADE |
| projects | time_logs | 1:N | CASCADE |
| projects | tasks | 1:N | CASCADE |
| projects | contracts | 1:N | CASCADE |
| projects | ml_predictions | 1:N | SET NULL |
| invoices | payments | 1:N | CASCADE |

## 5. Common Queries

### 5.1 Dashboard Aggregations

```sql
-- Total earned
SELECT COALESCE(SUM(total), 0) FROM invoices WHERE status = 'Paid';

-- Total pending
SELECT COALESCE(SUM(total), 0) FROM invoices WHERE status = 'Unpaid';

-- Active projects count
SELECT COUNT(*) FROM projects WHERE status = 'In Progress';

-- Overdue invoices
SELECT * FROM invoices
WHERE status = 'Unpaid' AND due_date < DATE('now')
ORDER BY due_date ASC;
```

### 5.2 ML Training Data Queries

```sql
-- Payment predictor training data
SELECT i.total, i.due_date, i.date_issued, p.type, pay.payment_date
FROM invoices i
JOIN projects p ON i.project_id = p.id
JOIN payments pay ON pay.invoice_id = i.id
WHERE i.status = 'Paid';

-- Income forecaster monthly data
SELECT total, date_issued FROM invoices WHERE status = 'Paid' ORDER BY date_issued;

-- Pricing advisor historical rates
SELECT i.total, t.total_hours
FROM invoices i
JOIN projects p ON i.project_id = p.id
LEFT JOIN (
    SELECT project_id, SUM(duration_hours) as total_hours
    FROM time_logs GROUP BY project_id
) t ON p.id = t.project_id
WHERE i.status = 'Paid' AND p.type = ? AND t.total_hours > 0;
```

### 5.3 Reporting Queries

```sql
-- Income by month
SELECT strftime('%Y-%m', date_issued) as month, SUM(total) as income
FROM invoices WHERE status = 'Paid'
GROUP BY month ORDER BY month;

-- Profitability by project type
SELECT p.type, SUM(i.total) as revenue, SUM(t.hours) as hours,
       SUM(i.total) / SUM(t.hours) as effective_rate
FROM projects p
JOIN invoices i ON p.id = i.project_id
JOIN (SELECT project_id, SUM(duration_hours) as hours FROM time_logs GROUP BY project_id) t
  ON p.id = t.project_id
WHERE i.status = 'Paid'
GROUP BY p.type;

-- Top clients by revenue
SELECT c.name, SUM(i.total) as total_revenue, COUNT(DISTINCT p.id) as projects
FROM clients c
JOIN projects p ON c.id = p.client_id
JOIN invoices i ON p.id = i.project_id
WHERE i.status = 'Paid'
GROUP BY c.id ORDER BY total_revenue DESC LIMIT 10;
```

## 6. Data Integrity Rules

| Rule | Enforcement |
|------|-------------|
| Client name required | NOT NULL constraint |
| Client email unique | UNIQUE constraint |
| Invoice number unique | UNIQUE constraint |
| Project must have client | FK NOT NULL |
| Invoice must have project | FK NOT NULL |
| Cascade deletes | ON DELETE CASCADE on all child FKs |
| No orphan predictions | ON DELETE SET NULL (project_id nullable) |
| Foreign keys enforced | PRAGMA foreign_keys = ON per connection |

## 7. Migration Strategy

For V1, schema is created fresh via `schema.sql`. Future versions:

```
data/
  migrations/
    001_initial.sql          ← current schema.sql
    002_add_expenses.sql     ← future: add expenses table
    003_add_tags.sql         ← future: project tags
```

Migration runner (future):
1. Track applied migrations in a `_migrations` table
2. On startup, apply any unapplied migrations in order
3. Never modify existing migration files

## 8. Seed Data Script

For development and ML training, a seed script populates realistic sample data:

```
scripts/
  seed_data.py    ← generates 10 clients, 25 projects, 40 invoices,
                     30 payments, 100 time logs, 15 contracts
```

This ensures:
- Dashboard shows meaningful numbers
- ML models have enough data to train
- Demo during viva is impressive

## 9. Backup & Recovery

| Operation | Method |
|-----------|--------|
| Backup | Copy `data/solodash.db` to external location |
| Restore | Replace `data/solodash.db` with backup copy |
| Export | Future: CSV export of each table |
| Reset | Delete `data/solodash.db`; app recreates on next launch |
