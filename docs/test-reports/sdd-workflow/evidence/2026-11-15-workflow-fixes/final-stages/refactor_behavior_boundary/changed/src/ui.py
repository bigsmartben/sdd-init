"""Public mark-paid adapter for the local SQLite fixture."""

from src.order_service import set_status


def mark_paid(connection, order_id):
    set_status(connection, order_id, "paid")
