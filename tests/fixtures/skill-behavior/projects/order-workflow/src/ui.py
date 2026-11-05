"""UI adapter surface in the evaluation fixture (there is no graphical UI)."""


def mark_paid(connection, order_id):
    connection.execute("UPDATE orders SET status = ? WHERE order_id = ?", ("paid", order_id))
    connection.commit()
