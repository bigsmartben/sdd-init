"""Existing local tests; acceptance is a separate checks entry point."""
from pathlib import Path
import tempfile
import unittest

from src import order_service, storage, ui


class OrderIdentifierTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "orders.sqlite"
        self.connection = storage.connect(self.path)
        self.addCleanup(self.connection.close)

    def assert_identifier_rejected(self, order_id):
        statements = []
        self.connection.set_trace_callback(statements.append)
        try:
            with self.assertRaises(ValueError):
                order_service.create_order(self.connection, order_id)
        finally:
            self.connection.set_trace_callback(None)
        self.assertFalse(any(statement.lstrip().upper().startswith("INSERT") for statement in statements))
        self.assertEqual(self.connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0], 0)

    def test_whitespace_only_identifiers_are_rejected_before_insert(self):
        for order_id in (" ", "\t", "\n", " \t\r\n ", "\u2003"):
            with self.subTest(order_id=repr(order_id)):
                self.assert_identifier_rejected(order_id)

    def test_empty_and_none_identifiers_remain_rejected(self):
        for order_id in ("", None):
            with self.subTest(order_id=order_id):
                self.assert_identifier_rejected(order_id)

    def test_nonblank_identifier_is_persisted_with_surrounding_spaces(self):
        order_id = "  ORDER-SPACE  "
        order_service.create_order(self.connection, order_id)
        other = storage.connect(self.path)
        try:
            self.assertEqual(other.execute("SELECT order_id, status FROM orders").fetchall(),
                             [(order_id, "pending")])
            self.assertEqual(order_service.read_status(other, order_id), "pending")
        finally:
            other.close()


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
