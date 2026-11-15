"""Existing local tests; acceptance is a separate checks entry point."""
from pathlib import Path
import tempfile
import unittest
import sqlite3

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
        self.assert_persisted("ORDER-1", "submitted")

    def assert_persisted(self, order_id, status):
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, order_id), status)
        finally:
            other.close()

    def test_cancelled_submit_does_not_write_or_commit(self):
        order_service.cancel_order(self.connection, "ORDER-1")
        self.assert_persisted("ORDER-1", "cancelled")
        statements = []
        self.connection.set_trace_callback(statements.append)
        before = self.connection.total_changes
        accepted = order_service.submit_order(self.connection, "ORDER-1")
        self.connection.set_trace_callback(None)
        self.assertIs(accepted, False)
        self.assertEqual(self.connection.total_changes, before)
        self.assertFalse(any(sql.lstrip().upper().startswith(("UPDATE", "COMMIT")) for sql in statements), statements)
        self.assert_persisted("ORDER-1", "cancelled")

    def test_cancelled_submit_preserves_other_order_and_transaction(self):
        order_service.cancel_order(self.connection, "ORDER-1")
        self.connection.execute("INSERT INTO orders VALUES (?, ?)", ("ORDER-2", "pending"))
        self.assertIs(order_service.submit_order(self.connection, "ORDER-1"), False)
        self.assertTrue(self.connection.in_transaction)
        self.connection.rollback()
        with self.assertRaises(ValueError):
            order_service.read_status(self.connection, "ORDER-2")
        self.assert_persisted("ORDER-1", "cancelled")

    def test_mark_paid_from_all_existing_states(self):
        for before in ("pending", "submitted", "cancelled"):
            with self.subTest(before=before):
                order_service.set_status(self.connection, "ORDER-1", before)
                ui.mark_paid(self.connection, "ORDER-1")
                self.assert_persisted("ORDER-1", "paid")

    def test_missing_order_raises_value_error(self):
        operations = (
            order_service.read_status,
            order_service.cancel_order,
            order_service.submit_order,
            lambda connection, order_id: order_service.set_status(connection, order_id, "paid"),
            ui.mark_paid,
        )
        for operation in operations:
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(ValueError):
                    operation(self.connection, "MISSING")

    def test_database_failure_propagates_and_recovers(self):
        self.connection.execute("PRAGMA query_only = ON")
        operations = (
            lambda connection, order_id: order_service.create_order(connection, "ORDER-2"),
            order_service.cancel_order,
            order_service.submit_order,
            lambda connection, order_id: order_service.set_status(connection, order_id, "paid"),
            ui.mark_paid,
        )
        for operation in operations:
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(sqlite3.OperationalError):
                    operation(self.connection, "ORDER-1")
                self.assert_persisted("ORDER-1", "pending")
        self.connection.execute("PRAGMA query_only = OFF")
        self.assertIs(order_service.submit_order(self.connection, "ORDER-1"), True)
        self.assert_persisted("ORDER-1", "submitted")

    def test_mark_paid_is_persisted(self):
        ui.mark_paid(self.connection, "ORDER-1")
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "paid")
        finally:
            other.close()


if __name__ == "__main__":
    unittest.main()
