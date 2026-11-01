# User guide

[Wiki home](Home.md) · Full visual list: [report specification](../../report/SPECIFICATION.md)

> **There is no `.pbix` report file in this repository yet.** Someone on the team must build it once with the [90-minute build guide](../../report/BUILD_IN_90_MINUTES.md). This guide describes the report as specified.

## Open the report

You need Windows with **Power BI Desktop**. No Power BI Service, gateway or tenant is used.

1. Clone or download the repo to a local folder.
2. **If `report/power-platform-ops-dashboard.pbix` exists:** double-click it.
   **If it does not:** follow the [build guide](../../report/BUILD_IN_90_MINUTES.md). A `.pq` or `.dax` file is source text and cannot be opened as a report.
3. If refresh fails because the folder moved: **Transform data → Manage parameters → `DataFolder`**, enter the absolute path of your `data` folder (no trailing `\`), then **Close & Apply** and **Refresh**.
4. Check the footer: *Synthetic data | Snapshot 31 Dec 2025 | Calendar days | EUR*.

## Use the filters

| Slicer | Pages | What it filters |
| --- | --- | --- |
| **Date** (Between) | All, synced | Orders by **booking** date, Tickets by **creation** date |
| **Region** (`Customers[region]`) | All, synced | Orders and Tickets |
| **Product group** (`Products[product_group]`) | All, synced | Orders and Tickets |
| **Priority** (`Tickets[priority]`) | After sales only | Tickets only; order numbers do not change |

Tips:

- Default Date range: **2024-07-01 to 2025-12-31**. Any date range hides the one undated order and the one undated ticket. Clear the Date slicer to see all 5,000 / 1,500.
- Click a bar or matrix cell to cross-filter the other visuals on the page. Click it again to clear.
- Hover over a visual for tooltips (for example, Order Count and On-Time Delivery Rate on the region bar).

## Page 1: Overview

- **Cards:** Booked order value (EUR), Order Count, On-Time Delivery Rate, Ticket creations per 100 bookings.
- **Revenue trend:** monthly Total Revenue with the Rolling 3 Month Average line. The rolling line starts in September 2024.
- **Revenue by region:** bar chart. Right-click a bar → **Drill through → Delivery performance** to see that region's late orders.
- **Tickets by month:** look for the September 2025 spike; set Product group = Sofas to see that it comes from sofas.
- **Data issue cards:** Orders with Data Issues and Tickets with Data Issues. These rows are kept and flagged ([why](Data-Cleansing-Rules.md)).

## Page 2: Delivery performance

- **Cards:** Delivered Orders, Eligible Deliveries, Late Orders, Average Lead Time Days. Delivered minus Eligible = deliveries we cannot judge.
- **Matrix:** On-Time Delivery Rate by product group (rows) and region (columns). The East column is lower.
- **Lead time bar:** Average Lead Time Days per product group.
- **Late order table:** every order with `late_flag` = true, newest delivery first.
- After a drill-through, use the **Back** button (Ctrl+click while editing) to return to Overview.

## Page 3: After sales

- **Cards:** Ticket Count, Open Tickets ("still open at snapshot"), Average Ticket Resolution Days.
- **Tickets by category:** bar chart, largest first.
- **Resolution trend:** average resolution days by **creation** month.
- **Priority mix:** stacked columns by month; `Unknown` is shown on purpose.
- **Open-ticket worklist:** table filtered to `ticket_status` = Open.
- **Priority slicer:** affects this page's ticket visuals only.

## Reading the numbers correctly

- **Total Revenue** = booked value of non-cancelled orders, not invoiced revenue.
- **Tickets per 100 Orders** can be above 100; it is a workload ratio, not a complaint rate.
- **YoY %** is only like-for-like for July–December 2025.

More in [KPI definitions](KPI-Definitions.md) and the [FAQ](FAQ-and-Data-Quality.md).
