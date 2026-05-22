-- SmartDesk Database Schema
-- All tables use INTEGER PRIMARY KEY AUTOINCREMENT for consistency.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT,
    company TEXT,
    notes TEXT,
    created_date TEXT DEFAULT (DATE('now'))
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT,
    description TEXT,
    status TEXT DEFAULT 'Not Started',
    deadline TEXT,
    budget REAL,
    created_date TEXT DEFAULT (DATE('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    invoice_number TEXT UNIQUE NOT NULL,
    amount REAL NOT NULL,
    tax REAL DEFAULT 0,
    total REAL NOT NULL,
    date_issued TEXT DEFAULT (DATE('now')),
    due_date TEXT,
    status TEXT DEFAULT 'Unpaid',
    notes TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    amount_paid REAL NOT NULL,
    payment_date TEXT DEFAULT (DATE('now')),
    payment_mode TEXT,
    reference TEXT,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS time_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT,
    duration_hours REAL,
    description TEXT,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    due_date TEXT,
    is_completed INTEGER DEFAULT 0,
    created_date TEXT DEFAULT (DATE('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    contract_text TEXT,
    hourly_rate REAL,
    revision_rounds INTEGER,
    timeline_days INTEGER,
    risk_score INTEGER,
    risk_level TEXT,
    findings TEXT,
    analyzed_date TEXT DEFAULT (DATE('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS ml_predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    prediction_type TEXT NOT NULL,
    input_data TEXT,
    result TEXT,
    confidence REAL,
    model_version TEXT,
    created_date TEXT DEFAULT (DATETIME('now')),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- ─── Performance Indexes ─────────────────────────────────────────────────────

-- Projects: filtered by status, joined on client_id
CREATE INDEX IF NOT EXISTS idx_projects_client_id ON projects(client_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);

-- Invoices: filtered by status, due_date, joined on project_id
CREATE INDEX IF NOT EXISTS idx_invoices_project_id ON invoices(project_id);
CREATE INDEX IF NOT EXISTS idx_invoices_status ON invoices(status);
CREATE INDEX IF NOT EXISTS idx_invoices_due_date ON invoices(due_date);

-- Payments: joined on invoice_id
CREATE INDEX IF NOT EXISTS idx_payments_invoice_id ON payments(invoice_id);

-- Time logs: joined on project_id, ordered by start_time
CREATE INDEX IF NOT EXISTS idx_time_logs_project_id ON time_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_time_logs_start_time ON time_logs(start_time);

-- Tasks: filtered by project_id
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);

-- Contracts: joined on project_id
CREATE INDEX IF NOT EXISTS idx_contracts_project_id ON contracts(project_id);

-- Clients: searched by name, email, company
CREATE INDEX IF NOT EXISTS idx_clients_name ON clients(name);
CREATE INDEX IF NOT EXISTS idx_clients_email ON clients(email);
