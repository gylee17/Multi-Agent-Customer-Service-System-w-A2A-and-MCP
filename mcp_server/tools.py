from typing import List, Dict, Any, Optional
from .db import get_conn

def get_customer(customer_id: int) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM customers WHERE id = ?",
            (customer_id,)
        ).fetchone()
        return dict(row) if row else None

def list_customers(status: str, limit: int = 50) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM customers WHERE status = ? LIMIT ?",
            (status, limit)
        ).fetchall()
        return [dict(r) for r in rows]

def update_customer(customer_id: int, data: Dict[str, Any]) -> bool:
    if not data:
        return False

    columns = []
    params = []
    for key, value in data.items():
        columns.append(f"{key} = ?")
        params.append(value)

    params.append(customer_id)
    sql = f"""
        UPDATE customers
        SET {', '.join(columns)}, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """
    with get_conn() as conn:
        cur = conn.execute(sql, tuple(params))
        return cur.rowcount > 0

def create_ticket(customer_id: int, issue: str, priority: str = "medium") -> Dict[str, Any]:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO tickets (customer_id, issue, status, priority, created_at)
            VALUES (?, ?, 'open', ?, CURRENT_TIMESTAMP)
            """,
            (customer_id, issue, priority),
        )
        ticket_id = cur.lastrowid
        row = conn.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (ticket_id,)
        ).fetchone()
        return dict(row)

def get_customer_history(customer_id: int) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM tickets WHERE customer_id = ? ORDER BY created_at DESC",
            (customer_id,)
        ).fetchall()
        return [dict(r) for r in rows]
