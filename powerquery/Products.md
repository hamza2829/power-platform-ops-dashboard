# Products query, in plain words

Load `products.csv`, trim product names, and keep the first row for each group. Convert targets to positive whole numbers of **calendar days**; unparseable or invalid targets become null. Expected result: **5 rows**.

This dimension has targets, not order events, so it has no actual lead time, dates or late flag. Orders uses its target only to estimate a missing promise; the estimate is flagged and excluded from on-time comparisons. No working-day calendar is implied. The script still needs a Desktop runtime check.
