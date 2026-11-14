"""Existing local tests; acceptance is a separate checks entry point."""
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src import order_service, storage, ui


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

    def test_cancelled_submit_preserves_persisted_status_without_writes(self):
        order_service.cancel_order(self.connection, "ORDER-1")
        before_changes = self.connection.total_changes
        statements = []
        self.connection.set_trace_callback(statements.append)
        try:
            self.assertFalse(order_service.submit_order(self.connection, "ORDER-1"))
        finally:
            self.connection.set_trace_callback(None)
        self.assertEqual(self.connection.total_changes, before_changes)
        self.assertFalse(self.connection.in_transaction)
        self.assertFalse(any(statement.lstrip().upper().startswith(
            ("INSERT", "UPDATE", "DELETE", "REPLACE", "BEGIN", "COMMIT")
        ) for statement in statements), statements)
        self.connection.close()
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "cancelled")
        finally:
            other.close()

    def test_missing_order_submit_raises(self):
        with self.assertRaisesRegex(ValueError, "order not found"):
            order_service.submit_order(self.connection, "MISSING")

    def test_submit_propagates_database_read_error(self):
        self.connection.close()
        with self.assertRaises(sqlite3.ProgrammingError):
            order_service.submit_order(self.connection, "ORDER-1")

    def test_submit_propagates_real_commit_failure(self):
        self.connection.execute("PRAGMA busy_timeout = 0")
        reader = storage.connect(self.path)
        try:
            reader.execute("BEGIN")
            reader.execute("SELECT status FROM orders").fetchall()
            with self.assertRaisesRegex(sqlite3.OperationalError, "database is locked"):
                order_service.submit_order(self.connection, "ORDER-1")
            # A reserved writer can UPDATE while this reader blocks its COMMIT.
            self.assertTrue(self.connection.in_transaction)
            self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "submitted")
            self.assertEqual(order_service.read_status(reader, "ORDER-1"), "pending")
        finally:
            self.connection.rollback()
            reader.rollback()
            reader.close()
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "pending")
        finally:
            other.close()

    def test_mark_paid_is_persisted(self):
        ui.mark_paid(self.connection, "ORDER-1")
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "paid")
        finally:
            other.close()


if __name__ == "__main__":
    unittest.main()
