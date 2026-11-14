"""Existing local tests; acceptance is a separate checks entry point."""
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src import order_service, storage, ui


class CommitProbe:
    """Delegate SQL to real SQLite and observe or reject the commit boundary."""
    def __init__(self, connection, fail=False):
        self.connection = connection
        self.fail = fail
        self.commits = 0

    def execute(self, *args):
        return self.connection.execute(*args)

    def commit(self):
        self.commits += 1
        if self.fail:
            raise sqlite3.OperationalError("injected commit failure")
        self.connection.commit()


class OrderTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "orders.sqlite"
        self.connection = storage.connect(self.path)
        self.addCleanup(self.connection.close)
        order_service.create_order(self.connection, "ORDER-1")

    def test_normal_submit(self):
        self.assertTrue(order_service.submit_order(self.connection, "ORDER-1"))
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "submitted")

    def test_mark_paid_is_persisted(self):
        ui.mark_paid(self.connection, "ORDER-1")
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "paid")
        finally:
            other.close()

    def test_cancelled_submit_has_no_write_or_commit(self):
        order_service.cancel_order(self.connection, "ORDER-1")
        statements = []
        self.connection.set_trace_callback(statements.append)
        probe = CommitProbe(self.connection)
        self.assertIs(order_service.submit_order(probe, "ORDER-1"), False)
        self.assertEqual(probe.commits, 0)
        self.assertTrue(statements)
        self.assertTrue(all(sql.lstrip().upper().startswith("SELECT ") for sql in statements))
        self.connection.set_trace_callback(None)
        self.connection.close()
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "cancelled")
        finally:
            other.close()

    def test_mark_paid_missing_raises(self):
        with self.assertRaises(ValueError):
            ui.mark_paid(self.connection, "MISSING")

    def test_mark_paid_from_all_existing_states(self):
        for initial in ("pending", "cancelled", "submitted", "paid"):
            with self.subTest(initial=initial):
                order_service.set_status(self.connection, "ORDER-1", initial)
                ui.mark_paid(self.connection, "ORDER-1")
                other = storage.connect(self.path)
                try:
                    self.assertEqual(order_service.read_status(other, "ORDER-1"), "paid")
                finally:
                    other.close()

    def test_commit_errors_propagate_without_persisted_success(self):
        for name, operation, order_id in (
            ("create", order_service.create_order, "ORDER-2"),
            ("cancel", order_service.cancel_order, "ORDER-1"),
            ("submit", order_service.submit_order, "ORDER-1"),
            ("set_status", lambda c, o: order_service.set_status(c, o, "paid"), "ORDER-1"),
            ("mark_paid", ui.mark_paid, "ORDER-1"),
        ):
            with self.subTest(operation=name):
                probe = CommitProbe(self.connection, fail=True)
                with self.assertRaisesRegex(sqlite3.OperationalError, "commit failure"):
                    operation(probe, order_id)
                self.assertEqual(probe.commits, 1)
                other = storage.connect(self.path)
                try:
                    self.assertEqual(order_service.read_status(other, "ORDER-1"), "pending")
                    self.assertEqual(other.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 1)
                finally:
                    other.close()
                    self.connection.rollback()


if __name__ == "__main__":
    unittest.main()
