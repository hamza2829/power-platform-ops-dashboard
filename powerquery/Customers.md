# Customers query, in plain words

Load `customers.csv` from the `DataFolder` text parameter. Treat IDs, regions and segments as text and trim spaces. Keep the first row for each customer ID, using a buffered source index to make that choice predictable. Remove blank keys; label empty region/segment values `Unknown`. Expected result: **800 rows** with unique customer IDs.

There are no dates or delivery metrics in this dimension. Lead time and late flags belong to Orders, not Customers. This M script is supplied for you to run and check in Desktop; it has not been executed by Python CI.
