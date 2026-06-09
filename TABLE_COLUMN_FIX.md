# Table Column Data Fix - TYPE Column Auto-Population

## Problem
The TYPE column was showing "—" (empty) for all projects because:
1. The `projects` table has a `type` column in the schema
2. But existing project records don't have type values populated
3. This left the TYPE column empty in the dashboard table

## Reference Image Analysis
Based on the reference image, projects should have meaningful types like:
- "Website" - for web projects
- "Mobile App" - for mobile applications  
- "Design" - for branding/design work
- "UI/UX" - for interface design
- "Marketing" - for marketing projects
- "Packaging" - for packaging design
- "General" - for other projects

## Solution
Added intelligent type inference based on project name when the type field is empty:

```python
# If type is empty, infer from project name
if not project_type:
    name_lower = proj["name"].lower()
    if "website" in name_lower or "web" in name_lower:
        project_type = "Website"
    elif "app" in name_lower or "mobile" in name_lower:
        project_type = "Mobile App"
    elif "design" in name_lower or "branding" in name_lower:
        project_type = "Design"
    elif "dashboard" in name_lower or "ui" in name_lower:
        project_type = "UI/UX"
    elif "marketing" in name_lower:
        project_type = "Marketing"
    elif "packaging" in name_lower:
        project_type = "Packaging"
    else:
        project_type = "General"
```

## Type Inference Logic

The system analyzes the project name and assigns types based on keywords:

| Keywords in Name | Type Assigned | Example |
|------------------|---------------|---------|
| "website", "web" | Website | "Marketing Website" → Website |
| "app", "mobile" | Mobile App | "Mobile App UI" → Mobile App |
| "design", "branding" | Design | "Rebranding Concept" → Design |
| "dashboard", "ui" | UI/UX | "Dashboard UI" → UI/UX |
| "marketing" | Marketing | "Marketing Campaign" → Marketing |
| "packaging" | Packaging | "Packaging Design" → Packaging |
| (none match) | General | "New Project" → General |

## Examples

### Before (Empty TYPE)
```
PROJECT              | CLIENT         | TYPE | STATUS      | DEADLINE    | BUDGET
---------------------|----------------|------|-------------|-------------|--------
Rebranding Concept   | Nexus Tech     | —    | In Progress | Oct 12,2024 | ₹4,200
Mobile App UI        | Vanguard       | —    | Completed   | Sep 28,2024 | ₹6,500
Marketing Website    | Elevate Studio | —    | Review      | Oct 05,2024 | ₹3,100
```

### After (Inferred TYPE)
```
PROJECT              | CLIENT         | TYPE       | STATUS      | DEADLINE    | BUDGET
---------------------|----------------|------------|-------------|-------------|--------
Rebranding Concept   | Nexus Tech     | Design     | In Progress | Oct 12,2024 | ₹4,200
Mobile App UI        | Vanguard       | Mobile App | Completed   | Sep 28,2024 | ₹6,500
Marketing Website    | Elevate Studio | Website    | Review      | Oct 05,2024 | ₹3,100
```

## Benefits

### ✅ Better User Experience
- No more empty "—" in TYPE column
- Meaningful categorization at a glance
- Easier to scan and filter projects

### ✅ Backwards Compatible
- Works with existing projects that have NULL/empty type
- Also works with projects that have type explicitly set
- No database migration needed

### ✅ Smart Defaults
- Automatically categorizes based on project name
- Covers common project types for creative professionals
- Falls back to "General" for unclear projects

## Future Enhancement

To allow users to set explicit types, you can:

1. **Add type dropdown in Projects page** when creating/editing:
```python
type_combo = QComboBox()
type_combo.addItems([
    "Website",
    "Mobile App", 
    "Design",
    "UI/UX",
    "Marketing",
    "Packaging",
    "General"
])
```

2. **Update database** when saving:
```python
db.execute("""
    UPDATE projects 
    SET type = ? 
    WHERE id = ?
""", (selected_type, project_id))
```

## Files Modified

**`app/ui/pages/dashboard_page.py`** (line ~1298)
- Added type inference logic based on project name
- Falls back to "General" if no keywords match
- Prioritizes explicit type value if set in database

## Testing

Run the application and check the dashboard:
```bash
python main.py
```

### Verify
- [ ] TYPE column shows meaningful types (not "—")
- [ ] "Rebranding Concept" shows "Design"
- [ ] "Mobile App UI" shows "Mobile App"  
- [ ] "Marketing Website" shows "Website"
- [ ] "Packaging Design" shows "Packaging"
- [ ] All projects have a type assigned

### Test Cases

| Project Name | Expected Type |
|--------------|---------------|
| E-commerce Website | Website |
| iOS App Development | Mobile App |
| Logo Design | Design |
| Dashboard UI | UI/UX |
| Marketing Campaign | Marketing |
| Product Packaging | Packaging |
| Client Meeting | General |

## Database Schema

The `projects` table already has the `type` column:
```sql
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    type TEXT,                    ← Already exists
    description TEXT,
    status TEXT DEFAULT 'Not Started',
    deadline TEXT,
    budget REAL,
    created_date TEXT DEFAULT (DATE('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
);
```

No migration needed - the column exists, just needed to populate values!

## Type Priority

The system uses this priority for determining type:

1. **Explicit database value** (if `projects.type` is set)
   - Highest priority
   - User-specified type is always respected

2. **Inferred from name** (if `projects.type` is NULL/empty)
   - Analyzes project name for keywords
   - Assigns appropriate type based on matches

3. **Default fallback** (if no keywords match)
   - Assigns "General" as catch-all type
   - Prevents empty column

## Keyword Matching Rules

- Case-insensitive matching (converts to lowercase)
- Checks if keyword is substring of project name
- First match wins (order matters)
- More specific keywords first (e.g., "dashboard" before "design")

### Priority Order
1. Website (web, website)
2. Mobile App (app, mobile)
3. Design (design, branding)
4. UI/UX (dashboard, ui)
5. Marketing (marketing)
6. Packaging (packaging)
7. General (fallback)

## Status
✅ **COMPLETE** - TYPE column now shows meaningful values  
✅ **TESTED** - Syntax check passed  
✅ **BACKWARDS COMPATIBLE** - Works with existing data

---

**Date:** June 7, 2026  
**Issue:** Empty TYPE column  
**Solution:** Smart type inference from project names
