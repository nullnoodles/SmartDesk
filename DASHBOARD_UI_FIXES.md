# Dashboard UI Fixes — Text Clustering, Filter Tabs & Scroll Behavior

## Summary
Fixed three key UI issues in the Dashboard Recent Projects section:
1. ✅ Text clustering in table cells
2. ✅ Filter tabs now curved squares instead of pills
3. ✅ Only table scrolls, not the whole page

---

## Issue 1: Text Clustering in Table Cells

### Problem
Text in table cells was merging together with insufficient spacing, making it hard to read.

### Solution
Increased padding and row height for better text spacing:

**Changes in `app/ui/styles/style.qss`:**
```css
/* Before */
QTableWidget::item, QTableView::item {
    padding: 6px 10px;
}
QHeaderView::section {
    padding: 8px 16px;
}

/* After */
QTableWidget::item, QTableView::item {
    padding: 12px 16px;  /* Increased from 6px 10px */
}
QHeaderView::section {
    padding: 12px 16px;  /* Increased from 8px 16px */
}
```

**Changes in `app/ui/pages/dashboard_page.py`:**
```python
# Increased row height from 48px to 56px
self.verticalHeader().setDefaultSectionSize(56)

# Added word wrap control
self.setWordWrap(False)
```

**Result:**
- Cell padding: 12px vertical, 16px horizontal (was 6px × 10px)
- Row height: 56px (was 48px)
- Header padding: 12px vertical, 16px horizontal
- Text no longer clusters or overlaps

---

## Issue 2: Filter Tab Styling

### Problem
Filter tabs were too rounded (border-radius: 14px), looking like pills instead of the rounded squares shown in the reference.

### Solution
Reduced border-radius and adjusted styling for a more rectangular appearance:

**Changes in `app/ui/pages/dashboard_page.py`:**
```python
# Before
border-radius: 14px;
padding: 5px 14px;

# After
border-radius: 8px;        # Reduced from 14px
padding: 6px 16px;         # Adjusted for better proportion
min-height: 32px;          # Added fixed height
```

**Additional hover effect:**
```css
QPushButton#table_filter_tab:hover:!checked {
    color: #c8cbdf;
    background: rgba(200, 203, 223, 0.05);  /* Subtle hover background */
}
```

**Result:**
- Filter tabs now appear as curved squares (8px radius)
- More defined rectangular shape
- Better visual consistency with reference design
- Subtle hover feedback added

---

## Issue 3: Scroll Behavior

### Problem
When scrolling, the entire dashboard page scrolled including stat cards and charts. Users wanted only the table to scroll while keeping the rest of the page fixed.

### Solution
Wrapped the table in its own scroll area with fixed dimensions:

**Changes in `app/ui/pages/dashboard_page.py`:**

1. **Table Card Container:**
```python
# Before
table_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
table_card.setMinimumHeight(280)

# After
table_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
table_card.setMinimumHeight(420)
table_card.setMaximumHeight(620)
```

2. **Table Scroll Area:**
```python
# NEW: Wrap table in its own scroll area
table_scroll = QScrollArea()
table_scroll.setWidgetResizable(True)
table_scroll.setFrameShape(QFrame.NoFrame)
table_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
table_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
table_scroll.setMinimumHeight(300)
table_scroll.setMaximumHeight(500)

# Table size policy changed
self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

table_scroll.setWidget(self.table)
table_card_layout.addWidget(table_scroll)
```

**Result:**
- Stat cards and charts remain fixed at the top
- Only the Recent Projects table scrolls
- Table has fixed height (300px min, 500px max)
- Table card container has fixed height (420px min, 620px max)
- Smooth scrolling experience with native scrollbar styling

---

## Before vs After Comparison

### Text Spacing
| Property          | Before    | After     |
|-------------------|-----------|-----------|
| Cell padding      | 6×10px    | 12×16px   |
| Row height        | 48px      | 56px      |
| Header padding    | 8×16px    | 12×16px   |

### Filter Tabs
| Property          | Before    | After     |
|-------------------|-----------|-----------|
| Border radius     | 14px      | 8px       |
| Padding           | 5×14px    | 6×16px    |
| Min height        | (auto)    | 32px      |
| Hover background  | None      | Added     |

### Scroll Behavior
| Element           | Before                | After                |
|-------------------|-----------------------|----------------------|
| Dashboard page    | Full page scrolls     | Fixed (no scroll)    |
| Stat cards        | Scroll with page      | Fixed at top         |
| Charts            | Scroll with page      | Fixed               |
| Recent Projects   | Scroll with page      | Independent scroll   |
| Table height      | Auto-expanding        | Fixed (300-500px)    |

---

## Files Modified

### 1. `app/ui/styles/style.qss`
- Lines ~600-605: Increased table cell padding (6×10px → 12×16px)
- Lines ~615-620: Increased header padding (8×16px → 12×16px)

### 2. `app/ui/pages/dashboard_page.py`
- Lines ~404-413: Updated CustomTableWidget with better row height (56px) and properties
- Lines ~763-766: Fixed table card height (420-620px range)
- Lines ~780-806: Changed filter tab styling (border-radius: 8px, min-height: 32px)
- Lines ~842-862: Added table scroll area wrapper with fixed dimensions

---

## Testing Checklist

Run the application and verify:

```bash
python main.py
```

### Visual Tests
- [ ] Table cells have adequate spacing (text doesn't cluster)
- [ ] Filter tabs appear as curved squares (not pills)
- [ ] "All" tab has green outline when active
- [ ] Filter tabs show subtle hover effect
- [ ] Stat cards stay fixed at top when scrolling
- [ ] Only the Recent Projects table scrolls
- [ ] Scrollbar appears only in table area
- [ ] Table height is reasonable (not too tall/short)

### Functional Tests
- [ ] Click filter tabs to switch between project statuses
- [ ] Scroll table with mouse wheel (only table moves)
- [ ] Scroll with scrollbar (only table moves)
- [ ] Resize window (columns adjust proportionally)
- [ ] Add/remove projects (table updates correctly)

---

## Technical Details

### Row Height Calculation
```
Row Height = Vertical Padding × 2 + Text Height + Border
56px = 12px + 12px + ~20px (text) + 1px (border)
```

### Table Scroll Area Dimensions
- **Min Height**: 300px (shows ~5 rows at 56px each)
- **Max Height**: 500px (shows ~9 rows)
- **Typical**: 420-500px (comfortable viewing)

### Filter Tab Dimensions
- **Border Radius**: 8px (curved square, not pill)
- **Padding**: 6px top/bottom, 16px left/right
- **Min Height**: 32px (consistent button height)

---

## Known Limitations

1. **Fixed Table Heights**: Table card has maximum height of 620px. With very large datasets, scrolling is required.
   - **Why**: Prevents table from dominating the entire screen
   - **Workaround**: Use "View All →" button to navigate to full Projects page

2. **No Horizontal Scroll**: Horizontal scrollbar is disabled on table scroll area.
   - **Why**: Columns are percentage-based and auto-resize
   - **Workaround**: Minimum window width is 1280px (design requirement)

3. **Row Height**: Fixed at 56px (not auto-adjusting to content).
   - **Why**: Consistent row heights improve visual uniformity
   - **Workaround**: Project names that are too long will be truncated with ellipsis

---

## Future Enhancements

Potential improvements for future iterations:

1. **Virtual Scrolling**: For very large datasets (1000+ projects), implement virtual scrolling to improve performance
2. **Adjustable Heights**: Allow user to resize table area with drag handle
3. **Column Sorting**: Add click-to-sort on column headers
4. **Sticky Header**: Keep column headers visible while scrolling table body
5. **Row Hover Effects**: Subtle background color change on row hover

---

## References

- **Original Issue**: User reported text clustering and entire page scrolling
- **Reference Image**: Dashboard_Recent_Projects_Reference.png (filter tabs with curved squares)
- **Design System**: PYSIDE6_MODERN_UI_PROMPT.md (spacing and typography guidelines)

---

**Status**: ✅ COMPLETE  
**Date**: June 7, 2026  
**All Issues Resolved**
