# Execution and authorship status

Prepared on **28 October 2026** with AI assistance in Codex. This file records what has evidence; it does not say the user has personally executed something they have not reported doing.

| Part | Current state | Evidence / owner |
| --- | --- | --- |
| Python seeded generator and raw CSVs | Implemented and executed by Codex on Windows, Python 3.12.14 | `data/manifest.json`, four CSVs; seed 42 |
| Generator/data-contract tests | **28 tests passed locally** | `python -m pytest -q`; see local execution note below |
| Committed data and reference checker | Executed, passed | `python tools/verify_data.py --check` |
| Ubuntu GitHub Actions | **28 tests passed; data/reference checker passed** | [Successful run](https://github.com/hamza2829/power-platform-ops-dashboard/actions/runs/40704930392); `docs/VERIFICATION.md` |
| Power Query M | Source written and reviewed, **not executed in Desktop** | Four .pq files and explanations |
| DAX and model | Source/specification written and reviewed, **not executed in a semantic model** | `dax/` and root model diagram |
| Power BI report / PBIX | **Not built** | User will build locally; no PBIX supplied |
| Screenshots | **Not captured** | Placeholders only; user will add real captures |
| Optional Power Automate | **Design documents only; not built/tested** | `automation/POWER_AUTOMATE.md` |
| Optional Power Apps | **Design documents only; not built/tested** | `automation/POWER_APPS.md` |
| Power BI Service deployment | **Not performed** | No workspace, gateway, scheduled refresh or cloud deployment configured |

The Codex environment used its bundled Python runtime and an ignored `.test-deps` directory for pytest. An existing Windows temp-folder permission issue required `--basetemp=.pytest-local-run1` for the successful local run. That is a local runner detail; normal installs can use a virtual environment and `python -m pytest -q`. The Ubuntu workflow uses a clean Python 3.12 environment.

## User's own Desktop verification log — pending

Check only after doing each step yourself. Add date, Desktop version, result and evidence path below the checklist. These are deliberately not pre-checked by AI.

- [ ] Ran all M queries and inspected the 16 dirty-data cases.
- [ ] Confirmed clean row counts and exactly six model relationships.
- [ ] Created Date/16 measures and checked the reference totals, including time intelligence.
- [ ] Built all three report pages and tested slicer interactions and region drill-through.
- [ ] Saved PBIX and captured real screenshots.
- [ ] Can explain date roles, ticket ratio, missing-date handling and on-time denominator.
- [ ] Optional flow built and smoke-tested; evidence recorded (otherwise remains design only).
- [ ] Optional app built and smoke-tested; evidence recorded (otherwise remains design only).

Verification date: _pending_

Desktop version: _pending_

Personal observations and evidence: _pending_
