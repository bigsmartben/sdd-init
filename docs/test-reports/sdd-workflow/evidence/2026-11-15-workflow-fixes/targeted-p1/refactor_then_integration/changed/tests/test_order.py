"""Existing local tests; acceptance is a separate checks entry point."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

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
        for initial_status in ("pending", "submitted", "cancelled", "paid"):
            with self.subTest(initial_status=initial_status):
                path = Path(self.directory.name) / f"{initial_status}.sqlite"
                connection = storage.connect(path)
                try:
                    order_service.create_order(connection, "ORDER-PAID")
                    order_service.set_status(connection, "ORDER-PAID", initial_status)
                    with patch("src.order_service.set_status", wraps=order_service.set_status) as set_status:
                        result = ui.mark_paid(connection, "ORDER-PAID")
                        set_status.assert_called_once_with(connection, "ORDER-PAID", "paid")
                    self.assertIsNone(result)
                finally:
                    connection.close()
                other = storage.connect(path)
                try:
                    self.assertEqual(order_service.read_status(other, "ORDER-PAID"), "paid")
                finally:
                    other.close()

    def test_mark_paid_missing_order_does_not_insert(self):
        with self.assertRaisesRegex(ValueError, "^order not found$"):
            ui.mark_paid(self.connection, "MISSING")
        self.assertEqual(self.connection.execute("SELECT order_id FROM orders").fetchall(), [("ORDER-1",)])
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")

    def test_mark_paid_readonly_error_preserves_pending(self):
        self.connection.execute("PRAGMA query_only=ON")
        with self.assertRaisesRegex(sqlite3.OperationalError, "readonly"):
            ui.mark_paid(self.connection, "ORDER-1")
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")
        self.connection.close()
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "pending")
        finally:
            other.close()

    def test_mark_paid_closed_connection_error_propagates(self):
        self.connection.close()
        with self.assertRaisesRegex(sqlite3.ProgrammingError, "closed database"):
            ui.mark_paid(self.connection, "ORDER-1")


if __name__ == "__main__":
    unittest.main()
