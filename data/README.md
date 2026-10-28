# Synthetic data contract

The committed CSVs are UTF-8, comma-separated, with headers, LF newlines, ISO `yyyy-mm-dd` dates and dot-decimal **EUR** values. Dates span order bookings from **2024-07-01 to 2025-12-31**, inclusive (18 months). Promises can extend beyond the snapshot. Actual deliveries, ticket creations and closures never extend beyond it in the clean generator output. No personal names, contact details, addresses, or real company records are used.

| CSV | Grain / primary key | Unique logical records | Raw rows including duplicates |
| --- | --- | ---: | ---: |
| orders.csv | One order / order_id | 5,000 | 5,003 |
| customers.csv | One customer / customer_id | 800 | 801 |
| service_tickets.csv | One ticket / ticket_id | 1,500 | 1,502 |
| products.csv | One product group / product_group | 5 | 6 |

## Columns

| Table | Column | Meaning / intended cleaned type |
| --- | --- | --- |
| orders | order_id | Unique business order ID, text ORD-000001 etc. |
| | customer_id | Foreign key to customers, text |
| | product_group | Foreign key to products, text |
| | order_date | Booking date, Date; one deliberate missing date retained |
| | promised_date | Original delivery promise, Date; if absent, a flagged estimate may be added in M |
| | delivered_date | Actual delivery date, Date or null |
| | status | Delivered / Open / Cancelled, text; status is as of 2025-12-31 |
| | order_value | Full-order booked value in EUR, fixed decimal; not invoiced revenue |
| customers | customer_id | Unique customer ID, text CUS-0001 etc. |
| | region | Fictional operating region North / South / East / West |
| | segment | Retail / Trade / Hospitality |
| service_tickets | ticket_id | Unique ticket ID, text TKT-000001 etc. |
| | order_id | Foreign key to orders, text; multiple tickets can reference one order |
| | created_date | Business ticket creation date, Date; one deliberate missing date |
| | closed_date | Closure date, Date or null; original blank means still open |
| | category | Damage / Missing parts / Assembly / Warranty |
| | priority | High / Medium / Low; one deliberate invalid value maps to Unknown |
| products | product_group | Unique group name: Sofas / Kitchens / Dining / Bedroom / Office |
| | target_lead_time_days | Positive whole calendar days: 28 / 42 / 21 / 28 / 14 respectively |

## How the patterns are made

`generate.py` uses a private `random.Random(seed)` instance. Customers are evenly assigned to four fictional regions, with weighted segments. Autumn receives more orders. Each product group has a different target and price range. Delivery delay probability is higher in East, for Kitchens, and in the autumn; generated actual dates after the snapshot leave an order Open. About 3.5% of orders are cancelled.

Tickets are sampled with replacement from orders delivered before the cutoff, so repeat complaints are possible. Sofas and Kitchens have higher complaint weights. A fictional sofa batch issue moves some tickets into September 2025, after delivery; this intentionally creates a visible service spike. High-priority tickets have shorter generated resolution times. Some tickets remain open. These are scenario assumptions, not evidence about any real manufacturer, and no real causal model is claimed.

## Deliberate dirt and the cleaning decision

`manifest.json` lists the exact affected IDs for every seed, row counts and SHA-256 checksums. There are **16 recorded issues**: 9 modified cells and 7 appended duplicates. Originals precede duplicates; the first occurrence wins even when a later order copy has a conflicting value.

| Issue | Count | Cleaning rule |
| --- | ---: | --- |
| Missing order promise | 1 | Estimate order date + product target; flag promise_imputed; exclude from on-time eligibility |
| Delivered order missing actual date | 1 | Keep status and row, actual/lead time/late flag remain null |
| Missing order date | 1 | Keep undated row; no made-up booking date or lead time |
| Wrong order value type (`not-a-number`) | 1 | Null value with a data-quality flag; SUM ignores it, order count keeps it |
| Delivery before order | 1 | Clear impossible actual date and flag it |
| Missing ticket creation date | 1 | Keep undated ticket; exclude unknown duration |
| Wrong ticket closure type (`tomorrow`) | 1 | Null closure, Unknown status and duration |
| Ticket closure before creation | 1 | Null closure, Unknown status and duration |
| Wrong priority (`urgent?`) | 1 | Unknown priority with a quality flag |
| Duplicate orders/tickets/customers/products | 3 / 2 / 1 / 1 | Buffer source order and keep first key |

Other blank actual/closure dates are normal for open/cancelled work; they are not necessarily dirty. Dimensions have no dates or lead time columns because those business events belong in facts. Tickets gets resolution_days rather than a fabricated delivery late flag.

## Reproduce and check

From the repo root, using Python **3.12** for exact committed-byte reproduction:

```powershell
python data/generate.py
python tools/verify_data.py
python tools/verify_data.py --check
```

Use `python data/generate.py --seed 123 --output data-experiment` for an experiment; default committed artifacts and reference numbers always use seed 42. Generating into the default `data` directory replaces only the four named CSVs and manifest. The checker deliberately rejects a different seed in the committed dataset. After intentionally changing the generator, regenerate default data and reference totals, run tests, and review the diffs together.

There are no pandas/numpy/runtime dependencies. `pytest` is needed only for tests. Python's random algorithm behavior is tied to the supported interpreter version; cross-version byte identity is not promised. The Python reference cleaner in `tools/verify_data.py` is an acceptance-number calculator, not a substitute for executing M/DAX in Power BI.
