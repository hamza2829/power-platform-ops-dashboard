# Operations Dashboard wiki

Internal wiki and training material for the data analysis team. Everything here describes what is **in this repository**. It does not describe a live production system.

## Current status: read this first

| Part | Status |
| --- | --- |
| Synthetic CSV data, Python generator, 28 tests | Built and tested ([verification](../VERIFICATION.md)) |
| Power Query scripts (`powerquery/*.pq`) | Written; **not yet run in Power BI Desktop** |
| 16 DAX measures + Date table (`dax/`) | Written; **not yet run in a Power BI model** |
| Power BI report (`.pbix`) | **Not built. There is no `.pbix` file in the repo.** Build it with the [90-minute guide](../../report/BUILD_IN_90_MINUTES.md) |
| Power Automate / Power Apps | Design documents only ([automation](../../automation/README.md)) |

Numbers in this wiki come from the Python reference calculator ([`reference_totals.json`](../reference_totals.json)), not from a Power BI screen. They are the values you should see once the report is built.

## What the dashboard shows

A three-page Power BI report for a **fictional furniture manufacturer's** order processing and after-sales team. All data is synthetic (seed 42, snapshot 31 Dec 2025, orders booked 1 Jul 2024 to 31 Dec 2025).

1. **Overview:** booked order value, order count, on-time delivery rate, tickets per 100 orders, monthly trends, revenue by region, data-quality counts.
2. **Delivery performance:** on-time rate by product group and region, lead time, list of late orders. Region drill-through from Overview lands here.
3. **After sales:** tickets by category, resolution time, priority mix, open-ticket worklist.

Built-in story to find: the **East** region has more late deliveries, and a **sofa batch issue** causes a ticket spike in **September 2025**.

## Who it is for

- **Service and operations managers:** check demand, missed delivery promises and support workload by region and product group.
- **Data analysts:** maintain the queries and measures, answer KPI questions, run the data checks.
- **New team members:** start with the [training](Training.md).

## Pages in this wiki

| Page | Use it when you want to… |
| --- | --- |
| [Data model](Data-Model.md) | understand the tables, keys and relationships |
| [Data cleansing rules](Data-Cleansing-Rules.md) | know what Power Query changes in the raw CSVs |
| [KPI definitions](KPI-Definitions.md) | look up any of the 16 measures |
| [User guide](User-Guide.md) | open the report and read its three pages |
| [Requirements template](Requirements-Template.md) | ask for a new KPI or report |
| [Training](Training.md) | run or follow the 45-minute onboarding session |
| [FAQ and data quality checks](FAQ-and-Data-Quality.md) | find out why a number looks wrong |

## Other sources in the repo

[Project README](../../README.md) · [Data dictionary](../../data/README.md) · [Report specification](../../report/SPECIFICATION.md) · [Build status](../BUILD_STATUS.md)

The CI check `tools/check_docs.py` keeps this wiki honest: it fails if a relative link breaks or if a DAX measure is missing from the KPI page.
