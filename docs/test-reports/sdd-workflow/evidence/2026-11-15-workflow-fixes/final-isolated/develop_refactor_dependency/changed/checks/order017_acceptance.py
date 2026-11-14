"""WO-ORDER-017 public-entry acceptance against real file SQLite."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import order_service, storage


def main():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "orders.sqlite"
        connection = storage.connect(path)
        rejected = []
        valid = ["ORDER-1", "  ORDER-2  ", "订单-3"]
        try:
            for value in ["", " ", "\t\r\n", "\u2003\u3000", None, 0]:
                try:
                    order_service.create_order(connection, value)
                except ValueError as error:
                    assert str(error) == "order_id is required"
                else:
                    raise AssertionError(f"accepted invalid input: {value!r}")
                assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0
                assert not connection.in_transaction
                rejected.append(repr(value))
            for value in valid:
                order_service.create_order(connection, value)
                assert order_service.read_status(connection, value) == "pending"
        finally:
            connection.close()
        reader = """import json, sys
from src import order_service, storage
connection = storage.connect(sys.argv[1])
try:
    ids = json.loads(sys.argv[2])
    rows = [(value, order_service.read_status(connection, value)) for value in ids]
    assert connection.execute('SELECT COUNT(*) FROM orders').fetchone()[0] == len(ids)
    print(json.dumps(rows, ensure_ascii=False))
finally:
    connection.close()
"""
        result = subprocess.run(
            [sys.executable, "-B", "-c", reader, str(path), json.dumps(valid)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )
        persisted = json.loads(result.stdout)
        assert persisted == [[value, "pending"] for value in valid]
        print(json.dumps({"scenario": "AC-4", "result": "PASS", "rejected": rejected,
                          "rows_after_process_restart": persisted,
                          "components": "public src functions + real file SQLite + new Python process"},
                         ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
