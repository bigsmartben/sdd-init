"""Public mark-paid adapter for the local SQLite fixture."""

from src import order_service


def mark_paid(connection, order_id):
    order_service.set_status(connection, order_id, "paid")
