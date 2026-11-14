"""Existing local tests; acceptance is a separate checks entry point."""
from pathlib import Path
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
        self.assert_persisted_status("submitted")

    def test_cancelled_order_cannot_be_submitted(self):
        order_service.cancel_order(self.connection, "ORDER-1")
        changes_before = self.connection.total_changes
        statements = []
        self.connection.set_trace_callback(statements.append)
        try:
            self.assertFalse(order_service.submit_order(self.connection, "ORDER-1"))
        finally:
            self.connection.set_trace_callback(None)
        self.assertEqual(self.connection.total_changes, changes_before)
        self.assertTrue(statements)
        self.assertTrue(all(statement.lstrip().upper().startswith("SELECT ") for statement in statements))
        self.assert_persisted_status("cancelled")

    def test_submit_missing_order_raises(self):
        with self.assertRaises(ValueError):
            order_service.submit_order(self.connection, "MISSING")
        self.assert_persisted_status("pending")

    def assert_persisted_status(self, expected):
        self.connection.close()
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), expected)
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
