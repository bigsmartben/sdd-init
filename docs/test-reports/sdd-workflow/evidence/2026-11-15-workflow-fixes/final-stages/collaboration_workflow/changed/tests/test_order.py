"""Existing local tests; acceptance is a separate checks entry point."""
from pathlib import Path
import sqlite3
import tempfile
import unittest

from src import order_service, storage, ui


class ObservedConnection:
    """Observe real SQLite calls and inject failures at the connection boundary."""

    def __init__(self, connection, fail=None):
        self.connection = connection
        self.fail = fail
        self.writes = 0
        self.commits = 0

    def execute(self, sql, parameters=()):
        if sql.startswith(("INSERT", "UPDATE")):
            self.writes += 1
            if self.fail == "execute":
                raise sqlite3.OperationalError("injected write failure")
        return self.connection.execute(sql, parameters)

    def commit(self):
        self.commits += 1
        if self.fail == "commit":
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
        self.assert_persisted("ORDER-1", "submitted")

    def assert_persisted(self, order_id, status):
        other = sqlite3.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, order_id), status)
        finally:
            other.close()

    def test_cancelled_submit_does_not_write_or_commit(self):
        order_service.cancel_order(self.connection, "ORDER-1")
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "cancelled")
        observed = ObservedConnection(self.connection)
        before = self.connection.total_changes
        self.assertIs(order_service.submit_order(observed, "ORDER-1"), False)
        self.assertEqual((observed.writes, observed.commits), (0, 0))
        self.assertEqual(self.connection.total_changes, before)
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "cancelled")
        self.connection.close()
        self.assert_persisted("ORDER-1", "cancelled")

    def test_other_existing_statuses_still_submit(self):
        for status in ("paid", "submitted"):
            with self.subTest(status=status):
                order_service.set_status(self.connection, "ORDER-1", status)
                self.assertIs(order_service.submit_order(self.connection, "ORDER-1"), True)
                self.assert_persisted("ORDER-1", "submitted")

    def test_missing_operations_raise_without_write_or_commit(self):
        operations = (
            order_service.read_status,
            order_service.cancel_order,
            order_service.submit_order,
            lambda connection, order_id: order_service.set_status(connection, order_id, "paid"),
            ui.mark_paid,
        )
        for operation in operations:
            with self.subTest(operation=operation.__name__):
                observed = ObservedConnection(self.connection)
                before = self.connection.total_changes
                with self.assertRaises(ValueError):
                    operation(observed, "MISSING")
                self.assertEqual((observed.writes, observed.commits), (0, 0))
                self.assertEqual(self.connection.total_changes, before)
                self.assert_persisted("ORDER-1", "pending")

    def test_database_errors_propagate(self):
        for operation in (order_service.submit_order, ui.mark_paid):
            for failure in ("execute", "commit"):
                with self.subTest(operation=operation.__name__, failure=failure):
                    observed = ObservedConnection(self.connection, fail=failure)
                    try:
                        with self.assertRaises(sqlite3.OperationalError):
                            operation(observed, "ORDER-1")
                        self.assert_persisted("ORDER-1", "pending")
                    finally:
                        self.connection.rollback()

    def test_closed_connection_errors_propagate(self):
        self.connection.close()
        for operation in (order_service.read_status, order_service.cancel_order,
                          order_service.submit_order, ui.mark_paid):
            with self.subTest(operation=operation.__name__):
                with self.assertRaises(sqlite3.ProgrammingError):
                    operation(self.connection, "ORDER-1")

    def test_orders_are_isolated(self):
        order_service.create_order(self.connection, "ORDER-2")
        order_service.cancel_order(self.connection, "ORDER-1")
        ui.mark_paid(self.connection, "ORDER-2")
        self.assertFalse(order_service.submit_order(self.connection, "ORDER-1"))
        self.assert_persisted("ORDER-1", "cancelled")
        self.assert_persisted("ORDER-2", "paid")

    def test_mark_paid_is_persisted(self):
        ui.mark_paid(self.connection, "ORDER-1")
        self.connection.close()
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "paid")
        finally:
            other.close()


if __name__ == "__main__":
    unittest.main()
