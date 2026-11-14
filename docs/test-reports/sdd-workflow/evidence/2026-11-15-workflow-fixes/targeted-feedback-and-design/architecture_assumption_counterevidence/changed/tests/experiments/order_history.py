"""Isolated feasibility evidence; never imported by product code.

Run from repository root: python -B tests/experiments/order_history.py
All databases are synthetic and removed by TemporaryDirectory.
"""
import json
from pathlib import Path
import platform
import sqlite3
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from src import order_service, storage


def snapshot(path):
    with sqlite3.connect(path) as c:
        return list(c.execute("SELECT order_id, status FROM orders ORDER BY order_id"))


def history(path):
    with sqlite3.connect(path) as c:
        return list(c.execute("SELECT seq, order_id, old_status, new_status FROM history ORDER BY seq"))


def schema_history(c):
    c.execute("""CREATE TABLE history (
        seq INTEGER PRIMARY KEY AUTOINCREMENT, order_id TEXT NOT NULL,
        old_status TEXT, new_status TEXT NOT NULL)""")


def update_with_history(c, status):
    old = c.execute("SELECT status FROM orders WHERE order_id='O'").fetchone()[0]
    c.execute("UPDATE orders SET status=? WHERE order_id='O'", (status,))
    if old != status:
        c.execute("INSERT INTO history(order_id, old_status, new_status) VALUES ('O', ?, ?)", (old, status))


def main():
    result = {"python": platform.python_version(), "sqlite": sqlite3.sqlite_version, "cases": {}}
    with tempfile.TemporaryDirectory(prefix="order-history-") as tmp:
        root = Path(tmp)
        # E1: distinct real-service write paths have indistinguishable logical records.
        for name, states in [("a", ["submitted", "paid"]), ("b", ["paid"])]:
            c = storage.connect(root / name)
            order_service.create_order(c, "O")
            for state in states:
                order_service.set_status(c, "O", state)
            c.close()
        a, b = snapshot(root / "a"), snapshot(root / "b")
        assert a == b == [("O", "paid")]
        result["cases"]["E1_current_rows"] = {"path_a": ["pending", "submitted", "paid"], "path_b": ["pending", "paid"], "reopened_a": a, "reopened_b": b, "same_logical_export": a == b}

        # E2: trace is connection-local and includes writes later rolled back.
        path = root / "trace"
        c = storage.connect(path)
        order_service.create_order(c, "O")
        trace = []
        c.set_trace_callback(trace.append)
        c.execute("UPDATE orders SET status='submitted' WHERE order_id='O'")
        c.rollback()
        other = storage.connect(path)
        order_service.set_status(other, "O", "paid")
        other.close()
        c.close()
        assert any("submitted" in sql for sql in trace)
        assert not any("paid" in sql for sql in trace)
        assert snapshot(path) == [("O", "paid")]
        result["cases"]["E2_trace"] = {"observed_sql": trace, "reopened_rows": snapshot(path), "other_connection_update_seen": False, "rolled_back_update_seen": True}

        # E3: service-owned history candidate, independent from src service commits.
        path = root / "service"
        c = storage.connect(path)
        schema_history(c)
        with c:
            c.execute("INSERT INTO orders VALUES ('O','pending')")
            c.execute("INSERT INTO history(order_id,new_status) VALUES ('O','pending')")
        with c:
            update_with_history(c, "submitted")
            update_with_history(c, "paid")
        try:
            with c:
                update_with_history(c, "cancelled")
                raise RuntimeError("synthetic pre-commit failure")
        except RuntimeError:
            pass
        # A rejected history write must also roll back its preceding state write.
        c.execute("CREATE TRIGGER fail_history BEFORE INSERT ON history WHEN NEW.new_status='cancelled' BEGIN SELECT RAISE(ABORT,'synthetic history failure'); END")
        try:
            with c:
                update_with_history(c, "cancelled")
        except sqlite3.IntegrityError:
            pass
        else:
            raise AssertionError("history failure was not injected")
        c.close()
        entries = history(path)
        assert [r[3] for r in entries] == ["pending", "submitted", "paid"]
        assert snapshot(path) == [("O", "paid")]
        # Bypass demonstrates coverage dependency on routing every write through helper.
        other = sqlite3.connect(path)
        with other:
            other.execute("UPDATE orders SET status='cancelled' WHERE order_id='O'")
        other.close()
        assert history(path) == entries
        result["cases"]["E3_service_history"] = {"reopened_history": entries, "rolled_back_states_absent": True, "history_write_failure_atomic": True, "bypass_current_rows": snapshot(path), "bypass_recorded": False}

        # E4: persistent triggers observe writes across connections, transactionally.
        path = root / "trigger"
        c = storage.connect(path)
        schema_history(c)
        c.executescript("""
        CREATE TRIGGER orders_created AFTER INSERT ON orders BEGIN
          INSERT INTO history(order_id,new_status) VALUES (NEW.order_id,NEW.status);
        END;
        CREATE TRIGGER orders_changed AFTER UPDATE OF status ON orders
        WHEN OLD.status IS NOT NEW.status BEGIN
          INSERT INTO history(order_id,old_status,new_status)
          VALUES (NEW.order_id,OLD.status,NEW.status);
        END;
        """)
        order_service.create_order(c, "O")
        c.close()
        other = sqlite3.connect(path)
        with other:
            other.execute("UPDATE orders SET status='submitted' WHERE order_id='O'")
            other.execute("UPDATE orders SET status='paid' WHERE order_id='O'")
            other.execute("UPDATE orders SET status='paid' WHERE order_id='O'")
        try:
            with other:
                other.execute("UPDATE orders SET status='cancelled' WHERE order_id='O'")
                raise RuntimeError("synthetic rollback")
        except RuntimeError:
            pass
        other.close()
        entries = history(path)
        assert [r[3] for r in entries] == ["pending", "submitted", "paid"]
        assert [r[0] for r in entries] == sorted({r[0] for r in entries})
        assert snapshot(path) == [("O", "paid")]
        result["cases"]["E4_trigger_history"] = {"reopened_history": entries, "other_connection_recorded": True, "same_transaction_intermediate_state_preserved": True, "rollback_absent": True, "same_value_update_omitted": True}
    result["all_assertions_passed"] = True
    result["temporary_databases_removed"] = True
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
