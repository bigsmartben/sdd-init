"""Targeted regression coverage for BUG-001 and BUG-002."""
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src import order_service, storage, ui


class OrderBugfixTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "orders.sqlite"
        self.connection = storage.connect(self.path)
        self.addCleanup(self.connection.close)
        order_service.create_order(self.connection, "ORDER-1")

    def reopened_status(self, order_id="ORDER-1"):
        self.connection.close()
        other = storage.connect(self.path)
        try:
            return order_service.read_status(other, order_id)
        finally:
            other.close()

    def test_cancelled_submit_is_rejected_and_persisted(self):
        order_service.cancel_order(self.connection, "ORDER-1")
        self.assertIs(order_service.submit_order(self.connection, "ORDER-1"), False)
        self.assertEqual(self.reopened_status(), "cancelled")

    def test_pending_submit_is_accepted_and_persisted(self):
        self.assertIs(order_service.submit_order(self.connection, "ORDER-1"), True)
        self.assertEqual(self.reopened_status(), "submitted")

    def test_missing_payment_raises_without_mutating_other_order(self):
        with self.assertRaisesRegex(ValueError, "order not found"):
            ui.mark_paid(self.connection, "MISSING")
        self.assertEqual(self.reopened_status(), "pending")

    def test_payment_is_persisted(self):
        ui.mark_paid(self.connection, "ORDER-1")
        self.assertEqual(self.reopened_status(), "paid")

    def test_order_operations_are_isolated(self):
        order_service.create_order(self.connection, "订单-二")
        order_service.cancel_order(self.connection, "ORDER-1")
        self.assertIs(order_service.submit_order(self.connection, "ORDER-1"), False)
        ui.mark_paid(self.connection, "订单-二")
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "cancelled")
        self.assertEqual(self.reopened_status("订单-二"), "paid")

    def test_write_errors_propagate(self):
        self.connection.execute("PRAGMA query_only = ON")
        for operation in (order_service.cancel_order, order_service.submit_order, ui.mark_paid):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(sqlite3.OperationalError):
                    operation(self.connection, "ORDER-1")
        self.assertEqual(self.reopened_status(), "pending")

    def test_commit_errors_propagate(self):
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript("""
            CREATE TABLE allowed_status (status TEXT PRIMARY KEY);
            CREATE TABLE status_audit (
                status TEXT REFERENCES allowed_status(status)
                DEFERRABLE INITIALLY DEFERRED
            );
            CREATE TRIGGER audit_status AFTER UPDATE OF status ON orders
            BEGIN
                INSERT INTO status_audit VALUES (NEW.status);
            END;
        """)
        for operation in (order_service.cancel_order, order_service.submit_order, ui.mark_paid):
            with self.subTest(operation=operation.__name__):
                # UPDATE succeeds; the deferred constraint fails at commit.
                with self.assertRaises(sqlite3.IntegrityError):
                    operation(self.connection, "ORDER-1")
                self.assertTrue(self.connection.in_transaction)
                self.connection.rollback()
                self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")
        self.assertEqual(self.reopened_status(), "pending")


if __name__ == "__main__":
    unittest.main()
