# Dynamic Dashboard System

## Overview

SmartDesk now features a fully dynamic dashboard that automatically updates when data changes occur on any page. This ensures real-time synchronization across the entire application without manual refresh requirements.

## Implementation Details

### 1. Global Data Change Signal System

**Core Components:**
- `app/core/signals.py` - Contains `DataChangedSignal` and `emit_data_changed()` function
- Global signal instance attached to `QApplication` as `app.data_changed`
- All data modification operations emit this signal

**Signal Flow:**
```
Data Change → emit_data_changed() → Global Signal → Dashboard Refresh
```

### 2. Dashboard Auto-Refresh

**Dashboard Connections:**
- Connected to global `data_changed` signal in `__init__`
- Automatically refreshes all stat cards and charts when signal is received
- Uses timer-based initial loading (50ms delay) to ensure UI is ready

**Real-time Updates:**
- **Active Projects:** Now correctly shows count of all active statuses (In Progress + Review + Not Started)
- **Total Revenue:** Updates when invoices are marked as paid
- **Pending Invoices:** Updates when invoice status changes
- **Hours Tracked:** Updates when time entries are added

### 3. Multi-Page Synchronization

**Main Window Enhancements:**
- Global data change handler refreshes dashboard + current page + critical pages
- Ensures all pages stay synchronized when data changes
- Prevents stale data display across navigation

**Pages with Data Change Emissions:**
- ✅ **Clients Page** - Emits on add/update/delete operations
- ✅ **Projects Page** - Emits on add/update/delete operations  
- ✅ **Invoices Page** - Emits on create/mark_paid operations
- ✅ **Time Page** - Emits on timer stop/manual entry
- ✅ **Contracts Page** - Emits on contract analysis/save
- ✅ **Settings Page** - Emits on business profile/preferences save
- ❌ **Analytics Page** - Read-only, no emissions needed

### 4. Database Integration

**Query Responsiveness:**
- All dashboard stat queries use current database state
- No caching or static values that could become stale
- Proper null handling and fallback values

**Performance Considerations:**
- Refresh operations are lightweight (simple aggregate queries)
- Timer-based loading prevents UI blocking
- Selective page refresh reduces unnecessary operations

## Usage Examples

### Automatic Updates in Action:

1. **Add New Client** → Dashboard "Active Projects" updates if client has projects
2. **Create Project** → Dashboard "Active Projects" count increases
3. **Mark Invoice Paid** → Dashboard "Total Revenue" increases, "Pending Invoices" decreases
4. **Log Time** → Dashboard "Hours Tracked" increases
5. **Update Project Status** → Dashboard "Active Projects" adjusts based on new status

### Cross-Page Synchronization:

- Change project status on Projects page → Dashboard immediately shows updated count
- Mark invoice paid on Invoices page → Dashboard revenue cards update instantly
- Add time entry on Time page → Dashboard hours counter refreshes
- Navigate between pages → All pages show current data without manual refresh

## Technical Benefits

1. **Real-time Data Consistency** - No stale data across the application
2. **Seamless User Experience** - Changes are immediately visible everywhere
3. **Reduced Manual Refresh** - Users don't need to navigate away and back to see updates
4. **Scalable Architecture** - Easy to add new pages to the dynamic system
5. **Performance Optimized** - Only refreshes what's necessary when data changes

## Verification

To verify the system is working:

1. Open dashboard and note current stats (e.g., Active Projects: 11)
2. Go to Projects page and change a project status from "Completed" to "In Progress"  
3. Return to dashboard → Active Projects should increase by 1
4. Go to Invoices page and mark an unpaid invoice as paid
5. Dashboard should immediately show updated revenue/pending amounts

The system eliminates the need for manual page refresh and provides a truly dynamic, responsive user interface.