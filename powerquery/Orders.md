# Orders query, in plain words

Load `orders.csv`; keep the first occurrence of each order ID **before** doing joins. Explicitly parse ISO dates and dot-decimal values so Windows regional settings do not change the result. Invalid values become null, never zero. Join Products to get its target. Expected result: **5,000 rows**.

If the promise is absent or before the order date, use order date plus the product target when possible and set `promise_imputed = true`. Keep missing order dates as null. Clear impossible actual dates before the order date. A delivered order with a missing actual date stays Delivered, but its delivery metrics are unknown. `data_quality_issue` makes these records findable.

`lead_time_days` is actual delivery minus order date for delivered orders with known dates. `late_flag` is true/false only for delivered orders with a known actual and an original, valid promise; otherwise it is null. A delivery on its promised date is on time. Open and cancelled orders are not measured as delivered. An undated order remains in unfiltered counts but disappears when a Date slicer selects a real date range. The generated reference totals show both cases; verify M in Desktop yourself.
