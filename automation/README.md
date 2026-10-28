# Optional: design documents only

**Neither the flow nor the canvas app has been built, imported, deployed or tested.** There is no exported flow package, `.msapp`, SharePoint connection, Teams message, or email sent by this repo. These designs are optional interview discussion material until you implement and test them yourself. They do not run in CI.

Use [the SharePoint contract](SHAREPOINT_SCHEMA.md), [flow design](POWER_AUTOMATE.md), and [canvas app formulas](POWER_APPS.md) together. SharePoint is the chosen storage option because it has a straightforward item-created trigger and better multiuser behavior than an Excel file. The design uses email for notification; Teams is an optional substitution. You need your own Microsoft 365 environment, permissions and appropriate connector licensing; these are not needed for the local Power BI project.

The synthetic CSV dashboard is a **separate fixed snapshot**. The optional app and flow do not update its CSVs or the report automatically. Connecting live SharePoint data would require new queries, field mapping (for example SharePoint ID to ticket ID), security/refresh decisions and separate testing.

After implementation, record the environment, test date, tested scenarios and actual evidence in `docs/BUILD_STATUS.md`. Change status only for parts that you really built.
