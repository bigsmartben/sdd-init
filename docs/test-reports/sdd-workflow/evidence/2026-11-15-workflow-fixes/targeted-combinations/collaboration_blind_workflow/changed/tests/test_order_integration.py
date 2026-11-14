"""File SQLite integration through the contracted public order entry points."""
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src import order_service, storage, ui


class OrderIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "orders.sqlite"
        self.connection = storage.connect(self.path)
        self.addCleanup(self.connection.close)

    def persisted(self, order_id):
        other = storage.connect(self.path)
        try:
            return order_service.read_status(other, order_id)
        finally:
            other.close()

    def test_I01_create_pending(self):
        order_service.create_order(self.connection, "订单-1")
        self.assertEqual(self.persisted("订单-1"), "pending")

    def test_I02_submit_and_reopen_AC1(self):
        order_service.create_order(self.connection, "ORDER-1")
        self.assertIs(order_service.submit_order(self.connection, "ORDER-1"), True)
        self.connection.close()
        self.assertEqual(self.persisted("ORDER-1"), "submitted")

    def test_I03_cancel_repeated_submit_and_reopen_AC2(self):
        order_service.create_order(self.connection, "ORDER-1")
        order_service.cancel_order(self.connection, "ORDER-1")
        self.assertEqual(self.persisted("ORDER-1"), "cancelled")
        for _ in range(2):
            changes = self.connection.total_changes
            self.assertIs(order_service.submit_order(self.connection, "ORDER-1"), False)
            self.assertEqual(self.connection.total_changes, changes)
            self.assertEqual(self.persisted("ORDER-1"), "cancelled")
        self.connection.close()
        self.assertEqual(self.persisted("ORDER-1"), "cancelled")

    def test_I04_set_status_and_mark_paid(self):
        for order_id in ("SERVICE", "ADAPTER"):
            order_service.create_order(self.connection, order_id)
        order_service.set_status(self.connection, "SERVICE", "paid")
        ui.mark_paid(self.connection, "ADAPTER")
        self.connection.close()
        self.assertEqual(self.persisted("SERVICE"), "paid")
        self.assertEqual(self.persisted("ADAPTER"), "paid")

    def test_I05_missing_order_errors(self):
        operations = (
            ("read_status", lambda: order_service.read_status(self.connection, "missing")),
            ("cancel_order", lambda: order_service.cancel_order(self.connection, "missing")),
            ("submit_order", lambda: order_service.submit_order(self.connection, "missing")),
            ("set_status", lambda: order_service.set_status(self.connection, "missing", "paid")),
            ("mark_paid", lambda: ui.mark_paid(self.connection, "missing")),
        )
        for name, operation in operations:
            with self.subTest(operation=name):
                with self.assertRaises(ValueError):
                    operation()

    def test_I06_invalid_creation_ids(self):
        for order_id in ("", None, 42):
            with self.subTest(order_id=order_id):
                with self.assertRaises(ValueError):
                    order_service.create_order(self.connection, order_id)
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 0)

    def test_I07_database_errors_propagate(self):
        self.connection.close()
        operations = (
            ("create_order", lambda: order_service.create_order(self.connection, "ORDER-1")),
            ("read_status", lambda: order_service.read_status(self.connection, "ORDER-1")),
            ("cancel_order", lambda: order_service.cancel_order(self.connection, "ORDER-1")),
            ("submit_order", lambda: order_service.submit_order(self.connection, "ORDER-1")),
            ("set_status", lambda: order_service.set_status(self.connection, "ORDER-1", "paid")),
            ("mark_paid", lambda: ui.mark_paid(self.connection, "ORDER-1")),
        )
        for name, operation in operations:
            with self.subTest(operation=name):
                with self.assertRaises(sqlite3.Error):
                    operation()

    def test_I08_multi_order_isolation(self):
        for order_id in ("CANCEL", "SUBMIT", "PAY"):
            order_service.create_order(self.connection, order_id)
        order_service.cancel_order(self.connection, "CANCEL")
        self.assertIs(order_service.submit_order(self.connection, "CANCEL"), False)
        self.assertIs(order_service.submit_order(self.connection, "SUBMIT"), True)
        ui.mark_paid(self.connection, "PAY")
        self.connection.close()
        for order_id, status in (("CANCEL", "cancelled"), ("SUBMIT", "submitted"), ("PAY", "paid")):
            with self.subTest(order_id=order_id):
                self.assertEqual(self.persisted(order_id), status)


if __name__ == "__main__":
    unittest.main()
