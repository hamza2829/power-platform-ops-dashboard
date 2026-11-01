# FAQ and data quality checks

[Wiki home](Home.md)

Reference numbers: [`docs/reference_totals.json`](../reference_totals.json) (Python reference, seed 42). Compare within displayed rounding.

## Wrong totals

**Order Count shows 4,999, but the data has 5,000 orders.**
Expected. ORD-000003 has no order date, so any Date slicer range excludes it. Clear the Date slicer → 5,000. Same for tickets (1,499 vs 1,500, TKT-000001). Do not invent a date to "fix" it.

**Total Revenue is lower than the sum of `order_value` in Excel.**
Total Revenue excludes **Cancelled** orders and ORD-000004 (invalid value → null). Excel also counts the three duplicate rows (999999.00 each) unless you remove them. Expected: €11,516,357.74 (full 18 months) or €11,524,358.92 (no Date slicer).

**Delivered Orders and Eligible Deliveries differ.**
Expected: 4,552 vs 4,549. Eligible excludes deliveries with no usable delivery date and those with an imputed promise. See [Eligible Deliveries](KPI-Definitions.md#eligible-deliveries).

**Tickets per 100 Orders is over 100.**
It is a workload ratio, not a percentage of orders. Sofas in September 2025 = 214.6 is expected.

**Priority slicer doesn't change Order Count or Total Revenue.**
Correct. Priority is a Tickets column and only filters ticket measures.

**YoY % for 2024 is blank, or 2025 vs 2024 looks huge.**
Data starts July 2024, so only July–December 2025 have a prior-year month. Compare those months only. July 2025 should be −18.0%.

**Rolling 3 Month Average is blank for July/August 2024.**
Expected: it needs three full months of data. First value: September 2024 = €650,691.

**Numbers are double-counted or slicers behave strangely.**
Check the model: exactly six relationships, all one-to-many, single direction, no Orders–Tickets relationship, no bidirectional filters ([Data model](Data-Model.md)). Turn off auto-detected relationships and Auto date/time.

**Region totals don't add up after a drill-through.**
Drill-through passes all filters ("Keep all filters" is on). Clear the drill-through filter or use Back before comparing.

## Missing data

**Refresh fails / "file not found".**
`DataFolder` parameter points to the wrong place. Set it to the absolute `data` folder path, no quotes, no trailing `\`.

**A whole table is empty or has errors.**
Queries must be named exactly `Products`, `Customers`, `Orders`, `Tickets` and created in that order (Orders uses Products; Tickets uses Orders).

**Dates or amounts are null for many rows.**
Do not add automatic "Changed Type" steps; the scripts parse ISO dates and dot decimals with `en-US`. Only the deliberately damaged rows should be null.

**A delivery date or closing date is blank.**
Normal for Open/Cancelled orders and Open tickets. It is a data issue only for the IDs in `data/manifest.json`.

**Dates after 31 Dec 2025 do not appear.**
The data is a fixed snapshot. It does not move to today's date.

## Data quality checks

Run these after any change to data, queries or measures.

| # | Check | How | Expected |
| --- | --- | --- | --- |
| 1 | Clean row counts | Table view in Desktop | Customers 800, Products 5, Orders 5,000, Tickets 1,500 |
| 2 | Keys unique | Column profile on each key | No duplicate `customer_id`, `product_group`, `order_id`, `ticket_id` |
| 3 | No conversion errors | Power Query → Column quality (entire data set) | 0 errors; nulls only where expected |
| 4 | Relationships | Model view | Exactly the six listed in [Data model](Data-Model.md) |
| 5 | Unfiltered counts | Cards, no slicers | 5,000 orders / 1,500 tickets |
| 6 | Full-period KPIs | Date 2024-07-01 – 2025-12-31 | Values in `slices.all_18_months_date_slicer` |
| 7 | Slices | East; Sofas + Sep 2025; High priority | `east_all_18_months`, `sofas_september_2025`, `high_priority_all_18_months` |
| 8 | Data issue cards | No slicers | Orders 5, Tickets 4 (the IDs in `manifest.json`) |
| 9 | Source files unchanged | `python tools/verify_data.py --check` | `PASS` |
| 10 | Python tests | `python -m pytest -q` | All pass |
| 11 | Docs | `python tools/check_docs.py` | `PASS` |

Checks 9–11 also run in GitHub Actions. Checks 1–8 need Power BI Desktop and are **not automated**; record them in [BUILD_STATUS.md](../BUILD_STATUS.md).
