"""Existing local tests; acceptance is a separate checks entry point."""
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import Mock

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
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "paid")
        self.connection.close()
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "paid")
        finally:
            other.close()

    def test_mark_paid_keeps_existing_status_inputs(self):
        for status in ("pending", "submitted", "cancelled", "paid"):
            with self.subTest(status=status):
                order_service.set_status(self.connection, "ORDER-1", status)
                self.assertIsNone(ui.mark_paid(self.connection, "ORDER-1"))
                self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "paid")

    def test_mark_paid_missing_order_raises(self):
        with self.assertRaisesRegex(ValueError, "order not found"):
            ui.mark_paid(self.connection, "MISSING")
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")

    def test_mark_paid_database_write_failure_propagates(self):
        self.connection.execute("PRAGMA query_only=ON")
        with self.assertRaises(sqlite3.OperationalError):
            ui.mark_paid(self.connection, "ORDER-1")
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")

    def test_mark_paid_commit_failure_propagates(self):
        connection = Mock(wraps=self.connection)
        failure = sqlite3.OperationalError("commit failed")
        connection.commit.side_effect = failure
        with self.assertRaises(sqlite3.OperationalError) as raised:
            ui.mark_paid(connection, "ORDER-1")
        self.assertIs(raised.exception, failure)
        self.assertTrue(self.connection.in_transaction)
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "pending")
        finally:
            other.close()
        self.connection.rollback()
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")


if __name__ == "__main__":
    unittest.main()
