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

    def test_mark_paid_is_persisted(self):
        self.assertIsNone(ui.mark_paid(self.connection, "ORDER-1"))
        self.connection.close()
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "paid")
        finally:
            other.close()

    def test_mark_paid_missing_order(self):
        with self.assertRaisesRegex(ValueError, "^order not found$"):
            ui.mark_paid(self.connection, "MISSING")
        self.assertEqual(
            self.connection.execute("SELECT order_id, status FROM orders").fetchall(),
            [("ORDER-1", "pending")],
        )

    def test_mark_paid_read_error_propagates(self):
        self.connection.close()
        with self.assertRaises(sqlite3.ProgrammingError):
            ui.mark_paid(self.connection, "ORDER-1")

    def test_mark_paid_write_error_propagates(self):
        self.connection.execute("PRAGMA query_only = ON")
        with self.assertRaisesRegex(sqlite3.OperationalError, "readonly"):
            ui.mark_paid(self.connection, "ORDER-1")
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")

    def test_mark_paid_commit_error_propagates(self):
        reader = storage.connect(self.path)
        try:
            reader.execute("BEGIN")
            self.assertEqual(order_service.read_status(reader, "ORDER-1"), "pending")
            self.connection.execute("PRAGMA busy_timeout = 0")
            with self.assertRaisesRegex(sqlite3.OperationalError, "locked"):
                ui.mark_paid(self.connection, "ORDER-1")
            self.connection.rollback()
            reader.rollback()
            self.assertEqual(order_service.read_status(reader, "ORDER-1"), "pending")
        finally:
            self.connection.rollback()
            reader.close()


if __name__ == "__main__":
    unittest.main()
