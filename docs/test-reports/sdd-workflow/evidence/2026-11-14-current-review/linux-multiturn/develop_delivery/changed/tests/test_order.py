"""Existing local tests; acceptance is a separate checks entry point."""
from pathlib import Path
import tempfile
import unittest

from src import order_service, storage, ui


class CreateOrderValidationTests(unittest.TestCase):
    def check_input(self, order_id, rejected):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.sqlite"
            connection = storage.connect(path)
            try:
                order_service.create_order(connection, "BASELINE")
                baseline = connection.execute("SELECT * FROM orders ORDER BY order_id").fetchall()
                if rejected:
                    with self.assertRaisesRegex(ValueError, "^order_id is required$"):
                        order_service.create_order(connection, order_id)
                    expected = baseline
                else:
                    order_service.create_order(connection, order_id)
                    self.assertEqual(order_service.read_status(connection, order_id), "pending")
                    expected = sorted(baseline + [(order_id, "pending")])
                self.assertEqual(connection.execute("SELECT * FROM orders ORDER BY order_id").fetchall(), expected)
            finally:
                connection.close()
            connection = storage.connect(path)
            try:
                self.assertEqual(connection.execute("SELECT * FROM orders ORDER BY order_id").fetchall(), expected)
                if not rejected:
                    self.assertEqual(order_service.read_status(connection, order_id), "pending")
                    if order_id != order_id.strip():
                        with self.assertRaisesRegex(ValueError, "^order not found$"):
                            order_service.read_status(connection, order_id.strip())
            finally:
                connection.close()

    def test_empty_and_whitespace_ids_are_rejected_without_writes(self):
        for order_id in ("", " ", "   ", "\t", "\n", " \t\r\n ", "\u3000", "\u00a0"):
            with self.subTest(order_id=order_id):
                self.check_input(order_id, rejected=True)

    def test_legal_ids_preserve_original_value(self):
        for order_id in ("ORDER-1", " ORDER-1 ", "\tORDER-1\n"):
            with self.subTest(order_id=order_id):
                self.check_input(order_id, rejected=False)

    def test_non_string_ids_are_rejected_without_writes(self):
        for order_id in (None, 0, False, [], {}):
            with self.subTest(order_id=order_id):
                self.check_input(order_id, rejected=True)


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
