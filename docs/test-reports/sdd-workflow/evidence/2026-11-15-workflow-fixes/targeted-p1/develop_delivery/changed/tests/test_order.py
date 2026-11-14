"""Existing local tests; acceptance is a separate checks entry point."""
from pathlib import Path
from contextlib import contextmanager
import tempfile
import unittest

from src import order_service, storage, ui


class OrderIdTests(unittest.TestCase):
    @contextmanager
    def fresh_database(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.sqlite"
            connection = storage.connect(path)
            try:
                order_service.create_order(connection, "BASELINE")
                yield connection, path
            finally:
                connection.close()

    def rows(self, connection):
        return connection.execute("SELECT order_id, status FROM orders ORDER BY order_id").fetchall()

    def assert_rejected(self, order_id):
        with self.fresh_database() as (connection, path):
            before = self.rows(connection)
            with self.assertRaises(ValueError) as raised:
                order_service.create_order(connection, order_id)
            self.assertEqual(str(raised.exception), "order_id is required")
            self.assertEqual(self.rows(connection), before)
            connection.close()
            reopened = storage.connect(path)
            try:
                self.assertEqual(self.rows(reopened), before)
            finally:
                reopened.close()

    def test_blank_ids_are_rejected_without_writes(self):
        for order_id in ("", " ", "   ", "\t", "\n", " \t\n ", "\u00a0", "\u3000", " \t\u3000\n"):
            with self.subTest(order_id=repr(order_id)):
                self.assert_rejected(order_id)

    def test_non_string_ids_keep_existing_rejection(self):
        for order_id in (None, 0, False):
            with self.subTest(order_id=order_id):
                self.assert_rejected(order_id)

    def test_valid_ids_are_preserved_and_persisted(self):
        for order_id in ("ORDER-1", " ORDER-1 ", "0"):
            with self.subTest(order_id=order_id):
                with self.fresh_database() as (connection, path):
                    before = self.rows(connection)
                    order_service.create_order(connection, order_id)
                    expected = sorted(before + [(order_id, "pending")])
                    self.assertEqual(self.rows(connection), expected)
                    connection.close()
                    reopened = storage.connect(path)
                    try:
                        self.assertEqual(self.rows(reopened), expected)
                    finally:
                        reopened.close()


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
        ui.mark_paid(self.connection, "ORDER-1")
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "paid")
        finally:
            other.close()


if __name__ == "__main__":
    unittest.main()
