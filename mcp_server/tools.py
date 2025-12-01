"""
tools.py

MCP-style tools for the customer support system.

These functions are the "MCP tools" referenced in the assignment:

- get_customer(customer_id)
- list_customers(status, limit)
- update_customer(customer_id, data)
- create_ticket(customer_id, issue, priority)
- get_customer_history(customer_id)

They sit on top of the SQLite database created by `database_setup.py`
and use the connection helper in `db.py`.
"""

from typing import Any, Dict, List, Optional

from .db import get_conn, _row_to_dict


# ------------------------------------------------------------
# 1. get_customer(customer_id)
# ------------------------------------------------------------
def get_customer(customer_id: int) -> Dict[str, Any]:
    """
    Get a single customer by ID.

    Args:
        customer_id: customers.id

    Returns:
        dict with keys:
          - found: bool
          - customer: dict or None
          - message: str
    """
    with get_conn() as conn:
        row = conn.execute(
            """
            SELECT id, name, email, phone, status, created_at, updated_at
            FROM customers
            WHERE id = ?
            """,
            (customer_id,),
        ).fetchone()

    if row is None:
        return {
            "found": False,
            "customer": None,
            "message": f"No customer found with id {customer_id}",
        }

    return {
        "found": True,
        "customer": _row_to_dict(row),
        "message": "Customer retrieved successfully.",
    }


# ------------------------------------------------------------
# 2. list_customers(status, limit)
# ------------------------------------------------------------
def list_customers(status: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
    """
    List customers filtered by status.

    Args:
        status: customers.status ('active' or 'disabled').
                If None, returns customers with any status.
        limit: maximum number of customers to return.

    Returns:
        dict with keys:
          - count: int
          - customers: list[dict]
    """
    query = """
        SELECT id, name, email, phone, status, created_at, updated_at
        FROM customers
    """
    params: List[Any] = []

    if status:
        query += " WHERE status = ?"
        params.append(status)

    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)

    with get_conn() as conn:
        rows = conn.execute(query, tuple(params)).fetchall()

    return {
        "count": len(rows),
        "customers": [_row_to_dict(r) for r in rows],
    }


# ------------------------------------------------------------
# 3. update_customer(customer_id, data)
# ------------------------------------------------------------
def update_customer(customer_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a customer record with the fields in `data`.

    Args:
        customer_id: customers.id
        data: dict of fields to update, e.g. {
            "email": "new@email.com",
            "status": "active"
        }

    Returns:
        dict with keys:
          - success: bool
          - rows_affected: int
          - message: str
    """
    if not data:
        return {
            "success": False,
            "rows_affected": 0,
            "message": "No fields provided to update.",
        }

    allowed_fields = {"name", "email", "phone", "status"}
    set_clauses = []
    params: List[Any] = []

    for key, value in data.items():
        if key in allowed_fields:
            set_clauses.append(f"{key} = ?")
            params.append(value)

    if not set_clauses:
        return {
            "success": False,
            "rows_affected": 0,
            "message": "No valid fields to update.",
        }

    # Add customer_id for WHERE clause
    params.append(customer_id)

    with get_conn() as conn:
        cur = conn.execute(
            f"""
            UPDATE customers
            SET {", ".join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            tuple(params),
        )
        rows_affected = cur.rowcount

    return {
        "success": rows_affected > 0,
        "rows_affected": rows_affected,
        "message": "Customer updated." if rows_affected > 0 else "Customer not found.",
    }


# ------------------------------------------------------------
# 4. create_ticket(customer_id, issue, priority)
# ------------------------------------------------------------
def create_ticket(
    customer_id: int,
    issue: str,
    priority: str = "medium",
) -> Dict[str, Any]:
    """
    Create a new ticket for a given customer.

    Args:
        customer_id: tickets.customer_id (FK to customers.id)
        issue: description of the problem
        priority: 'low', 'medium', or 'high'

    Returns:
        dict with keys:
          - success: bool
          - ticket: dict or None
          - message: str
    """
    if priority not in ("low", "medium", "high"):
        return {
            "success": False,
            "ticket": None,
            "message": "Invalid priority; must be low, medium, or high.",
        }

    with get_conn() as conn:
        # Make sure customer exists
        exists = conn.execute(
            "SELECT 1 FROM customers WHERE id = ?",
            (customer_id,),
        ).fetchone()
        if not exists:
            return {
                "success": False,
                "ticket": None,
                "message": f"Customer {customer_id} does not exist.",
            }

        cur = conn.execute(
            """
            INSERT INTO tickets (customer_id, issue, status, priority)
            VALUES (?, ?, 'open', ?)
            """,
            (customer_id, issue, priority),
        )
        ticket_id = cur.lastrowid

        row = conn.execute(
            """
            SELECT id, customer_id, issue, status, priority, created_at
            FROM tickets
            WHERE id = ?
            """,
            (ticket_id,),
        ).fetchone()

    return {
        "success": True,
        "ticket": _row_to_dict(row),
        "message": "Ticket created successfully.",
    }


# ------------------------------------------------------------
# 5. get_customer_history(customer_id)
# ------------------------------------------------------------
def get_customer_history(customer_id: int) -> Dict[str, Any]:
    """
    Get ticket history for a given customer.

    Args:
        customer_id: tickets.customer_id

    Returns:
        dict with keys:
          - customer_id: int
          - ticket_count: int
          - tickets: list[dict]
    """
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, customer_id, issue, status, priority, created_at
            FROM tickets
            WHERE customer_id = ?
            ORDER BY created_at DESC
            """,
            (customer_id,),
        ).fetchall()

    return {
        "customer_id": customer_id,
        "ticket_count": len(rows),
        "tickets": [_row_to_dict(r) for r in rows],
    }
