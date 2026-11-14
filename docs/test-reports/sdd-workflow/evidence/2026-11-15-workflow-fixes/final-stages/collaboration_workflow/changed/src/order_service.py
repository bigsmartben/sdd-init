"""Order operations in the intentionally imperfect evaluation fixture."""


def create_order(connection, order_id):
    if not isinstance(order_id, str) or not order_id:
        raise ValueError("order_id is required")
    connection.execute("INSERT INTO orders VALUES (?, ?)", (order_id, "pending"))
    connection.commit()


def read_status(connection, order_id):
    row = connection.execute("SELECT status FROM orders WHERE order_id = ?", (order_id,)).fetchone()
    if row is None:
        raise ValueError("order not found")
    return row[0]


def set_status(connection, order_id, status):
    read_status(connection, order_id)
    connection.execute("UPDATE orders SET status = ? WHERE order_id = ?", (status, order_id))
    connection.commit()


def cancel_order(connection, order_id):
    set_status(connection, order_id, "cancelled")


def submit_order(connection, order_id):
    if read_status(connection, order_id) == "cancelled":
        return False
    set_status(connection, order_id, "submitted")
    return True
