"""Direct AC-4 checks for creation validation and persistence."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

from src import order_service, storage


INVALID_ORDER_IDS = ("", " ", "\t", "\n", " \t\r\n", "\u00a0", "\u2003", "\u3000", None, 0, False, b"ORDER", [], {})


class CreateOrderValidationTests(unittest.TestCase):
    def test_invalid_ids_do_not_access_connection(self):
        for order_id in INVALID_ORDER_IDS:
            with self.subTest(order_id=repr(order_id)):
                connection = Mock()
                with self.assertRaisesRegex(ValueError, "^order_id is required$"):
                    order_service.create_order(connection, order_id)
                self.assertEqual(connection.mock_calls, [])

    def test_invalid_ids_leave_file_database_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.sqlite"
            connection = storage.connect(path)
            try:
                order_service.create_order(connection, "EXISTING")
                for order_id in INVALID_ORDER_IDS:
                    with self.subTest(order_id=repr(order_id)):
                        before = connection.execute("SELECT * FROM orders ORDER BY order_id").fetchall()
                        changes = connection.total_changes
                        with self.assertRaisesRegex(ValueError, "^order_id is required$"):
                            order_service.create_order(connection, order_id)
                        self.assertEqual(connection.total_changes, changes)
                        self.assertFalse(connection.in_transaction)
                        self.assertEqual(connection.execute("SELECT * FROM orders ORDER BY order_id").fetchall(), before)
                before = [("EXISTING", "pending")]
            finally:
                connection.close()
            reopened = storage.connect(path)
            try:
                self.assertEqual(reopened.execute("SELECT * FROM orders ORDER BY order_id").fetchall(), before)
            finally:
                reopened.close()

    def test_valid_ids_are_committed_without_normalization(self):
        order_ids = ("ORDER-1", " ORDER-2\t", "\u2003订单-3\u3000")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.sqlite"
            connection = storage.connect(path)
            try:
                for order_id in order_ids:
                    order_service.create_order(connection, order_id)
                self.assertFalse(connection.in_transaction)
            finally:
                connection.close()
            reopened = storage.connect(path)
            try:
                self.assertEqual(dict(reopened.execute("SELECT * FROM orders")), dict.fromkeys(order_ids, "pending"))
            finally:
                reopened.close()


if __name__ == "__main__":
    unittest.main()
