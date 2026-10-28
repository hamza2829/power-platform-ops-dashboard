import copy
import csv
import json
import random
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import pytest

from data.generate import (AS_OF_DATE, FIELDS, START_DATE, generate_clean,
                           inject_dirty_rows, write_dataset)
from tools.verify_data import build_report, clean_reference, verify_committed

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def clean():
    return generate_clean()


@pytest.fixture(scope="module")
def raw(clean):
    return inject_dirty_rows(clean)[0]


@pytest.mark.parametrize("table,count", [("orders", 5000), ("customers", 800),
                                          ("service_tickets", 1500), ("products", 5)])
def test_clean_row_counts(clean, table, count):
    assert len(clean[table]) == count
    key = FIELDS[table][0]
    assert len({r[key] for r in clean[table]}) == count


@pytest.mark.parametrize("table,count", [("orders", 5003), ("customers", 801),
                                          ("service_tickets", 1502), ("products", 6)])
def test_raw_row_counts(raw, table, count):
    assert len(raw[table]) == count


@pytest.mark.parametrize("table", list(FIELDS))
def test_csv_schema(raw, table):
    assert all(list(row) == FIELDS[table] for row in raw[table])


@pytest.mark.parametrize("dirty", [False, True])
def test_foreign_keys(clean, raw, dirty):
    tables = raw if dirty else clean
    customers = {r["customer_id"] for r in tables["customers"]}
    products = {r["product_group"] for r in tables["products"]}
    orders = {r["order_id"] for r in tables["orders"]}
    assert all(o["customer_id"] in customers and o["product_group"] in products for o in tables["orders"])
    assert all(t["order_id"] in orders for t in tables["service_tickets"])


def test_seed_reproducibility_on_disk(tmp_path):
    first, second = tmp_path / "first", tmp_path / "second"
    write_dataset(first, seed=42)
    write_dataset(second, seed=42)
    for file in first.iterdir():
        assert file.read_bytes() == (second / file.name).read_bytes()


def test_different_seed_changes_data():
    assert generate_clean(42)["orders"] != generate_clean(43)["orders"]


def test_no_global_rng_side_effects():
    before = random.getstate()
    generate_clean()
    assert random.getstate() == before


def test_full_eighteen_month_window(clean):
    dates = [date.fromisoformat(o["order_date"]) for o in clean["orders"]]
    assert min(dates) == START_DATE
    assert max(dates) == AS_OF_DATE
    assert len({(d.year, d.month) for d in dates}) == 18


def test_clean_order_chronology(clean):
    for order in clean["orders"]:
        ordered, promised = (date.fromisoformat(order[f]) for f in ("order_date", "promised_date"))
        assert ordered < promised
        assert float(order["order_value"]) > 0
        if order["status"] == "Delivered":
            assert ordered <= date.fromisoformat(order["delivered_date"]) <= AS_OF_DATE
        else:
            assert order["delivered_date"] == ""


def test_clean_ticket_chronology(clean):
    orders = {o["order_id"]: o for o in clean["orders"]}
    for ticket in clean["service_tickets"]:
        parent = orders[ticket["order_id"]]
        created = date.fromisoformat(ticket["created_date"])
        assert parent["status"] == "Delivered"
        assert date.fromisoformat(parent["delivered_date"]) < created <= AS_OF_DATE
        if ticket["closed_date"]:
            assert created <= date.fromisoformat(ticket["closed_date"]) <= AS_OF_DATE


def test_dirty_injection_is_explicit_and_does_not_mutate(clean):
    before = copy.deepcopy(clean)
    _, issues = inject_dirty_rows(clean)
    assert clean == before
    assert len(issues) == 16  # 9 changed cells plus 7 appended duplicate rows
    assert {i["table"] for i in issues} == set(FIELDS)


def test_regional_delay_pattern(clean):
    region = {c["customer_id"]: c["region"] for c in clean["customers"]}
    late, delivered = Counter(), Counter()
    for order in clean["orders"]:
        if order["status"] == "Delivered":
            r = region[order["customer_id"]]
            delivered[r] += 1
            late[r] += order["delivered_date"] > order["promised_date"]
    assert late["East"] / delivered["East"] > late["North"] / delivered["North"] + 0.20


def test_product_ticket_pattern_and_september_spike(clean):
    orders = {o["order_id"]: o for o in clean["orders"]}
    tickets, delivered, sofa_months = Counter(), Counter(), Counter()
    for order in clean["orders"]:
        if order["status"] == "Delivered":
            delivered[order["product_group"]] += 1
    for ticket in clean["service_tickets"]:
        group = orders[ticket["order_id"]]["product_group"]
        tickets[group] += 1
        if group == "Sofas":
            sofa_months[ticket["created_date"][:7]] += 1
    assert tickets["Sofas"] / delivered["Sofas"] > 2 * tickets["Office"] / delivered["Office"]
    assert sofa_months["2025-09"] == max(sofa_months.values())


def test_reference_cleaning_keeps_unknowns_and_first_duplicate(raw):
    reference = clean_reference(raw)
    orders, tickets = reference["orders"], reference["service_tickets"]
    assert len(orders) == 5000 and len(tickets) == 1500
    assert sum(o["order_date"] is None for o in orders) == 1
    assert sum(o["order_value"] is None for o in orders) == 1
    assert sum(o["promise_imputed"] for o in orders) == 1
    assert sum(o["data_quality_issue"] for o in orders) == 5
    assert all(o["late_flag"] is None for o in orders if o["promise_imputed"])
    assert all(o["lead_time_days"] is None or o["lead_time_days"] >= 0 for o in orders)
    assert orders[0]["order_value"] != 999999
    assert sum(t["ticket_status"] == "Unknown" for t in tickets) == 2
    assert sum(t["created_date"] is None for t in tickets) == 1
    assert tickets[3]["priority"] == "Unknown"
    assert all(t["customer_id"] and t["product_group"] for t in tickets)
    assert all(t["resolution_days"] is None or t["resolution_days"] >= 0 for t in tickets)


def test_manifest_matches_actual_csv_counts(tmp_path):
    manifest = write_dataset(tmp_path)
    for name, info in manifest["files"].items():
        with (tmp_path / name).open(newline="", encoding="utf-8") as stream:
            assert len(list(csv.DictReader(stream))) == info["rows"]
    assert json.loads((tmp_path / "manifest.json").read_text()) == manifest


def test_reference_date_and_priority_filter_semantics():
    report = build_report(ROOT / "data")
    unfiltered = report["slices"]["unfiltered_no_date_slicer"]
    period = report["slices"]["all_18_months_date_slicer"]
    high = report["slices"]["high_priority_all_18_months"]
    assert unfiltered["Order Count"] - period["Order Count"] == 1
    assert unfiltered["Ticket Count"] - period["Ticket Count"] == 1
    assert high["Order Count"] == period["Order Count"]  # ticket priority cannot filter Orders
    assert high["Total Revenue"] == period["Total Revenue"]
    assert high["Ticket Count"] < period["Ticket Count"]


def test_committed_artifacts_reproduce():
    verify_committed(ROOT / "data", ROOT / "docs" / "reference_totals.json")


def test_cli_output_directory(tmp_path):
    output = tmp_path / "path with spaces"
    result = subprocess.run([sys.executable, str(ROOT / "data" / "generate.py"),
                             "--output", str(output), "--seed", "42"],
                            check=True, capture_output=True, text=True)
    assert "orders.csv: 5003 rows" in result.stdout
    assert (output / "service_tickets.csv").exists()
