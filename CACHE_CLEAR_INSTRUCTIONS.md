# Cache Clear Instructions

## Problem
Python caches compiled bytecode in `__pycache__` folders. When you make changes to `.py` files, the old cached version might still be running.

## Solution: Clear All Caches

### Method 1: PowerShell Command (Recommended)
```powershell
Get-ChildItem -Path "d:\Code\Tool\Smartdesk" -Include "__pycache__" -Recurse -Force | Remove-Item -Recurse -Force
```

### Method 2: Manual Deletion
1. Navigate to `d:\Code\Tool\Smartdesk`
2. Search for folders named `__pycache__`
3. Delete all `__pycache__` folders
4. Common locations:
   - `app\__pycache__`
   - `app\ui\__pycache__`
   - `app\ui\pages\__pycache__`
   - `app\data\__pycache__`
   - `app\core\__pycache__`
   - `app\ml\__pycache__`

### Method 3: Python Clean Script
```python
import os
import shutil
from pathlib import Path

project_root = Path(__file__).parent
for pycache in project_root.rglob("__pycache__"):
    shutil.rmtree(pycache)
    print(f"Deleted: {pycache}")
```

## After Clearing Cache

1. **Close the application** if it's running
2. **Clear caches** using one of the methods above
3. **Restart the application**:
   ```bash
   python main.py
   ```

## Verify the Fix

Check the Dashboard Recent Projects table:

### Column Order Should Be:
1. **PROJECT** - Project name (bold white)
2. **CLIENT** - Client name (gray)
3. **TYPE** - Project type (gray) ← Should show "Development", "Design", etc.
4. **STATUS** - Status badge (colored pill) ← Should show In Progress, Completed, etc.
5. **DEADLINE** - Date (gray) ← Should show "Jun 7, 2026" format
6. **BUDGET** - Amount (white, right-aligned) ← Should show ₹35,000, ₹28,000, etc.

### What to Check:
- [ ] TYPE column shows project types (Development, Design, Video, Music)
- [ ] STATUS column shows colored status badges (NOT money values)
- [ ] BUDGET column shows money values with ₹ symbol (NOT empty)
- [ ] All columns are properly aligned
- [ ] No data clustering or overlapping

## Common Issues

### Issue: "Still showing old data after clearing cache"
**Solution:** Make sure to **close the application** completely before clearing cache and restarting.

### Issue: "Columns still misaligned"
**Solution:** Check that you're looking at the **Dashboard page**, not another page. The fix only applies to the Dashboard Recent Projects table.

### Issue: "Application won't start after clearing cache"
**Solution:** This is normal - caches will be regenerated on first run. Just wait a few seconds for the application to start.

## Debugging: Verify Code is Correct

Run this test to see actual database values:
```bash
python test_project_data.py
```

Expected output should show:
```
1. MVP Landing Page
   Type: 'Development'
   Status: Completed
   Budget: 35000.0

2. Explainer Video
   Type: 'Video'
   Status: In Progress
   Budget: 28000.0
```

## Table Column Indices (For Reference)

The code uses these column indices:
```python
self.table.setItem(i, 0, name_item)      # PROJECT
self.table.setItem(i, 1, client_item)    # CLIENT
self.table.setItem(i, 2, type_item)      # TYPE
self.table.setCellWidget(i, 3, status_badge)  # STATUS
self.table.setItem(i, 4, deadline_item)  # DEADLINE
self.table.setItem(i, 5, budget_item)    # BUDGET
```

All indices are correct (0-5 for 6 columns).

## Status Check

After clearing cache and restarting:

✅ TYPE column: Should show Development, Design, Video, Music  
✅ STATUS column: Should show colored badges (In Progress, Completed, Not Started)  
✅ BUDGET column: Should show ₹35,000, ₹28,000, ₹22,000, etc.  
✅ No empty columns  
✅ No misaligned data  

---

**If issue persists after clearing cache**, please provide a fresh screenshot and we'll investigate further.
