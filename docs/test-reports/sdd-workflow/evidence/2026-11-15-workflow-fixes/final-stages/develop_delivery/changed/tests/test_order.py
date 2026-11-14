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
        self.assertEqual(order_service.read_status(self.connection, "ORDER-1"), "submitted")

    def test_mark_paid_is_persisted(self):
        ui.mark_paid(self.connection, "ORDER-1")
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, "ORDER-1"), "paid")
        finally:
            other.close()

    def test_invalid_order_ids_leave_orders_unchanged(self):
        invalid = ("", " ", "\t", "\n", "\u3000", " \t\n\u3000 ", None, 0, False, [])
        for value in invalid:
            with self.subTest(order_id=value):
                before = self.connection.execute("SELECT order_id, status FROM orders ORDER BY order_id").fetchall()
                with self.assertRaises(ValueError) as raised:
                    order_service.create_order(self.connection, value)
                self.assertEqual(str(raised.exception), "order_id is required")
                self.assertEqual(
                    self.connection.execute("SELECT order_id, status FROM orders ORDER BY order_id").fetchall(),
                    before,
                )
                other = storage.connect(self.path)
                try:
                    self.assertEqual(
                        other.execute("SELECT order_id, status FROM orders ORDER BY order_id").fetchall(),
                        before,
                    )
                finally:
                    other.close()

    def test_valid_order_ids_are_persisted_without_trimming(self):
        for value in ("ORDER-2", " ORDER-3 ", "\tORDER-4\n", "\u3000订单-5\u3000"):
            with self.subTest(order_id=value):
                self.assertIsNone(order_service.create_order(self.connection, value))
                self.assertEqual(order_service.read_status(self.connection, value), "pending")
                other = storage.connect(self.path)
                try:
                    self.assertEqual(order_service.read_status(other, value), "pending")
                    if value != value.strip():
                        with self.assertRaises(ValueError):
                            order_service.read_status(other, value.strip())
                finally:
                    other.close()


if __name__ == "__main__":
    unittest.main()
