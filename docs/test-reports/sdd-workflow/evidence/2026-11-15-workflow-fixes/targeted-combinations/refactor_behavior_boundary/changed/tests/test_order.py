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

    def test_mark_paid_missing_order_raises(self):
        with self.assertRaisesRegex(ValueError, "order not found"):
            ui.mark_paid(self.connection, "MISSING")
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")

    def test_mark_paid_write_failure_propagates(self):
        self.connection.execute("PRAGMA query_only = ON")
        with self.assertRaises(sqlite3.OperationalError):
            ui.mark_paid(self.connection, "ORDER-1")
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")

    def test_mark_paid_commit_failure_propagates(self):
        failure = sqlite3.OperationalError("injected commit failure")

        class CommitFailureConnection:
            def __init__(self, connection):
                self.connection = connection

            def execute(self, *args, **kwargs):
                return self.connection.execute(*args, **kwargs)

            def commit(self):
                raise failure

        with self.assertRaises(sqlite3.OperationalError) as raised:
            ui.mark_paid(CommitFailureConnection(self.connection), "ORDER-1")
        self.assertIs(raised.exception, failure)
        self.connection.rollback()
        self.connection.close()
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "pending")
        finally:
            other.close()


if __name__ == "__main__":
    unittest.main()
