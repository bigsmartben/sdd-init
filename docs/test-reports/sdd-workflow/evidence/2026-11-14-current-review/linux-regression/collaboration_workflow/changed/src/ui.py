"""UI adapter surface in the evaluation fixture (there is no graphical UI)."""

from . import order_service


def mark_paid(connection, order_id):
    order_service.set_status(connection, order_id, "paid")
