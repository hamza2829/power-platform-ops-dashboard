# KPI definitions

[Wiki home](Home.md) · Source of truth: [`dax/measures.dax`](../../dax/measures.dax) · Formats: [`dax/README.md`](../../dax/README.md)

All **16 measures** in the repo, in file order. The DAX below is copied from `dax/measures.dax`; CI ([`tools/check_docs.py`](../../tools/check_docs.py)) fails if a measure is missing here or its code differs.

**About the example results.** They come from the Python reference calculator ([`docs/reference_totals.json`](../reference_totals.json)), not from Power BI. The DAX has **not been executed in a Power BI model yet**. Unless stated otherwise, the example context is: Date slicer `2024-07-01` to `2025-12-31`, no other filters ("full 18 months").

| # | Measure | Format | Example (full 18 months) |
| ---: | --- | --- | ---: |
| 1 | Total Revenue | EUR, 0 dp | €11,516,358 |
| 2 | Order Count | Whole number | 4,999 |
| 3 | Delivered Orders | Whole number | 4,552 |
| 4 | Eligible Deliveries | Whole number | 4,549 |
| 5 | Late Orders | Whole number | 1,298 |
| 6 | On-Time Delivery Rate | %, 1 dp | 71.5% |
| 7 | Average Lead Time Days | 1 dp | 29.9 |
| 8 | Ticket Count | Whole number | 1,499 |
| 9 | Tickets per 100 Orders | 1 dp | 30.0 |
| 10 | Average Ticket Resolution Days | 1 dp | 10.2 |
| 11 | Open Tickets | Whole number | 240 |
| 12 | Revenue Previous Year | EUR, 0 dp | €609,565 (July 2025) |
| 13 | Revenue YoY % | %, 1 dp | −18.0% (July 2025) |
| 14 | Revenue Rolling 3 Month Average | EUR, 0 dp | €650,691 (Sep 2024) |
| 15 | Orders with Data Issues | Whole number | 4 |
| 16 | Tickets with Data Issues | Whole number | 3 |

## Order measures

### Total Revenue

**Meaning:** booked value in EUR of orders that are not cancelled. It is *not* invoiced or accounting revenue. An order with an invalid value (`ORD-000004`) adds nothing to the sum but is still counted in Order Count.

```dax
Total Revenue =
CALCULATE (
    SUM ( Orders[order_value] ),
    KEEPFILTERS ( Orders[status] <> "Cancelled" )
)
```

**Example:** €11,516,357.74 for the full 18 months. With no Date slicer it is €11,524,358.92, because the undated order `ORD-000003` (€8,001.18) is then included.

### Order Count

**Meaning:** number of orders in the current filter, including open and cancelled ones.

```dax
Order Count = COUNTROWS ( Orders )
```

**Example:** 4,999 (full 18 months); 5,000 with no Date slicer.

### Delivered Orders

**Meaning:** orders with status `Delivered`, even when the actual delivery date is missing or was cleared.

```dax
Delivered Orders =
CALCULATE ( [Order Count], KEEPFILTERS ( Orders[status] = "Delivered" ) )
```

**Example:** 4,552.

### Eligible Deliveries

**Meaning:** delivered orders where we can reliably say "late" or "on time" (`late_flag` is not blank). This is the on-time denominator. Excluded: missing or cleared delivery date, and promises estimated from the product target.

```dax
Eligible Deliveries =
CALCULATE (
    [Order Count],
    FILTER (
        Orders,
        Orders[status] = "Delivered" && NOT ( ISBLANK ( Orders[late_flag] ) )
    )
)
```

**Example:** 4,549, which is 3 fewer than Delivered Orders (`ORD-000001`, `ORD-000002`, `ORD-000005`).

### Late Orders

**Meaning:** eligible deliveries that arrived after the original promised date. Delivery on the promised date counts as on time.

```dax
Late Orders =
CALCULATE ( [Order Count], KEEPFILTERS ( Orders[late_flag] = TRUE () ) )
```

**Example:** 1,298.

### On-Time Delivery Rate

**Meaning:** share of eligible deliveries that were on time: (Eligible − Late) ÷ Eligible. Unknown cases are left out instead of being counted as successes.

```dax
On-Time Delivery Rate =
DIVIDE ( [Eligible Deliveries] - [Late Orders], [Eligible Deliveries] )
```

**Example:** (4,549 − 1,298) ÷ 4,549 = **71.5%**. East region only: 51.0%.

### Average Lead Time Days

**Meaning:** average calendar days from order date to actual delivery, for delivered orders with both dates known.

```dax
Average Lead Time Days =
CALCULATE (
    AVERAGE ( Orders[lead_time_days] ),
    KEEPFILTERS ( Orders[status] = "Delivered" )
)
```

**Example:** 29.9 days (29.941538).

## Ticket measures

### Ticket Count

**Meaning:** number of service tickets created in the current filter. One order can have several tickets.

```dax
Ticket Count = COUNTROWS ( Tickets )
```

**Example:** 1,499 (full 18 months); 1,500 with no Date slicer.

### Tickets per 100 Orders

**Meaning:** a workload ratio: tickets *created* in the period per 100 orders *booked* in the same period. It is not "% of orders with a complaint" and can be above 100, because tickets can concern older orders.

```dax
Tickets per 100 Orders = DIVIDE ( [Ticket Count] * 100, [Order Count] )
```

**Example:** 1,499 × 100 ÷ 4,999 = 30.0. Sofas in September 2025: 221 tickets vs 103 orders = 214.6.

### Average Ticket Resolution Days

**Meaning:** average calendar days from creation to closure for tickets with both dates usable. Open tickets and tickets with an invalid closure are excluded.

```dax
Average Ticket Resolution Days = AVERAGE ( Tickets[resolution_days] )
```

**Example:** 10.2 days (10.244232); High priority only: 4.1 days.

### Open Tickets

**Meaning:** tickets still open at the fixed snapshot date 31 Dec 2025, among the tickets created in the selected dates. It is not a historical backlog.

```dax
Open Tickets =
CALCULATE ( [Ticket Count], KEEPFILTERS ( Tickets[ticket_status] = "Open" ) )
```

**Example:** 240.

## Time intelligence measures

### Revenue Previous Year

**Meaning:** Total Revenue for the same period one year earlier, using the marked Date table.

```dax
Revenue Previous Year =
CALCULATE ( [Total Revenue], SAMEPERIODLASTYEAR ( 'Date'[Date] ) )
```

**Example:** for July 2025 it returns July 2024's value, €609,564.95. Only July–December 2025 have a matching prior-year month in this data.

### Revenue YoY %

**Meaning:** change in Total Revenue vs the previous year, as a percentage. Blank (not 0%) if either year has no data.

```dax
Revenue YoY % =
VAR CurrentRevenue = [Total Revenue]
VAR PreviousRevenue = [Revenue Previous Year]
RETURN
    IF (
        NOT ( ISBLANK ( CurrentRevenue ) ) && NOT ( ISBLANK ( PreviousRevenue ) ),
        DIVIDE ( CurrentRevenue - PreviousRevenue, PreviousRevenue )
    )
```

**Example:** July 2025: (€499,860.25 − €609,564.95) ÷ €609,564.95 = **−18.0%**.

### Revenue Rolling 3 Month Average

**Meaning:** average monthly Total Revenue over three full calendar months ending with the month on the axis. Not a 90-day average. Blank where the three months are not all inside July 2024–December 2025.

```dax
// Use on a Year Month line chart. Ignore the date slicer for the lookback window.
// The first two source months and months outside the snapshot deliberately return blank.
Revenue Rolling 3 Month Average =
VAR MonthEnd = EOMONTH ( MAX ( 'Date'[Date] ), 0 )
VAR WindowStart = EOMONTH ( MonthEnd, -3 ) + 1
VAR DataStart = DATE ( 2024, 7, 1 )
VAR DataEnd = DATE ( 2025, 12, 31 )
RETURN
    IF (
        WindowStart >= DataStart && MonthEnd <= DataEnd,
        DIVIDE (
            CALCULATE (
                COALESCE ( [Total Revenue], 0 ),
                REMOVEFILTERS ( 'Date' ),
                DATESBETWEEN ( 'Date'[Date], WindowStart, MonthEnd )
            ),
            3
        )
    )
```

**Example:** September 2024: (€609,564.95 + €566,832.85 + €775,676.12) ÷ 3 = €650,691.31. August 2024: blank.

## Data quality measures

### Orders with Data Issues

**Meaning:** orders kept in the model but flagged by cleaning (`data_quality_issue = TRUE`). See [Data cleansing rules](Data-Cleansing-Rules.md).

```dax
Orders with Data Issues =
CALCULATE ( [Order Count], KEEPFILTERS ( Orders[data_quality_issue] = TRUE () ) )
```

**Example:** 4 (full 18 months); 5 with no Date slicer (`ORD-000001` to `ORD-000005`).

### Tickets with Data Issues

**Meaning:** tickets kept in the model but flagged by cleaning.

```dax
Tickets with Data Issues =
CALCULATE ( [Ticket Count], KEEPFILTERS ( Tickets[data_quality_issue] = TRUE () ) )
```

**Example:** 3 (full 18 months); 4 with no Date slicer (`TKT-000001` to `TKT-000004`).
