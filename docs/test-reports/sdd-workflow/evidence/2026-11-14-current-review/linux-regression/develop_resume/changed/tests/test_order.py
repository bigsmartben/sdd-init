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

    def test_create_order_rejects_empty_or_whitespace_without_writing(self):
        for order_id in ("", "   ", "\t", "\t\n \r"):
            with self.subTest(order_id=repr(order_id)):
                with self.assertRaises(ValueError):
                    order_service.create_order(self.connection, order_id)
                self.assertEqual(
                    self.connection.execute("SELECT order_id, status FROM orders").fetchall(),
                    [("ORDER-1", "pending")],
                )
                other = storage.connect(self.path)
                try:
                    self.assertEqual(
                        other.execute("SELECT order_id, status FROM orders").fetchall(),
                        [("ORDER-1", "pending")],
                    )
                finally:
                    other.close()

    def test_create_order_preserves_valid_identifier_and_pending(self):
        for order_id in ("ORDER-2", " \tORDER-3\n "):
            with self.subTest(order_id=repr(order_id)):
                order_service.create_order(self.connection, order_id)
                self.assertEqual(order_service.read_status(self.connection, order_id), "pending")
                other = storage.connect(self.path)
                try:
                    self.assertEqual(order_service.read_status(other, order_id), "pending")
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
