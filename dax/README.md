# Model and measure notes

Create queries named exactly `Customers`, `Products`, `Orders`, `Tickets`, then the `Date` calculated table. Mark Date as the date table using `Date[Date]`. Sort `Date[Month]` by `Month Number` and `Year Month` by `Year Month Sort`. Use **Date columns**, not automatic date hierarchies. Disable automatic relationship detection and auto date/time for this file; create the six relationships in the root README manually.

Orders is one order per row; it is not an order-line fact. Tickets is one service ticket per row. Products is one product **group**, not one SKU. The lookup from Tickets to Orders happens during Power Query, not as a model relationship. Use only dimension fields in shared slicers.

All six relationships are active, single direction, dimension **1** to fact **many**. Date filters Orders by `order_date` and Tickets by `created_date`. Do not connect delivered/closed dates in this beginner model; analyzing those date roles is a later extension. A Date selection is therefore two different event clocks, not an order cohort.

Copy [Date.dax](Date.dax) into **New table**. Copy each definition in [measures.dax](measures.dax) into **New measure**, one at a time; comments are included. Use Orders as the home table for consistency, including ticket measures. Hiding raw numeric columns from report view is optional. Do not paste the whole measures file into a single formula bar.

| Measure | What it does and why | Format |
| --- | --- | --- |
| Total Revenue | Sums non-cancelled booked order value to compare demand in EUR; not recognized revenue. | EUR, 0 decimals |
| Order Count | Counts all orders to show workload, including cancelled/open orders. | Whole number |
| Delivered Orders | Counts delivered statuses to separate completed orders from workload. | Whole number |
| Eligible Deliveries | Uses CALCULATE and FILTER to count deliveries with a reliable late flag, defining the on-time denominator. | Whole number |
| Late Orders | Counts deliveries after an original valid promise to show missed commitments. | Whole number |
| On-Time Delivery Rate | Divides eligible on-time deliveries by eligible deliveries to avoid counting unknowns as successes. | Percentage, 1 decimal |
| Average Lead Time Days | Averages known actual calendar-day lead times to show fulfillment speed. | Decimal, 1 place |
| Ticket Count | Counts service events to show after sales workload. | Whole number |
| Tickets per 100 Orders | Compares ticket creations with order bookings in the period to show relative workload, not complaint incidence. | Decimal, 1 place |
| Average Ticket Resolution Days | Averages known completed durations to show service speed; open tickets contribute no duration. | Decimal, 1 place |
| Open Tickets | Counts tickets still open at 2025-12-31 among selected creation dates to show snapshot backlog. | Whole number |
| Revenue Previous Year | Uses SAMEPERIODLASTYEAR to retrieve the matching prior-year booked value. | EUR, 0 decimals |
| Revenue YoY % | Shows proportional change against prior-year value when both periods have data. | Percentage, 1 decimal |
| Revenue Rolling 3 Month Average | Averages three full calendar months of booked value to smooth the monthly trend. | EUR, 0 decimals |
| Orders with Data Issues | Counts flagged orders to expose cleaning limits instead of hiding them. | Whole number |
| Tickets with Data Issues | Counts flagged tickets to expose uncertain dates and priority. | Whole number |

`DIVIDE` returns blank if its denominator is zero/blank. Null values become DAX BLANK; zero is not a substitute for unknown. AVERAGE excludes blanks. The on-time denominator excludes open/cancelled orders, missing actuals, and imputed promises. Compare the eligible count with Delivered Orders so the exclusions stay visible.

Only July–December 2025 has a complete matching prior-year month in this 18-month sample. Filter to those months when demonstrating YoY; an all-2025 comparison with the partial 2024 history is not like-for-like. The rolling measure requires three full months in the source, treats an empty month inside that coverage as zero, and returns blank before September 2024. It intentionally looks before the slicer's start, preserves region/product filters, and should be demonstrated on a monthly axis. It is not a trailing 90-day average.

These are reviewed formulas, **not executed DAX tests**. Python reference totals support manual Desktop checks but cannot validate DAX filter context or M execution. Microsoft references: [star schema guidance](https://learn.microsoft.com/en-us/power-bi/guidance/star-schema), [CALENDAR](https://learn.microsoft.com/en-us/dax/calendar-function-dax), [CALCULATE](https://learn.microsoft.com/en-us/dax/calculate-function-dax), [SAMEPERIODLASTYEAR](https://learn.microsoft.com/en-us/dax/sameperiodlastyear-function-dax).
