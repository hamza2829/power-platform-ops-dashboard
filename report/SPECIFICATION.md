# Three-page report specification

Build a simple 16:9 report. Use a white background, dark blue headings, blue bars, and orange for late orders. Show a footer on every page: **Synthetic data | Snapshot 31 Dec 2025 | Calendar days | EUR**. Avoid red/green as the only indicator. Give every visual a descriptive title and alt text. Field names below are exact; square brackets mean measures from `dax/measures.dax`.

Default Date slicer range: **2024-07-01 through 2025-12-31**. Date filters order bookings and ticket creations, not delivery/closure events. Shared region and product slicers must use Customers and Products. Sync the Date, region and product slicers across pages; do not sync ticket priority to other pages. Set slicer interaction to **Filter** for every relevant visual.

## 1. Overview

Purpose: show booked demand, delivery reliability, and service workload.

| Position / visual | Fields / measures | Settings |
| --- | --- | --- |
| Top row: four cards | `[Total Revenue]`, `[Order Count]`, `[On-Time Delivery Rate]`, `[Tickets per 100 Orders]` | Revenue label: "Booked order value (EUR)"; ticket ratio label: "Ticket creations per 100 bookings" |
| Middle left: line chart | X: `Date[Year Month]`; Y: `[Total Revenue]`, `[Revenue Rolling 3 Month Average]` | Categorical ascending axis, sorted Year Month; show both legend labels |
| Middle right: clustered bar | Y: `Customers[region]`; X: `[Total Revenue]` | Tooltip: `[Order Count]`, `[On-Time Delivery Rate]`; region is also the drill-through source |
| Bottom left: clustered column | X: `Date[Year Month]`; Y: `[Ticket Count]` | Exposes the fictional September 2025 sofa spike; product slicer narrows it |
| Bottom right: small cards | `[Orders with Data Issues]`, `[Tickets with Data Issues]` | Explain that dirty records are retained, flagged and excluded from unsuitable averages |
| Top/left slicers | `Date[Date]` (Between), `Customers[region]` (dropdown), `Products[product_group]` (dropdown) | Use raw Date, not Date hierarchy |

A regional bar is used instead of a map because North/South/East/West are fictional operating regions without geographic boundaries. Add a text note: "Revenue is non-cancelled booked value; tickets can relate to earlier orders."

## 2. Delivery performance

Purpose: identify product/region problems and inspect late orders. This page is also the **drill-through destination**, keeping the report to three pages.

| Position / visual | Fields / measures | Settings |
| --- | --- | --- |
| Top row: cards | `[Delivered Orders]`, `[Eligible Deliveries]`, `[Late Orders]`, `[Average Lead Time Days]` | Explain the gap between delivered and assessable deliveries |
| Middle left: matrix | Rows: `Products[product_group]`; Columns: `Customers[region]`; Values: `[On-Time Delivery Rate]` | Percentage, 1 decimal; conditional formatting with numeric values still shown |
| Middle right: clustered bar | Y: `Products[product_group]`; X: `[Average Lead Time Days]` | Tooltip: `[Eligible Deliveries]`, `[Late Orders]` |
| Bottom: late order table | `Orders[order_id]`, `Customers[region]`, `Products[product_group]`, `Orders[order_date]`, `Orders[promised_date]`, `Orders[delivered_date]`, `Orders[lead_time_days]`, `Orders[order_value]` | Visual filter: `Orders[late_flag]` is True. Set numeric columns to Don't summarize. Sort delivered date descending |
| Slicers | Same Date, Customers region and Products group fields as Overview | Sync shared slicers |

**Region drill-through:** with no visual selected, add `Customers[region]` to this page's Drill-through field well in the Visualizations/Build pane. Use **Keep all filters = On** so the source date/product context is passed too. Power BI adds a Back button; if it does not, Insert > Buttons > Back, Action = Back. On Overview, right-click an East bar > Drill through > Delivery performance. The destination late-order table shows that region's late orders. Return with Back (Ctrl+click in edit mode).

This implements region-to-late-order-detail drill-through. An order-specific ticket drill-through would need an additional design for order filtering across both facts; it is not part of these three pages. Do not add an Orders-to-Tickets relationship just to make that work.

## 3. After sales

Purpose: investigate service categories, priorities and resolution speed.

| Position / visual | Fields / measures | Settings |
| --- | --- | --- |
| Top row: cards | `[Ticket Count]`, `[Open Tickets]`, `[Average Ticket Resolution Days]` | Label Open Tickets "Still open at snapshot"; it is not a historical backlog calculation |
| Middle left: clustered bar | Y: `Tickets[category]`; X: `[Ticket Count]` | Sort descending; tooltip `[Average Ticket Resolution Days]` |
| Middle right: line chart | X: `Date[Year Month]`; Y: `[Average Ticket Resolution Days]` | Ticket **creation** month, not closure month |
| Bottom left: stacked column | X: `Date[Year Month]`; Y: `[Ticket Count]`; Legend: `Tickets[priority]` | Include Unknown priority so the bad source value remains visible |
| Bottom right: table | `Tickets[ticket_id]`, `Tickets[order_id]`, `Tickets[created_date]`, `Tickets[closed_date]`, `Tickets[ticket_status]`, `Tickets[priority]`, `Tickets[resolution_days]` | Filter `ticket_status` to Open for an open-ticket worklist; Don't summarize durations |
| Slicers | `Tickets[priority]` (dropdown); `Date[Date]` (Between); `Customers[region]`; `Products[product_group]` | Priority affects Tickets only. Date, region and product use the synced slicers |

For a YoY interview demonstration, temporarily make a small table on Overview with `Date[Year Month]`, `[Total Revenue]`, `[Revenue Previous Year]`, `[Revenue YoY %]`, filtered to July–December 2025. Remove it after checking if the page is crowded. This is a QA step, not a fourth report page.
