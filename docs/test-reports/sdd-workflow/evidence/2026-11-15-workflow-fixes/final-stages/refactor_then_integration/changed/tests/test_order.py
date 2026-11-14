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
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")

    def test_mark_paid_readonly_database(self):
        readonly = sqlite3.connect(f"{self.path.as_uri()}?mode=ro", uri=True)
        self.addCleanup(readonly.close)
        with self.assertRaises(sqlite3.OperationalError):
            ui.mark_paid(readonly, "ORDER-1")
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "pending")

    def test_mark_paid_commit_failure(self):
        class FailingCommitConnection:
            def execute(proxy, *args, **kwargs):
                return self.connection.execute(*args, **kwargs)

            def commit(proxy):
                raise sqlite3.OperationalError("commit failed")

        with self.assertRaisesRegex(sqlite3.OperationalError, "^commit failed$"):
            ui.mark_paid(FailingCommitConnection(), "ORDER-1")
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "pending")
        finally:
            other.close()


if __name__ == "__main__":
    unittest.main()
