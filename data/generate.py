"""Generate four small CSVs with explicit, repeatable data-quality exercises.

Run from the repository root: python data/generate.py
Only Python's standard library is needed. Dates and money are serialized explicitly
so files have the same bytes on Windows and Ubuntu with the supported Python 3.12.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import io
import json
import random
from datetime import date, timedelta
from pathlib import Path

DEFAULT_SEED = 42
START_DATE = date(2024, 7, 1)
AS_OF_DATE = date(2025, 12, 31)
ORDER_COUNT = 5_000
TICKET_COUNT = 1_500
CUSTOMER_COUNT = 800
REGIONS = ("North", "South", "East", "West")
# group, calendar-day production target, typical order value in EUR
PRODUCTS = (
    ("Sofas", 28, 1800),
    ("Kitchens", 42, 6500),
    ("Dining", 21, 1100),
    ("Bedroom", 28, 1600),
    ("Office", 14, 700),
)
FIELDS = {
    "orders": ["order_id", "customer_id", "product_group", "order_date",
               "promised_date", "delivered_date", "status", "order_value"],
    "customers": ["customer_id", "region", "segment"],
    "service_tickets": ["ticket_id", "order_id", "created_date", "closed_date",
                        "category", "priority"],
    "products": ["product_group", "target_lead_time_days"],
}


def generate_clean(seed: int = DEFAULT_SEED) -> dict[str, list[dict[str, str]]]:
    """Build valid source records before introducing deliberate quality problems."""
    rng = random.Random(seed)  # local state; does not change global random state
    customers = [
        {"customer_id": f"CUS-{i:04d}", "region": REGIONS[(i - 1) % 4],
         "segment": rng.choices(["Retail", "Trade", "Hospitality"], [7, 2, 1])[0]}
        for i in range(1, CUSTOMER_COUNT + 1)
    ]
    products = [{"product_group": group, "target_lead_time_days": str(target)}
                for group, target, _ in PRODUCTS]
    days = (AS_OF_DATE - START_DATE).days + 1
    dates = [START_DATE + timedelta(days=i) for i in range(days)]
    # More orders in the autumn promotion season, fewer in January/February.
    weights = [1.6 if d.month in (9, 10, 11) else 0.8 if d.month in (1, 2) else 1.0
               for d in dates]
    orders = []
    for i in range(1, ORDER_COUNT + 1):
        customer = rng.choice(customers)
        group, target, price = rng.choices(PRODUCTS, [30, 15, 20, 20, 15])[0]
        ordered = START_DATE if i == 1 else AS_OF_DATE if i == ORDER_COUNT else rng.choices(dates, weights)[0]
        promised = ordered + timedelta(days=target + rng.randint(0, 7))
        late_chance = {"North": 0.16, "South": 0.22, "East": 0.46, "West": 0.18}[customer["region"]]
        late_chance += 0.08 if group == "Kitchens" else 0
        late_chance += 0.07 if ordered.month in (10, 11) else 0
        delay = rng.randint(1, 16) if rng.random() < late_chance else rng.randint(-7, 0)
        actual = promised + timedelta(days=delay)
        cancelled = rng.random() < 0.035
        status = "Cancelled" if cancelled else "Delivered" if actual <= AS_OF_DATE else "Open"
        orders.append({
            "order_id": f"ORD-{i:06d}", "customer_id": customer["customer_id"],
            "product_group": group, "order_date": ordered.isoformat(),
            "promised_date": promised.isoformat(),
            "delivered_date": actual.isoformat() if status == "Delivered" else "",
            "status": status, "order_value": f"{price * rng.uniform(0.7, 1.5):.2f}",
        })

    # Repeat complaints are possible: sample delivered orders with replacement.
    eligible = [o for o in orders if o["status"] == "Delivered"
                and o["delivered_date"] <= "2025-12-28"]
    ticket_weights = [3.5 if o["product_group"] == "Sofas" else
                      2.5 if o["product_group"] == "Kitchens" else 1.0 for o in eligible]
    tickets = []
    for i in range(1, TICKET_COUNT + 1):
        order = rng.choices(eligible, ticket_weights)[0]
        delivered = date.fromisoformat(order["delivered_date"])
        available_days = (AS_OF_DATE - delivered).days
        lag = rng.randint(1, min(30, available_days))
        created = delivered + timedelta(days=lag)
        # A fictional September 2025 sofa-batch issue, after delivery.
        if (order["product_group"] == "Sofas" and delivered <= date(2025, 9, 20)
                and rng.random() < 0.30):
            created = date(2025, 9, rng.randint(21, 30))
        category = rng.choices(["Damage", "Missing parts", "Assembly", "Warranty"],
                               [5 if order["product_group"] == "Sofas" else 2, 3, 2, 2])[0]
        priority = rng.choices(["High", "Medium", "Low"], [2, 5, 3])[0]
        resolution = rng.randint(1, 7) if priority == "High" else rng.randint(3, 21)
        closed = created + timedelta(days=resolution)
        still_open = rng.random() < 0.12 or closed > AS_OF_DATE
        tickets.append({
            "ticket_id": f"TKT-{i:06d}", "order_id": order["order_id"],
            "created_date": created.isoformat(),
            "closed_date": "" if still_open else closed.isoformat(),
            "category": category, "priority": priority,
        })
    return {"orders": orders, "customers": customers,
            "service_tickets": tickets, "products": products}


def inject_dirty_rows(clean: dict) -> tuple[dict, list[dict[str, str]]]:
    """Mutate a deep copy; document every affected key in the manifest."""
    tables = copy.deepcopy(clean)
    issues = []

    def record(table: str, row: dict, key: str, column: str, value: str, reason: str):
        row[column] = value
        issues.append({"table": table, "id": row[key], "column": column, "issue": reason})

    delivered = [o for o in tables["orders"] if o["status"] == "Delivered"]
    record("orders", delivered[0], "order_id", "promised_date", "", "missing promise; estimate from product target")
    record("orders", delivered[1], "order_id", "delivered_date", "", "delivered status but missing actual date")
    record("orders", delivered[2], "order_id", "order_date", "", "missing order date; retain undated record")
    record("orders", delivered[3], "order_id", "order_value", "not-a-number", "invalid numeric value; retain as null")
    bad_delivery = (date.fromisoformat(delivered[4]["order_date"]) - timedelta(days=1)).isoformat()
    record("orders", delivered[4], "order_id", "delivered_date", bad_delivery, "delivery before order; clear actual date")
    tickets = tables["service_tickets"]
    record("service_tickets", tickets[0], "ticket_id", "created_date", "", "missing creation date; retain undated record")
    record("service_tickets", tickets[1], "ticket_id", "closed_date", "tomorrow", "invalid date type; status Unknown")
    record("service_tickets", tickets[2], "ticket_id", "closed_date", "2024-01-01", "closure before creation; status Unknown")
    record("service_tickets", tickets[3], "ticket_id", "priority", "urgent?", "unrecognized priority; map to Unknown")
    for table, key, count in (("orders", "order_id", 3), ("service_tickets", "ticket_id", 2),
                              ("customers", "customer_id", 1), ("products", "product_group", 1)):
        for row in tables[table][:count]:
            duplicate = dict(row)
            if table == "orders":
                duplicate["order_value"] = "999999.00"  # conflicting later copy loses
            tables[table].append(duplicate)
            issues.append({"table": table, "id": row[key], "column": key,
                           "issue": "appended duplicate; first source occurrence wins"})
    return tables, issues


def csv_bytes(name: str, rows: list[dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS[name], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def write_dataset(output: Path, seed: int = DEFAULT_SEED) -> dict:
    tables, issues = inject_dirty_rows(generate_clean(seed))
    output.mkdir(parents=True, exist_ok=True)
    files = {}
    for name, rows in tables.items():
        payload = csv_bytes(name, rows)
        (output / f"{name}.csv").write_bytes(payload)
        files[f"{name}.csv"] = {"rows": len(rows), "sha256": hashlib.sha256(payload).hexdigest()}
    manifest = {"seed": seed, "start_date": START_DATE.isoformat(), "as_of_date": AS_OF_DATE.isoformat(),
                "currency": "EUR", "files": files, "deliberate_issues": issues}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    manifest = write_dataset(args.output, args.seed)
    for name, info in manifest["files"].items():
        print(f"{name}: {info['rows']} rows")
    print(f"Seed {args.seed}; snapshot {AS_OF_DATE}; {len(manifest['deliberate_issues'])} deliberate issues")


if __name__ == "__main__":
    main()
