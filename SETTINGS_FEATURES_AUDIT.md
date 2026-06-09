# SmartDesk Settings Features Audit Report

**Date:** June 4, 2026  
**Purpose:** Identify which Settings features have working backend logic vs UI-only placeholders

---

## 🎯 Executive Summary

**Total Features Audited:** 11  
**✅ Fully Implemented:** 6  
**🟡 Partially Implemented:** 2  
**❌ Missing / UI Only:** 3

---

## 📊 Detailed Feature Status

### ✅ IMPLEMENTED (Working Backend Logic)

#### 1. Profile & Account Settings
**Status:** ✅ **IMPLEMENTED**  
**Backend:** `app/core/settings_service.py` + `app/data/repositories/settings_repo.py`  
**Database:** `app_settings` table (created in migration 001)  
**Working Features:**
- Business name, email, phone ✅
- Address, GSTIN ✅
- Logo upload & storage ✅
- UPI ID & display name ✅
- All fields save to database via `BusinessProfile` dataclass
- Data persists across sessions

**Evidence:**
```python
# settings_service.py lines 59-92
def get_business(self) -> BusinessProfile:
    return BusinessProfile(
        name=self.repo.get(KEY_BUSINESS_NAME, "") or "",
        email=self.repo.get(KEY_BUSINESS_EMAIL, "") or "",
        ...
    )

def save_business(self, profile: BusinessProfile) -> None:
    mapping = {KEY_BUSINESS_NAME: profile.name, ...}
    for key, value in mapping.items():
        self.repo.set(key, value or "")
```

**UI Location:** Settings → Business Profile tab

---


#### 2. Workspace Settings (Preferences)
**Status:** ✅ **IMPLEMENTED (Partial)**  
**Backend:** `app/core/settings_service.py`  
**Database:** `app_settings` table  
**Working Features:**
- Default payment due days ✅
- GST rate (backend exists, no UI yet) ✅
- Saves to database

**Missing from UI:**
- ❌ Workspace name
- ❌ Currency selection
- ❌ Timezone
- ❌ Date format

**Evidence:**
```python
# settings_service.py lines 95-110
def get_default_due_days(self, fallback: int = 14) -> int:
    raw = self.repo.get(KEY_DEFAULT_DUE_DAYS)
    try:
        return int(raw) if raw else fallback
    except (TypeError, ValueError):
        return fallback

def set_default_due_days(self, days: int) -> None:
    self.repo.set(KEY_DEFAULT_DUE_DAYS, str(int(days)))
```

**UI Location:** Settings → Preferences tab (minimal UI)

---

#### 3. Email (SMTP) Configuration
**Status:** ✅ **IMPLEMENTED**  
**Backend:** `app/core/email_service.py`  
**Database:** `app_settings` table  
**Working Features:**
- SMTP host, port, username, password ✅
- From address ✅
- TLS toggle ✅
- Save/load configuration ✅
- Test email functionality ✅
- Used for sending invoices and overdue reminders ✅

**Evidence:**
```python
# email_service.py lines 66-75
def save_config(self, config: SMTPConfig) -> None:
    self.repo.set(KEY_SMTP_HOST, config.host)
    self.repo.set(KEY_SMTP_PORT, str(config.port))
    self.repo.set(KEY_SMTP_USERNAME, config.username)
    self.repo.set(KEY_SMTP_PASSWORD, config.password)
    self.repo.set(KEY_SMTP_FROM, config.from_addr)
    self.repo.set(KEY_SMTP_USE_TLS, "1" if config.use_tls else "0")
```

**UI Location:** Settings → Email (SMTP) tab

---


#### 4. Backup & Restore
**Status:** ✅ **IMPLEMENTED**  
**Backend:** `app/core/backup_service.py`  
**Working Features:**
- Create backup (ZIP containing database + PDFs) ✅
- Restore from backup ✅
- WAL checkpoint before backup ✅
- Rollback on restore failure ✅
- Manifest file with version tracking ✅

**Evidence:**
```python
# backup_service.py lines 22-49
def create_backup(self, output_zip: Path) -> Path:
    """Write a backup zip containing the database and exported PDFs."""
    # Force any pending WAL writes to disk before zipping
    conn = self.db.connect()
    conn.commit()
    conn.execute("PRAGMA wal_checkpoint(FULL)")
    
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(BACKUP_MANIFEST_NAME, manifest)
        # Database file
        if Path(DB_PATH).exists():
            zf.write(DB_PATH, arcname=f"data/{Path(DB_PATH).name}")
        # Exported PDFs
        ...
```

**UI Location:** Settings → Backup & Export tab

---

#### 5. Export Data (CSV)
**Status:** ✅ **IMPLEMENTED**  
**Backend:** `app/core/csv_exporter.py`  
**Working Features:**
- Export clients to CSV ✅
- Export projects to CSV ✅
- Export invoices to CSV ✅
- Full data export with all fields ✅

**Evidence:**
```python
# csv_exporter.py lines 16-43
def export_clients(self, path: Path) -> Path:
    rows = self.clients.get_all()
    return self._write(path, ["id", "name", "email", ...], rows)

def export_projects(self, path: Path) -> Path:
    rows = self.projects.get_all()
    return self._write(path, ["id", "name", "client_name", ...], rows)
```

**UI Location:** Settings → Backup & Export tab

---


#### 6. Receipt OCR (Bonus Feature)
**Status:** ✅ **IMPLEMENTED**  
**Backend:** `app/core/receipt_ocr.py`  
**Working Features:**
- Upload receipt image ✅
- Extract text via Tesseract OCR ✅
- Detect total amount ✅
- Detect date ✅
- Display results in UI ✅

**UI Location:** Settings → Receipt OCR tab

---

### 🟡 PARTIALLY IMPLEMENTED

#### 7. Change Password
**Status:** 🟡 **NOT APPLICABLE** (No user authentication system)  
**Reason:** SmartDesk is an **offline-first, local desktop app** with **no user accounts**  
**Architecture:** Single-user SQLite database per installation  
**Security Model:** OS-level file permissions protect data

**Notes:**
- There is no login/authentication system
- No password field in database
- No user accounts table
- Data security relies on OS user accounts
- Would only make sense if multi-user or cloud sync added

**Recommendation:** Skip this feature unless you add cloud sync or multi-user support

---

#### 8. Notification Toggles / Reminder System
**Status:** 🟡 **PARTIALLY IMPLEMENTED**  
**Backend:** Email reminders exist, but no toggle UI  
**Working Features:**
- Send overdue invoice reminders via email ✅ (invoices_page.py)
- SMTP integration working ✅

**Missing:**
- ❌ UI toggles to enable/disable notifications
- ❌ Desktop notifications (no plyer integration found)
- ❌ Scheduled reminder system
- ❌ Reminder frequency settings
- ❌ Notification preferences (email vs desktop)

**Evidence of Partial Implementation:**
```python
# invoices_page.py lines 359-429
def _send_overdue_reminders(self) -> None:
    """Manual trigger - user clicks button to send reminders"""
    overdue_rows = self.db.execute(...)
    for row in with_emails:
        self.email_service.send(...)
```

**Current State:** Manual reminders only (user clicks button)  
**Missing:** Automated scheduled reminders + toggle UI

**UI Location:** Invoices page (manual button), no settings toggle

---


### ❌ MISSING / NOT IMPLEMENTED

#### 9. Billing & Plan Management
**Status:** ❌ **MISSING**  
**Backend:** None  
**Database:** No tables for subscriptions, plans, billing  
**UI:** Placeholder text in sidebar ("Local · v1.0.0")

**No Evidence Found:**
- ❌ No subscription model
- ❌ No billing integration (Razorpay, Stripe, etc.)
- ❌ No plan tiers (free/pro/enterprise)
- ❌ No payment history
- ❌ No upgrade/downgrade logic

**Current Model:** Free, offline desktop app with no billing

**To Implement:**
1. Add `subscriptions` table (user_id, plan_type, status, expires_at)
2. Add `billing_history` table (transaction records)
3. Integrate Razorpay SDK for Indian market
4. Add plan limits (projects, clients, storage)
5. Add upgrade UI and payment flow
6. Add trial period logic

**Estimated Effort:** 2-3 weeks (new architecture layer)

---

#### 10. Integrations (Google Calendar, Razorpay, Slack, Dropbox)
**Status:** ❌ **MISSING**  
**Backend:** None  
**Database:** No integration tables  
**UI:** No integration settings page

**No Evidence Found:**
- ❌ No Google Calendar API integration
- ❌ No Razorpay payment gateway
- ❌ No Slack webhook/bot integration
- ❌ No Dropbox API for file storage
- ❌ No OAuth flow for any service
- ❌ No integration credentials storage

**To Implement:**
Each integration requires:
1. OAuth 2.0 flow (except Razorpay)
2. Token storage in `app_settings`
3. API client wrapper
4. Sync logic
5. UI for connect/disconnect
6. Error handling and token refresh

**Estimated Effort:**
- Google Calendar: 1 week (sync deadlines)
- Razorpay: 3-4 days (payment links in invoices)
- Slack: 3-4 days (notifications)
- Dropbox: 1 week (file attachments)

**Total:** 3-4 weeks for all 4 integrations

---


#### 11. Delete Account
**Status:** ❌ **NOT APPLICABLE** (No user accounts)  
**Reason:** Same as "Change Password" - no account system exists

**Current Data Deletion Options:**
- Manual: Delete `data/smartdesk.db` file
- UI: No built-in "clear all data" button
- Backup: Restore from empty backup

**If User Accounts Were Added:**
Would need:
1. Confirm dialog (enter password or type "DELETE")
2. Delete all user data from database
3. Delete uploaded files (logos, attachments)
4. Revoke integration tokens
5. Cancel subscription (if billing added)
6. Optionally export data before delete
7. Close application after deletion

**Current Recommendation:** Add "Clear All Data" button to Settings if needed  
**Estimated Effort:** 1-2 days (if account system exists)

---

## 📋 Quick Reference Table

| Feature | Status | Backend Exists | UI Exists | Database | Notes |
|---------|--------|----------------|-----------|----------|-------|
| **Profile & Account** | ✅ IMPLEMENTED | ✅ Yes | ✅ Yes | `app_settings` | Name, email, phone, bio, logo, UPI |
| **Change Password** | 🔴 N/A | ❌ No | ❌ No | None | No auth system |
| **Workspace Settings** | 🟡 PARTIAL | ✅ Yes | 🟡 Minimal | `app_settings` | Only due days UI, missing currency/timezone |
| **Notification Toggles** | 🟡 PARTIAL | 🟡 Partial | ❌ No | None | Manual reminders work, no automation |
| **Billing & Plan** | ❌ MISSING | ❌ No | 🟡 Placeholder | None | Sidebar shows "Local · v1.0.0" |
| **Integrations** | ❌ MISSING | ❌ No | ❌ No | None | Google, Razorpay, Slack, Dropbox |
| **Export All Data** | ✅ IMPLEMENTED | ✅ Yes | ✅ Yes | N/A | CSV export + backup ZIP |
| **Delete Account** | 🔴 N/A | ❌ No | ❌ No | None | No account to delete |
| **Email (SMTP)** | ✅ IMPLEMENTED | ✅ Yes | ✅ Yes | `app_settings` | Full config + test |
| **Backup/Restore** | ✅ IMPLEMENTED | ✅ Yes | ✅ Yes | N/A | ZIP format, rollback support |
| **Receipt OCR** | ✅ IMPLEMENTED | ✅ Yes | ✅ Yes | N/A | Tesseract integration |

---

## 🎯 Priority Recommendations

### High Priority (User-Facing Gaps)

**1. Complete Workspace Settings UI**
- **Missing:** Currency, timezone, date format dropdowns
- **Backend:** Already supports key/value storage
- **Effort:** 1-2 days
- **Impact:** Better UX for international users

**2. Automated Notification System**
- **Missing:** Scheduled reminders, toggle UI
- **Backend:** Email service exists, need scheduler
- **Effort:** 3-4 days
- **Impact:** Critical for freelancers (get paid faster)

### Medium Priority (Nice to Have)

**3. Razorpay Integration**
- **Why:** Indian market primary (UPI already supported)
- **What:** Payment links in invoices
- **Effort:** 3-4 days
- **Impact:** Reduce payment friction

**4. Google Calendar Sync**
- **Why:** Deadline management
- **What:** Sync project deadlines to Calendar
- **Effort:** 1 week
- **Impact:** Better time management

### Low Priority (Optional)

**5. Billing/Subscription System**
- **Why:** Only if monetizing as SaaS
- **Effort:** 2-3 weeks
- **Impact:** Revenue model, but changes app nature

**6. Slack/Dropbox Integrations**
- **Why:** Niche use cases
- **Effort:** 1-2 weeks each
- **Impact:** Power users only

---


## 🔍 Technical Details

### Database Architecture

**Settings Storage:**
```sql
-- Migration 001 (migrations.py)
CREATE TABLE IF NOT EXISTS app_settings (
    key TEXT PRIMARY KEY,
    value TEXT
)
```

**Key/Value Pairs in Use:**
```
business_name
business_email
business_phone
business_address
business_gstin
business_logo_path
upi_id
upi_name
default_due_days
default_gst_rate
smtp_host
smtp_port
smtp_username
smtp_password
smtp_from
smtp_use_tls
first_run_done
```

**Missing Keys (for future features):**
```
workspace_name
default_currency
timezone
date_format
notifications_enabled
reminder_frequency
google_calendar_token
razorpay_key_id
slack_webhook_url
dropbox_token
```

---

### Code Structure

**Service Layer:**
```
app/core/
├── settings_service.py     ✅ Business profile + preferences
├── email_service.py         ✅ SMTP config + send
├── backup_service.py        ✅ Backup/restore ZIP
├── csv_exporter.py          ✅ CSV export
└── receipt_ocr.py           ✅ OCR (bonus feature)
```

**Repository Layer:**
```
app/data/repositories/
└── settings_repo.py         ✅ Key/value storage
```

**UI Layer:**
```
app/ui/pages/
└── settings_page.py         ✅ 6 tabs (Business, Prefs, Email, OCR, Data, About)
```

---

## 💡 Implementation Roadmap

### Phase 1: Complete Existing Features (1 week)

**Week 1: Workspace Settings UI**
- [ ] Add currency dropdown (INR, USD, EUR, GBP)
- [ ] Add timezone selector
- [ ] Add date format picker (DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD)
- [ ] Save to `app_settings` (backend already supports)
- [ ] Use settings in invoices and UI

**Week 1: Notification Toggles**
- [ ] Add "Enable Reminders" checkbox
- [ ] Add reminder frequency dropdown (Daily, Weekly)
- [ ] Add reminder days-before-due spinbox
- [ ] Save to `app_settings`
- [ ] Add scheduled task (APScheduler or similar)
- [ ] Auto-send reminders based on settings

---

### Phase 2: High-Value Integrations (3 weeks)

**Week 2: Razorpay Integration**
- [ ] Add `razorpay_key_id` and `razorpay_key_secret` settings
- [ ] Create `RazorpayService` class
- [ ] Add "Generate Payment Link" button to invoices
- [ ] Store payment link in invoice record
- [ ] Add webhook handler for payment confirmation
- [ ] Auto-mark invoice as paid on webhook

**Week 3-4: Google Calendar Integration**
- [ ] Add OAuth 2.0 flow UI
- [ ] Store access token in `app_settings`
- [ ] Create `GoogleCalendarService` class
- [ ] Add "Sync to Calendar" toggle on projects
- [ ] Sync deadlines to Google Calendar
- [ ] Handle token refresh
- [ ] Add disconnect button

---

### Phase 3: Advanced Features (If Needed)

**Optional: Billing System** (2-3 weeks)
- Only if monetizing as SaaS
- Add subscription tables
- Integrate Stripe/Razorpay subscriptions
- Add plan limits and enforcement
- Add upgrade flow

**Optional: More Integrations** (1-2 weeks each)
- Slack notifications
- Dropbox file storage
- GitHub time tracking

---

## 🚨 Breaking Changes / Considerations

### If Adding User Accounts:
**Impact:** Changes entire architecture
- Need authentication system
- Need user table with passwords
- Need session management
- Need password reset flow
- Need "Change Password" feature
- Need "Delete Account" feature
- Need multi-tenancy in database

**Recommendation:** Only add if building SaaS version

### If Adding Cloud Sync:
**Impact:** Major feature
- Need backend server API
- Need data sync logic
- Need conflict resolution
- Need offline queue
- Changes offline-first model

**Recommendation:** Phase 3+ feature

---

## ✅ What's Already Production-Ready

These features work well and are production-ready:

1. ✅ **Business Profile** - Full CRUD, used in PDF invoices
2. ✅ **Email (SMTP)** - Send invoices and reminders
3. ✅ **Backup/Restore** - Reliable with rollback
4. ✅ **CSV Export** - Clean data export for accountants
5. ✅ **Receipt OCR** - Works if Tesseract installed

---

## 📝 Summary

**SmartDesk has a solid foundation** with 6 of 11 features fully implemented. The missing features fall into three categories:

1. **N/A:** Password/account features (no auth system by design)
2. **Partial:** Workspace settings and notifications (backend exists, UI incomplete)
3. **Missing:** Billing and integrations (not started)

**Next Steps:**
1. Complete workspace settings UI (1-2 days)
2. Add automated notifications (3-4 days)
3. Add Razorpay integration (3-4 days)
4. Consider Google Calendar (1 week)

**Total to "Complete":** 2-3 weeks to finish all user-facing features

---

**Audit completed by:** Kiro AI  
**Date:** June 4, 2026  
**Confidence:** High (full codebase scan)

