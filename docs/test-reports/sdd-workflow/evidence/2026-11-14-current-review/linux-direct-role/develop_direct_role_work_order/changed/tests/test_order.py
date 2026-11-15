"""Existing local tests; acceptance is a separate checks entry point."""
from pathlib import Path
import tempfile
import unittest

from src import order_service, storage, ui


class OrderIdentifierTests(unittest.TestCase):
    def fresh_connection(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        connection = storage.connect(Path(directory.name) / "orders.sqlite")
        self.addCleanup(connection.close)
        return connection

    def test_whitespace_only_ids_are_rejected_without_insertion(self):
        for order_id in (" ", "\t", "\n", " \t\r\n ", "\u2003"):
            with self.subTest(order_id=repr(order_id)):
                connection = self.fresh_connection()
                with self.assertRaises(ValueError):
                    order_service.create_order(connection, order_id)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 0)

    def test_nonblank_id_is_stored_with_surrounding_spaces(self):
        connection = self.fresh_connection()
        order_id = "  ORDER-2 \t"
        order_service.create_order(connection, order_id)
        self.assertEqual(
            connection.execute("SELECT order_id, status FROM orders").fetchall(),
            [(order_id, "pending")],
        )

    def test_empty_and_none_ids_are_rejected_without_insertion(self):
        for order_id in ("", None):
            with self.subTest(order_id=order_id):
                connection = self.fresh_connection()
                with self.assertRaises(ValueError):
                    order_service.create_order(connection, order_id)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 0)


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
