# Report deliverables

**Current status: report not built; no PBIX supplied.** Build it locally using [the 90-minute guide](BUILD_IN_90_MINUTES.md) and [the page specification](SPECIFICATION.md). The user owns Desktop execution and visual validation.

Save a finished report under `report/power-platform-ops-dashboard.pbix` only if it is under the project's **20 MB** binary budget. That exact filename is allowed by `.gitignore`; all other `report/*.pbix` files are ignored by default. For a larger PBIX, keep it outside Git, leave source CSV/M/DAX/specifications here, and change this note to say **PBIX excluded due to size**. Nothing currently depends on a binary or on Power BI Service.

Once present, open the PBIX in Power BI Desktop. If refresh fails because the folder moved, edit the DataFolder parameter to your local absolute `data` folder, then refresh. The snapshot does not advance to today's date automatically.
