"""Small Python reference for the documented cleaning rules; NOT an M/DAX engine.

Write reference totals: python tools/verify_data.py
Verify committed input bytes and totals: python tools/verify_data.py --check
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from data.generate import DEFAULT_SEED, write_dataset  # noqa: E402

KEYS = {"orders": "order_id", "customers": "customer_id",
        "service_tickets": "ticket_id", "products": "product_group"}


def parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def clean_reference(raw: dict) -> dict:
    """Independent, readable reference used to calculate Desktop acceptance numbers."""
    tables = {}
    for table, key in KEYS.items():
        seen = set()
        rows = []
        for source in raw[table]:
            row = {k: v.strip() for k, v in source.items()}
            if not row[key] or row[key] in seen:
                continue
            seen.add(row[key])
            rows.append(row)
        tables[table] = rows

    for product in tables["products"]:
        try:
            target = Decimal(product["target_lead_time_days"])
            product["target_lead_time_days"] = int(target) if target > 0 and target == int(target) else None
        except (InvalidOperation, ValueError):
            product["target_lead_time_days"] = None
    products = {p["product_group"]: p for p in tables["products"]}
    for customer in tables["customers"]:
        for field in ("region", "segment"):
            customer[field] = customer[field] or "Unknown"
    for order in tables["orders"]:
        for field in ("order_date", "promised_date", "delivered_date"):
            order[field] = parse_date(order[field])
        try:
            order["order_value"] = Decimal(order["order_value"])
        except InvalidOperation:
            order["order_value"] = None
        ordered, promised, delivered = (order[f] for f in ("order_date", "promised_date", "delivered_date"))
        target = products.get(order["product_group"], {}).get("target_lead_time_days")
        bad_promise = promised is None or (ordered is not None and promised < ordered)
        imputed = bad_promise and ordered is not None and target is not None
        order["promise_imputed"] = imputed
        order["target_lead_time_days"] = target
        if imputed:
            order["promised_date"] = ordered + timedelta(days=target)
        if order["status"] != "Delivered" or (ordered and delivered and delivered < ordered):
            order["delivered_date"] = None
        delivered = order["delivered_date"]
        order["lead_time_days"] = (delivered - ordered).days if delivered and ordered else None
        order["late_flag"] = (delivered > order["promised_date"]) if (
            order["status"] == "Delivered" and delivered and order["promised_date"] and not imputed) else None
        order["data_quality_issue"] = (ordered is None or order["order_value"] is None
                                       or order["promised_date"] is None or imputed
                                       or (order["status"] == "Delivered" and delivered is None))

    orders = {o["order_id"]: o for o in tables["orders"]}
    for ticket in tables["service_tickets"]:
        closure_supplied = bool(ticket["closed_date"])
        ticket["created_date"] = parse_date(ticket["created_date"])
        ticket["closed_date"] = parse_date(ticket["closed_date"])
        created, closed = ticket["created_date"], ticket["closed_date"]
        if created and closed and closed < created:
            closed = ticket["closed_date"] = None
        ticket["ticket_status"] = "Open" if not closure_supplied else "Unknown" if closed is None else "Closed"
        ticket["resolution_days"] = (closed - created).days if closed and created else None
        if ticket["priority"] not in ("High", "Medium", "Low"):
            ticket["priority"] = "Unknown"
        parent = orders.get(ticket["order_id"], {})
        for field in ("customer_id", "product_group"):
            ticket[field] = parent.get(field)
        ticket["data_quality_issue"] = (created is None or ticket["ticket_status"] == "Unknown"
                                        or ticket["priority"] == "Unknown"
                                        or ticket["customer_id"] is None or ticket["product_group"] is None)
    return tables


def mean(values: list) -> float | None:
    return round(sum(values) / len(values), 6) if values else None


def totals(tables: dict, start: date | None = None, end: date | None = None,
           region: str | None = None, group: str | None = None, priority: str | None = None) -> dict:
    customers = {c["customer_id"]: c for c in tables["customers"]}

    def selected(row: dict, field: str) -> bool:
        if start and (row[field] is None or not start <= row[field] <= end):
            return False
        return ((region is None or customers[row["customer_id"]]["region"] == region)
                and (group is None or row["product_group"] == group))

    orders = [o for o in tables["orders"] if selected(o, "order_date")]
    tickets = [t for t in tables["service_tickets"] if selected(t, "created_date")
               and (priority is None or t["priority"] == priority)]
    eligible = [o for o in orders if o["late_flag"] is not None]
    late = sum(o["late_flag"] is True for o in orders)
    revenue = sum((o["order_value"] for o in orders if o["status"] != "Cancelled"
                   and o["order_value"] is not None), Decimal("0"))
    return {
        "Order Count": len(orders), "Total Revenue": float(revenue),
        "Delivered Orders": sum(o["status"] == "Delivered" for o in orders),
        "Eligible Deliveries": len(eligible), "Late Orders": late,
        "On-Time Delivery Rate": round((len(eligible) - late) / len(eligible), 6) if eligible else None,
        "Average Lead Time Days": mean([o["lead_time_days"] for o in orders if o["lead_time_days"] is not None]),
        "Ticket Count": len(tickets),
        "Tickets per 100 Orders": round(len(tickets) * 100 / len(orders), 6) if orders else None,
        "Average Ticket Resolution Days": mean([t["resolution_days"] for t in tickets if t["resolution_days"] is not None]),
        "Open Tickets": sum(t["ticket_status"] == "Open" for t in tickets),
        "Orders with Data Issues": sum(o["data_quality_issue"] for o in orders),
        "Tickets with Data Issues": sum(t["data_quality_issue"] for t in tickets),
    }


def build_report(data_dir: Path) -> dict:
    raw = {}
    for name in KEYS:
        with (data_dir / f"{name}.csv").open(encoding="utf-8", newline="") as stream:
            raw[name] = list(csv.DictReader(stream))
    cleaned = clean_reference(raw)
    slices = {
        "unfiltered_no_date_slicer": totals(cleaned),
        "all_18_months_date_slicer": totals(cleaned, date(2024, 7, 1), date(2025, 12, 31)),
        "east_all_18_months": totals(cleaned, date(2024, 7, 1), date(2025, 12, 31), region="East"),
        "sofas_september_2025": totals(cleaned, date(2025, 9, 1), date(2025, 9, 30), group="Sofas"),
        "high_priority_all_18_months": totals(cleaned, date(2024, 7, 1), date(2025, 12, 31), priority="High"),
    }
    monthly = {}
    for year, months in ((2024, range(7, 13)), (2025, range(1, 13))):
        for month in months:
            first = date(year, month, 1)
            next_month = date(year + (month == 12), month % 12 + 1, 1)
            monthly[first.strftime("%Y-%m")] = totals(cleaned, first, next_month - timedelta(days=1))
    july_2024 = monthly["2024-07"]["Total Revenue"]
    july_2025 = monthly["2025-07"]["Total Revenue"]
    return {
        "scope": "Python reference only; compare these numbers manually in Power BI Desktop",
        "seed": DEFAULT_SEED,
        "raw_rows": {name: len(rows) for name, rows in raw.items()},
        "clean_rows": {name: len(rows) for name, rows in cleaned.items()},
        "slices": slices, "monthly": monthly,
        "time_intelligence_checks": {
            "Revenue Previous Year for July 2025": july_2024,
            "Revenue YoY % for July 2025": round((july_2025 - july_2024) / july_2024, 6),
            "Revenue Rolling 3 Month Average for September 2024": round(sum(
                monthly[m]["Total Revenue"] for m in ("2024-07", "2024-08", "2024-09")) / 3, 6),
            "Revenue Rolling 3 Month Average for August 2024": None,
        },
    }


def report_text(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True) + "\n"


def verify_committed(data_dir: Path, report_path: Path) -> None:
    # Rebuild in a temporary directory; verify both the manifest and every CSV byte.
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as temp:
        generated = Path(temp)
        write_dataset(generated)
        for name in ["manifest.json", *(f"{t}.csv" for t in KEYS)]:
            if (generated / name).read_bytes() != (data_dir / name).read_bytes():
                raise ValueError(f"Committed data differs from seed 42: {name}")
    manifest = json.loads((data_dir / "manifest.json").read_text(encoding="utf-8"))
    for name, info in manifest["files"].items():
        if hashlib.sha256((data_dir / name).read_bytes()).hexdigest() != info["sha256"]:
            raise ValueError(f"Checksum mismatch: {name}")
    if report_path.read_text(encoding="utf-8") != report_text(build_report(data_dir)):
        raise ValueError("Reference totals are stale; run python tools/verify_data.py")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data_dir, report_path = ROOT / "data", ROOT / "docs" / "reference_totals.json"
    if args.check:
        verify_committed(data_dir, report_path)
        print("PASS: seed-42 CSV bytes, manifest checksums, and Python reference totals")
    else:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_text(build_report(data_dir)), encoding="utf-8", newline="\n")
        print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
