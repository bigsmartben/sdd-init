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
        for status in ("pending", "submitted", "cancelled", "paid"):
            with self.subTest(status=status):
                order_service.set_status(self.connection, "ORDER-1", status)
                self.assertIsNone(ui.mark_paid(self.connection, "ORDER-1"))
                self.assertIsNone(ui.mark_paid(self.connection, "ORDER-1"))
                other = storage.connect(self.path)
                try:
                    self.assertEqual(order_service.read_status(other, "ORDER-1"), "paid")
                finally:
                    other.close()
                self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "paid")

    def test_mark_paid_missing_order_does_not_create_one(self):
        with self.assertRaisesRegex(ValueError, "order not found"):
            ui.mark_paid(self.connection, "MISSING")
        self.assertEqual(self.connection.execute("SELECT order_id FROM orders").fetchall(), [("ORDER-1",)])
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")

    def test_mark_paid_update_failure_propagates(self):
        self.connection.execute(
            "CREATE TRIGGER reject_paid BEFORE UPDATE ON orders "
            "WHEN NEW.status = 'paid' BEGIN SELECT RAISE(ABORT, 'paid write rejected'); END"
        )
        self.connection.commit()
        with self.assertRaisesRegex(sqlite3.IntegrityError, "paid write rejected"):
            ui.mark_paid(self.connection, "ORDER-1")
        self.connection.rollback()
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")

    def test_mark_paid_commit_failure_propagates(self):
        failure = sqlite3.OperationalError("commit rejected")
        connection = Mock(wraps=self.connection)
        connection.commit.side_effect = failure
        with self.assertRaises(sqlite3.OperationalError) as raised:
            ui.mark_paid(connection, "ORDER-1")
        self.assertIs(raised.exception, failure)
        connection.close.assert_not_called()
        self.connection.rollback()
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "pending")
        finally:
            other.close()
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")


if __name__ == "__main__":
    unittest.main()
