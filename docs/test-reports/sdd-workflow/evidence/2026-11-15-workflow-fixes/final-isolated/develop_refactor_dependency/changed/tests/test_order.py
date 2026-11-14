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

    def test_create_rejects_blank_ids_without_writes(self):
        statements = []
        self.connection.set_trace_callback(statements.append)
        self.addCleanup(self.connection.set_trace_callback, None)
        for order_id in ("", " ", "\t\n\r", "\u3000\u00a0", None, 12):
            with self.subTest(order_id=order_id):
                with self.assertRaisesRegex(ValueError, "^order_id is required$"):
                    order_service.create_order(self.connection, order_id)
        self.assertEqual(statements, [])
        other = storage.connect(self.path)
        try:
            self.assertEqual(other.execute("SELECT * FROM orders").fetchall(),
                             [("ORDER-1", "pending")])
        finally:
            other.close()

    def test_create_preserves_valid_id_and_persists(self):
        order_id = "  ORDER-2\t"
        order_service.create_order(self.connection, order_id)
        other = storage.connect(self.path)
        try:
            self.assertEqual(order_service.read_status(other, order_id), "pending")
            self.assertEqual(other.execute(
                "SELECT order_id FROM orders WHERE order_id = ?", (order_id,)
            ).fetchone(), (order_id,))
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
