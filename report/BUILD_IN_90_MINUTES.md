# Build in Power BI Desktop in about 90 minutes

This is a time-boxed guide, not a claim that a report already exists. Allow longer if you are new to Desktop. You need Windows, Power BI Desktop installed, and the repo extracted/cloned to a local folder. No Docker, tenant, Power BI Service, gateway, Python integration in Power BI, or cloud refresh is needed. The four raw CSVs are already committed; Python is optional for building the report. UI labels can vary slightly by Desktop release.

## 0–15 minutes: load the four queries

1. Start Desktop > **Blank report**. File > Options and settings > Options > **Current File > Data Load**: turn off automatic relationship creation/detection and **Auto date/time**. If a similarly named setting is under Data Load > Relationships, disable it there. Save as `report/power-platform-ops-dashboard.pbix`.
2. Home > **Transform data** > Transform data to open Power Query Editor. Home > Manage parameters > **New parameter**. Name it exactly `DataFolder`, Type **Text**, Suggested values **Any value**, Current value your absolute `data` path, such as `C:\Projects\power-platform-ops-dashboard\data`. Do not include a trailing backslash or surrounding quotes in the parameter value.
3. Home > New source > Other sources > **Blank query**. Rename it **Products**. Home > **Advanced Editor**, replace all text with `powerquery/Products.pq`, Done. This is pasted code; opening a `.pq` file alone does not import it.
4. Repeat for **Customers** using `Customers.pq`, **Orders** using `Orders.pq`, then **Tickets** using `Tickets.pq`. Names and order matter because Orders refers to Products and Tickets refers to Orders. Do not create an additional raw-CSV import or automatic Changed Type steps.
5. If prompted about combining sources/privacy, set the local files to a consistent privacy level such as **Organizational**. Keep normal privacy checks; there is no need to enable global Fast Combine. Check parameter spelling and source path if File.Contents fails.
6. View > Column quality and Column profile; switch profiling to the **entire data set**. Check that there are no conversion-error cells. Nulls are deliberate. Close & Apply. In Table view verify **Customers 800, Products 5, Orders 5,000, Tickets 1,500**. These are clean totals with no date filter. Use `manifest.json` to locate deliberate problem IDs.

## 15–30 minutes: model and date table

7. Modeling > **New table**. Paste `dax/Date.dax`. Select Date > Table tools > **Mark as date table**, column `Date[Date]`. Set that column's data type to Date if necessary. It should have **1,461 dates** from 2023-01-01 to 2026-12-31.
8. Select `Date[Month]` > Column tools > Sort by column > `Month Number`. Sort `Date[Year Month]` by `Year Month Sort`.
9. Open Model view > Manage relationships. Delete any automatically inferred relationships in this new model, then create **only these six**. For each set cardinality dimension **One to many (1:*)**, cross-filter direction **Single** from dimension to fact, and **Make this relationship active**:

   | One-side column | Many-side column |
   | --- | --- |
   | `Customers[customer_id]` | `Orders[customer_id]` |
   | `Customers[customer_id]` | `Tickets[customer_id]` |
   | `Products[product_group]` | `Orders[product_group]` |
   | `Products[product_group]` | `Tickets[product_group]` |
   | `Date[Date]` | `Orders[order_date]` |
   | `Date[Date]` | `Tickets[created_date]` |

10. Check that each dimension key is unique. Do not accept a many-to-many or bidirectional relationship as a workaround. There is **no Orders–Tickets relationship**. There are no active relationships to promised, delivered or closed dates. Keep identifiers as text and numeric durations as whole numbers.

## 30–45 minutes: measures and formats

11. Select Orders > Modeling > **New measure**. Paste the first definition from `dax/measures.dax`. Repeat for each of the **16 definitions**, in file order. Do not paste all definitions at once. Ticket measures can also live in Orders; their formulas still read Tickets.
12. Set formats using `dax/README.md`: money to EUR, On-Time Delivery Rate and Revenue YoY % to percent, averages/ratio to one decimal, counts to whole numbers. If your formula separator is a semicolon rather than a comma, adapt the argument separators; quoted strings and dates must remain unchanged.
13. Temporarily add cards for Order Count and Ticket Count with **no slicers**: expect **5,000 / 1,500**. Add a Between slicer from `Date[Date]` (choose the column instead of Date hierarchy), set 2024-07-01 to 2025-12-31: expect **4,999 / 1,499** because each fact has one undated event. Compare revenue and eligible deliveries with `docs/reference_totals.json`, `slices.all_18_months_date_slicer`. Do not repair the difference by inventing dates.

## 45–70 minutes: three pages

14. Name the first page **Overview**; add two pages **Delivery performance** and **After sales**. Format canvas size **16:9**. Use `report/SPECIFICATION.md` as the exact visual/field checklist. Build the cards and charts first, formatting second.
15. Create slicers for Date, Customers region and Products group on Overview. View > **Sync slicers**: sync and show them on all three pages. Add a separate Tickets priority slicer only on After sales. Format > **Edit interactions**: verify slicers filter the intended visuals. Turn on chart data labels where legible.
16. Configure the late-order table's visual filter `Orders[late_flag] = True`, set raw numeric/date columns to **Don't summarize** or raw Date, and add the matrix and lead-time chart. Add After sales visuals, including priority/date slicers and the open-ticket worklist. Include the synthetic-data footer and business definitions from the spec.

## 70–80 minutes: drill-through and sanity checks

17. On Delivery performance, deselect visuals and add `Customers[region]` to the **Drill-through** fields well. Keep all filters **On**. Keep/add the Back button with Action **Back**. On Overview right-click the East regional bar > **Drill through > Delivery performance**. Confirm the late table is limited to East. Use Back (Ctrl+click in edit mode). Clear drill-through filters before taking unfiltered screenshots.
18. Compare East with `slices.east_all_18_months` in the reference JSON. On After sales choose Sofas and September 2025 and compare with `slices.sofas_september_2025`. Clear filters, choose High priority, and compare with `slices.high_priority_all_18_months`. Priority must not change an order count/revenue measure if you temporarily put one on that page.
19. Make the temporary YoY table described in the spec. July 2025 must match `time_intelligence_checks` in the JSON; August 2024 rolling average must be blank, September 2024 rolling average must match the reference. Allow rounding to displayed precision. Then restore the default full period and remove temporary QA visuals if desired.

## 80–90 minutes: save evidence

20. Save the PBIX. Take **real** screenshots of each finished page, after clearing drill-through and restoring the default date range; save `report/screenshots/overview.png`, `delivery-performance.png`, and `after-sales.png`. Replace the README screenshot placeholders with image links. Do not label wireframes or AI mockups as screenshots.
21. Update the user verification checkboxes in `docs/BUILD_STATUS.md` only for checks you actually performed. Keep optional automation marked design only until you build and smoke-test it in your own environment.
22. If the PBIX is **under 20 MB**, commit it at the exact allowed path `report/power-platform-ops-dashboard.pbix`. If larger, save it locally outside the repo or under an ignored filename and record that it is excluded in `report/README.md`. Do not force-add a large binary. No Service publish step is required.

## Finish checklist

- [ ] Set DataFolder and execute all four M queries; inspect the dirty IDs and row counts.
- [ ] Add/mark/sort Date and create exactly six single-direction 1:* relationships.
- [ ] Create all 16 measures and set their formats.
- [ ] Build Overview, Delivery performance and After sales with the specified slicers.
- [ ] Test region drill-through to the late-order table and the Back button.
- [ ] Compare full-period, East, sofa-spike, priority, YoY and rolling reference values.
- [ ] Save the PBIX, add three real screenshots, and update build/test status honestly.

To reopen later, double-click your saved PBIX, Transform data > Manage parameters > change DataFolder if the repo moved, then Close & Apply and Refresh. Without a PBIX, follow this guide from a blank report. A `.pq` or `.dax` file is source text, not an openable Power BI report.
