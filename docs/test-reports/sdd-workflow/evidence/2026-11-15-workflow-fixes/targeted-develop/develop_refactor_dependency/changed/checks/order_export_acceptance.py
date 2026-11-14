"""WO-ORDER-017 AC-4 acceptance against a real temporary SQLite file."""
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import order_service, storage


def run():
    results = []
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "orders.sqlite"
        connection = storage.connect(path)
        try:
            invalid = ("", " ", "\t\n\r", "\u3000\u00a0", None, 17)
            for order_id in invalid:
                before = connection.total_changes
                error = None
                try:
                    order_service.create_order(connection, order_id)
                except ValueError as exception:
                    error = str(exception)
                count = connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
                passed = error == "order_id is required" and count == 0 and connection.total_changes == before
                results.append({"input": repr(order_id), "error": error, "rows": count, "no_writes": connection.total_changes == before, "result": "PASS" if passed else "FAIL"})
            valid = ("ORDER-4", "  ORDER-4  ", "订单-4")
            for order_id in valid:
                order_service.create_order(connection, order_id)
        finally:
            connection.close()
        connection = storage.connect(path)
        try:
            for order_id in valid:
                status = order_service.read_status(connection, order_id)
                results.append({"input": repr(order_id), "persisted_status": status, "result": "PASS" if status == "pending" else "FAIL"})
        finally:
            connection.close()
    return {"scenario": "AC-4", "result": "PASS" if all(item["result"] == "PASS" for item in results) else "FAIL", "cases": results}


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["result"] == "PASS" else 1)
