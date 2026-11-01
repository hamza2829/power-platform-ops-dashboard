# Training: 45-minute onboarding for new users

[Wiki home](Home.md)

**Audience:** new analysts and report users. **Goal:** read the dashboard correctly, explain the main KPIs, and spot data-quality traps.

**Before the session (trainer):** build the report once with the [90-minute guide](../../report/BUILD_IN_90_MINUTES.md); there is no `.pbix` in the repo. If it is not built yet, do Exercises 1–2 on the CSV files and treat Exercises 3–6 as "predict the value" questions using the reference numbers.

**Trainee needs:** the repo folder, Power BI Desktop (for 3–6), a text editor or Excel.

## Outline

| Time | Block | Material |
| --- | --- | --- |
| 0–5 min | Context: fictional company, synthetic data, snapshot 31 Dec 2025, what is and isn't built | [Home](Home.md) |
| 5–12 min | Data model: two facts, three dimensions, six relationships, no Orders–Tickets link | [Data model](Data-Model.md) |
| 12–20 min | Cleansing: duplicates, nulls not zero, flags. **Exercises 1–2** | [Cleansing rules](Data-Cleansing-Rules.md) |
| 20–32 min | KPIs and the report pages. **Exercises 3–5** | [KPI definitions](KPI-Definitions.md), [User guide](User-Guide.md) |
| 32–40 min | Traps: date slicer, ratio > 100, YoY. **Exercise 6** | [FAQ](FAQ-and-Data-Quality.md) |
| 40–45 min | Questions, how to request a KPI | [Requirements template](Requirements-Template.md) |

## Exercises

**1. Duplicates.** Open `data/orders.csv`. How many data rows does it have, how many clean orders remain, and which value of ORD-000001 does the model keep: 1561.76 or 999999.00?

**2. Dirty records.** Using `data/manifest.json`, name the order with an invalid value. What does cleaning do with it, and is it still counted in Order Count?

**3. Full-period check.** With the Date slicer on 2024-07-01 – 2025-12-31 and nothing else selected, read Order Count, Ticket Count and On-Time Delivery Rate. Then clear the Date slicer. What changes and why?

**4. East.** Select region East. What is the On-Time Delivery Rate, and how does it compare with the overall rate?

**5. Sofa spike.** On After sales, select Sofas and September 2025. What are Ticket Count and Tickets per 100 Orders? Is a value above 100 an error?

**6. Priority filter.** Select priority High on After sales. What is Ticket Count? Would Order Count change if it were on this page?

## Answers

All values are from [`reference_totals.json`](../reference_totals.json) (Python reference). Power BI should match within displayed rounding.

1. 5,003 data rows → **5,000** clean orders. The **first** occurrence wins, so ORD-000001 keeps **1561.76**; the appended 999999.00 copy is removed.
2. **ORD-000004** (`not-a-number`). The value becomes **null, not 0**, and the row is flagged `data_quality_issue`. Total Revenue ignores it. Order Count **still counts it**.
3. **4,999** orders, **1,499** tickets, **71.5%** on-time. Without a Date slicer: **5,000 / 1,500** and on-time 71.47% (eligible 4,550 instead of 4,549). The difference is the undated order ORD-000003 and undated ticket TKT-000001: any date range excludes rows with no date.
4. East: **51.0%** (1,120 eligible, 549 late) vs **71.5%** overall. East has deliberately higher delays in the synthetic data.
5. **221 tickets**, **214.6 per 100 orders** (103 orders). Not an error: the ratio compares tickets *created* in September with orders *booked* in September, and these tickets relate to sofas delivered earlier (the fictional batch issue).
6. **295** tickets. **No**: priority is a Tickets column with no path to Orders, so Order Count stays **4,999**.

## Check yourself after the session

- [ ] I can say what "Total Revenue" includes and excludes.
- [ ] I know why Delivered Orders (4,552) ≠ Eligible Deliveries (4,549).
- [ ] I know which date the Date slicer filters for Orders and for Tickets.
- [ ] I know where to look up a dirty record ID.
