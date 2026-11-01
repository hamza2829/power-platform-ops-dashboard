# Data cleansing rules

[Wiki home](Home.md) · Scripts: [Products.pq](../../powerquery/Products.pq), [Customers.pq](../../powerquery/Customers.pq), [Orders.pq](../../powerquery/Orders.pq), [Tickets.pq](../../powerquery/Tickets.pq) · Dirty IDs: [manifest.json](../../data/manifest.json)

The four Power Query (M) scripts turn the raw CSVs in `data/` into clean model tables. Load order matters: **Products → Customers → Orders → Tickets**, because Orders joins Products and Tickets joins Orders.

The M scripts have **not yet been run in Power BI Desktop**. The "after" values below come from `tools/verify_data.py`, a Python copy of the same rules that CI runs.

## Rules at a glance

| Rule | What happens | Why |
| --- | --- | --- |
| **Trim text** | Leading and trailing spaces are removed from every text column | `"East "` and `"East"` must be the same region |
| **Explicit types** | ISO dates (`yyyy-MM-dd`) and dot decimals are parsed with culture `en-US` | Windows regional settings must not change the result |
| **Invalid → null** | An unparseable date or amount becomes null, **never 0** | Zero is a real value; unknown is not |
| **Duplicates** | Keep the **first** row per ID, in source file order (buffered index) | Predictable result even when the duplicate has different values |
| **Blank keys** | Rows with an empty ID are removed | A row without a key cannot join |
| **Standard values** | Blank region/segment → `Unknown`; priority not High/Medium/Low → `Unknown` | Bad values stay visible in visuals |
| **Impossible chronology** | Delivery before order, or closure before creation, is cleared to null | A date we cannot trust is not used in durations |
| **Missing promise** | Estimated as order date + product target, flagged `promise_imputed = true` | Keeps a promise for display, but the estimate is excluded from on-time % |
| **Flag, don't delete** | Problem rows stay in the table with `data_quality_issue = true` | Counts stay complete, and the problems remain findable |

Row counts: Orders 5,003 → **5,000**, Customers 801 → **800**, Tickets 1,502 → **1,500**, Products 6 → **5**.

## Columns added by cleaning

| Table | Column | Rule |
| --- | --- | --- |
| Orders | `promise_imputed` | true if promise is missing or before order date, and order date and product target exist |
| Orders | `lead_time_days` | delivered date − order date (calendar days), only for Delivered with both dates |
| Orders | `late_flag` | delivered > promised; null if not delivered, a date is missing, or the promise was imputed |
| Orders | `data_quality_issue` | order date, value or promise is null, or promise imputed, or Delivered without a delivery date |
| Tickets | `ticket_status` | Open if source closure is blank; Unknown if supplied but unusable; else Closed |
| Tickets | `resolution_days` | closed − created (calendar days), only when both dates are usable |
| Tickets | `customer_id`, `product_group` | copied from the cleaned Orders row with the same `order_id` |
| Tickets | `data_quality_issue` | creation date null, status Unknown, priority Unknown, or no matching order |

## Before and after examples (seed 42 data)

### Orders

| order_id | Raw problem | After cleaning |
| --- | --- | --- |
| ORD-000001 | `promised_date` blank (Bedroom, ordered 2024-07-01) | promised 2024-07-29 (+28 days), `promise_imputed` true, `late_flag` null, lead time 35, flagged |
| ORD-000002 | Delivered, `delivered_date` blank | stays Delivered; lead time and `late_flag` null, flagged |
| ORD-000003 | `order_date` blank | order date stays null (no invented date); lead time null, flagged |
| ORD-000004 | `order_value` = `not-a-number` | value null (not 0); still counted as an order, flagged |
| ORD-000005 | ordered 2025-11-14, delivered 2025-11-13 | delivered date cleared to null; lead time and `late_flag` null, flagged |

Raw vs clean for ORD-000004:

```text
Raw:   ORD-000004,CUS-0668,Office,2025-04-04,2025-04-18,2025-04-29,Delivered,not-a-number
Clean: order_value = null, lead_time_days = 25, late_flag = true, data_quality_issue = true
```

**Duplicates:** the last three rows of `orders.csv` repeat ORD-000001/2/3 with `order_value` 999999.00. The first occurrence wins, so the clean values are 1561.76, 1418.96 and 8001.18.

### Tickets

| ticket_id | Raw problem | After cleaning |
| --- | --- | --- |
| TKT-000001 | `created_date` blank, closed 2025-06-02 | status Closed, `resolution_days` null, flagged |
| TKT-000002 | `closed_date` = `tomorrow` | closed null, status **Unknown** (not Open), flagged |
| TKT-000003 | created 2024-11-21, closed 2024-01-01 | closed cleared, status Unknown, flagged |
| TKT-000004 | `priority` = `urgent?` | priority `Unknown`, resolution 4 days, flagged |

Duplicates TKT-000001 and TKT-000002 are appended at the end of the file and removed.

### Dimensions

- **Customers:** `CUS-0001,North,Retail` appears again as the last row; the duplicate is removed (800 rows).
- **Products:** `Sofas,28` appears twice; one row is kept (5 rows). Targets must be positive whole numbers, otherwise null.

## Not dirty

A blank `delivered_date` on an **Open** or **Cancelled** order, or a blank `closed_date` on an **Open** ticket, is normal and is not flagged.
