"""Execute actual local acceptance; never contacts the external service."""
import argparse
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import order_service, storage


def run_create_order():
    invalid_results = []
    valid_results = []
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "orders.sqlite"
        connection = storage.connect(path)
        try:
            for order_id in ("", "   ", "\t", " \t\n "):
                rejected = False
                try:
                    order_service.create_order(connection, order_id)
                except ValueError:
                    rejected = True
                visible_count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
                other = storage.connect(path)
                try:
                    persisted_count = other.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
                finally:
                    other.close()
                invalid_results.append({
                    "order_id": order_id,
                    "rejected_with_value_error": rejected,
                    "visible_order_count": visible_count,
                    "persisted_order_count": persisted_count,
                })
            for order_id in ("ORDER-4", "  ORDER-5\t"):
                order_service.create_order(connection, order_id)
                other = storage.connect(path)
                try:
                    persisted_id, status = other.execute(
                        "SELECT order_id, status FROM orders WHERE order_id = ?", (order_id,)
                    ).fetchone()
                finally:
                    other.close()
                valid_results.append({
                    "order_id": order_id,
                    "persisted_order_id": persisted_id,
                    "persisted_status": status,
                })
        finally:
            connection.close()
    passed = all(
        row["rejected_with_value_error"]
        and row["visible_order_count"] == row["persisted_order_count"] == 0
        for row in invalid_results
    ) and all(
        row["persisted_order_id"] == row["order_id"] and row["persisted_status"] == "pending"
        for row in valid_results
    )
    return {"scenario": "AC-4", "result": "PASS" if passed else "FAIL",
            "invalid_orders": invalid_results, "valid_orders": valid_results}


def run(scenario):
    if scenario == "AC-4":
        return run_create_order()
    if scenario == "AC-3":
        config = json.loads((ROOT / "runtime.json").read_text(encoding="utf-8"))
        return {
            "scenario": scenario,
            "result": "BLOCKED",
            "reason": "No external call is performed by this fixture; authorized endpoint and permission are required",
            "endpoint_configured": bool(config["external_endpoint"]),
            "authorized": config["external_call_authorized"],
        }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "orders.sqlite"
        connection = storage.connect(path)
        try:
            order_service.create_order(connection, "ORDER-1")
            if scenario == "AC-2":
                order_service.cancel_order(connection, "ORDER-1")
            accepted = order_service.submit_order(connection, "ORDER-1")
        finally:
            connection.close()
        connection = storage.connect(path)
        try:
            status = order_service.read_status(connection, "ORDER-1")
        finally:
            connection.close()
    expected = (True, "submitted") if scenario == "AC-1" else (False, "cancelled")
    return {
        "scenario": scenario,
        "result": "PASS" if (accepted, status) == expected else "FAIL",
        "accepted": accepted,
        "persisted_status": status,
        "expected_accepted": expected[0],
        "expected_status": expected[1],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=("AC-1", "AC-2", "AC-3", "AC-4"))
    args = parser.parse_args()
    results = [run(scenario) for scenario in ([args.scenario] if args.scenario else ("AC-1", "AC-2", "AC-3", "AC-4"))]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 1 if any(row["result"] == "FAIL" for row in results) else 3 if any(row["result"] == "BLOCKED" for row in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
