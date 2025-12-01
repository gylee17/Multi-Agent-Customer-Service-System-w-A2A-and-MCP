# demo/run_scenarios_langgraph.py
"""
LangGraph-based multi-agent customer support system using A2A-style coordination.

- Router Agent (orchestrator)
- Customer Data Agent (specialist using DB "tools" / MCP layer)
- Support Agent (LLM that writes final responses)

Follows the same pattern as the class notebook:
- Uses StateGraph, TypedDict state, START/END, conditional edges
- Each node is an LLM-backed agent function that returns partial state
- Agent path is logged in `agent_log`
"""

import os
import re
from typing import TypedDict, Optional, List, Dict, Any

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI

# These should be your DB/MCP tool wrappers.
# Adjust the import path if your tools live elsewhere.
from mcp_server.tools import (
    get_customer,
    list_customers,
    get_customer_history,
    create_ticket,
    update_customer,
)


# 0. Ensure API key (Colab / local)
if "OPENAI_API_KEY" not in os.environ:
    print("⚠️ WARNING: OPENAI_API_KEY is not set in environment. "
          "Set it before running if you haven't already.")


# =====================================================
# 1. Shared State Definition (LangGraph-style)
# =====================================================
class SupportState(TypedDict, total=False):
    # User input query
    input: str

    # Routing / control
    route: Optional[str]           # "simple_data", "support_only", "data_then_support"
    needs_support: Optional[bool]  # whether SupportAgent should run after DataAgent

    # Parsed info
    customer_id: Optional[int]
    new_email: Optional[str]

    # Data pulled from DB
    customer: Optional[Dict[str, Any]]
    tickets: Optional[List[Dict[str, Any]]]

    # Final output + logs
    response: Optional[str]
    agent_log: List[str]


# =====================================================
# 2. Helper: Init state from user query
# =====================================================
def init_state(user_query: str) -> SupportState:
    """Initialize state from a raw user query."""
    return {
        "input": user_query,
        "agent_log": [],
    }


# =====================================================
# 3. LLM + simple parsing helpers
# =====================================================
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def extract_customer_id_from_text(text: str) -> Optional[int]:
    """Find a customer ID in the text (simple regex)."""
    m = re.search(r"\b(\d{1,6})\b", text)
    if m:
        try:
            return int(m.group(1))
        except ValueError:
            return None
    return None


def extract_email_from_text(text: str) -> Optional[str]:
    """Very simple email regex."""
    m = re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)
    if m:
        return m.group(0)
    return None


# =====================================================
# 4. Router Agent (LLM-based) — decides route
# =====================================================
def router_agent(state: SupportState) -> SupportState:
    """
    Router analyzes the user query and decides:

    - route:
        - "simple_data": just data lookup (e.g., "Get customer information for ID 5")
        - "data_then_support": need both data + support (e.g., upgrade, email update + history)
        - "support_only": pure support (e.g., refund / charged twice)
    - It also tries to extract customer_id and new_email.
    """
    query = state["input"]

    # Use LLM to pick general route
    prompt = f"""
    You are a router agent in a customer support system.
    Decide how this query should be handled:

    QUERY: "{query}"

    If it's asking ONLY for information (like "get info for ID X"),
    choose: simple_data.

    If it needs both data lookup AND a support reply
    (like "I'm customer 12345 and need help upgrading", or
     "update my email and show my ticket history"),
    choose: data_then_support.

    If it's mostly a support/complaint or escalation
    (like "I've been charged twice, please refund immediately!"),
    choose: support_only.

    Respond with ONE of:
    - simple_data
    - data_then_support
    - support_only
    """
    route = llm.invoke(prompt).content.strip().lower()

    # Normalize to one of the three valid routes
    if route not in ("simple_data", "data_then_support", "support_only"):
        route = "support_only"

    # Best-effort extraction of customer id & email
    cid = extract_customer_id_from_text(query)
    email = extract_email_from_text(query)

    # Log decision
    logs = state.get("agent_log", [])
    logs.append(f"Router → route={route}, customer_id={cid}, new_email={email}")

    # IMPORTANT CHANGE:
    # We now also let SupportAgent run for simple_data so that it can
    # turn raw customer_record into a nice human-readable answer.
    needs_support = route in ("data_then_support", "support_only", "simple_data")

    new_state: SupportState = {
        **state,
        "route": route,
        "customer_id": cid,
        "new_email": email,
        "needs_support": needs_support,
        "agent_log": logs,
    }
    return new_state


# =====================================================
# 5. Customer Data Agent — uses DB/MCP tools
# =====================================================
def data_agent(state: SupportState) -> SupportState:
    """
    Customer Data Agent: uses DB/MCP tools to get or update information.

    It examines the route + parsed info to decide which tools to call.
    """
    route = state.get("route", "")
    cid = state.get("customer_id")
    new_email = state.get("new_email")
    query = state["input"]
    logs = state.get("agent_log", [])

    customer = None
    tickets: List[Dict[str, Any]] = []

    # 1) Simple "Get customer information" scenario
    if "simple_data" in route and cid is not None:
        result = get_customer(cid)
        customer = result.get("customer")
        logs.append(f"DataAgent → get_customer({cid})")

    # 2) Multi-intent: update email + show history
    if "update my email" in query.lower() and cid is not None and new_email:
        # update_customer
        update_result = update_customer(cid, {"email": new_email})
        logs.append(f"DataAgent → update_customer({cid}, email={new_email}) "
                    f"→ success={update_result.get('success')}")

        # ticket history
        hist_result = get_customer_history(cid)
        tickets = hist_result.get("tickets", [])
        logs.append(f"DataAgent → get_customer_history({cid}) "
                    f"→ {len(tickets)} tickets")

        # We definitely want SupportAgent to summarize this
        state["needs_support"] = True

    # 3) Complex: "Show me all active customers who have open tickets"
    if "active customers" in query.lower() and "open tickets" in query.lower():
        # list active customers
        cust_result = list_customers(status="active", limit=100)
        customers = cust_result.get("customers", [])
        logs.append(f"DataAgent → list_customers(status='active') "
                    f"→ {len(customers)} customers")

        # filter customers that have any tickets
        customers_with_tickets = []
        for c in customers:
            c_id = c.get("id")
            if c_id is None:
                continue
            hist = get_customer_history(c_id)
            tix = hist.get("tickets", [])
            if any(t.get("status") in ("open", "in_progress") for t in tix):
                customers_with_tickets.append(
                    {
                        "customer": c,
                        "tickets": tix,
                    }
                )

        # store summary in state as "tickets" (list of dicts)
        tickets = customers_with_tickets
        logs.append(f"DataAgent → aggregated open-ticket customers={len(customers_with_tickets)}")

        # We want SupportAgent to format the final report
        state["needs_support"] = True

    # 4) Scenario: "I'm customer 12345 and need help upgrading my account"
    #    → DataAgent fetches the customer, SupportAgent proposes upgrade help.
    if "upgrade" in query.lower() and cid is not None:
        result = get_customer(cid)
        customer = result.get("customer")
        logs.append(f"DataAgent → get_customer({cid}) for upgrade flow")
        state["needs_support"] = True

    # 5) Generic fallback: if we have a clear customer ID, at least fetch it
    if customer is None and cid is not None and "simple_data" not in route:
        result = get_customer(cid)
        customer = result.get("customer")
        logs.append(f"DataAgent → get_customer({cid}) [fallback]")

    new_state: SupportState = {
        **state,
        "customer": customer,
        "tickets": tickets,
        "agent_log": logs,
    }
    return new_state


# =====================================================
# 6. Support Agent — LLM that writes the reply
# =====================================================
def support_agent(state: SupportState) -> SupportState:
    """
    Support Agent: generates the final response using the query + data in state.
    It uses the LLM to produce a user-friendly answer.
    """
    query = state["input"]
    customer = state.get("customer")
    tickets = state.get("tickets")
    logs = state.get("agent_log", [])

    # Build a context string from DB data
    context_parts = []

    if customer:
        context_parts.append(
            f"Customer: id={customer.get('id')}, "
            f"name={customer.get('name')}, "
            f"email={customer.get('email')}, "
            f"status={customer.get('status')}"
        )

    if isinstance(tickets, list) and tickets:
        if tickets and isinstance(tickets[0], dict) and "customer" in tickets[0]:
            # special case for "active customers with open tickets"
            # where tickets is actually a list of {customer, tickets}
            ctx = []
            for entry in tickets:
                c = entry.get("customer", {})
                tix = entry.get("tickets", [])
                open_tix = [t for t in tix if t.get("status") in ("open", "in_progress")]
                if not open_tix:
                    continue
                ctx.append(
                    f"- {c.get('name')} (id={c.get('id')}, status={c.get('status')}): "
                    f"{len(open_tix)} open/in-progress tickets"
                )
            if ctx:
                context_parts.append(
                    "Active customers with open tickets:\n" + "\n".join(ctx)
                )
        else:
            # standard ticket history list for one customer
            lines = []
            for t in tickets:
                lines.append(
                    f"- Ticket #{t.get('id')}: {t.get('issue')} "
                    f"[{t.get('status')}, {t.get('priority')}]"
                )
            context_parts.append("Ticket history:\n" + "\n".join(lines))

    context_str = "\n".join(context_parts) if context_parts else "No extra context retrieved."

    prompt = f"""
    You are a helpful customer support agent.

    USER QUERY:
    {query}

    CONTEXT FROM DATA AGENT:
    {context_str}

    TASK:
    - Answer the user's question or resolve their issue.
    - If there is billing urgency (e.g., charged twice), be empathetic and state that a refund or investigation will be initiated.
    - If it's an account upgrade or email update, confirm the change and summarize any ticket history if available.
    - If the user asked for a report (e.g. active customers with open tickets), summarize clearly.

    Respond in a concise and professional tone.
    """

    answer = llm.invoke(prompt).content.strip()

    logs.append("SupportAgent → generated final response")

    new_state: SupportState = {
        **state,
        "response": answer,
        "agent_log": logs,
    }
    return new_state


# =====================================================
# 7. Build LangGraph with router → conditional edges
# =====================================================
graph = StateGraph(SupportState)

graph.add_node("Router", router_agent)
graph.add_node("DataAgent", data_agent)
graph.add_node("SupportAgent", support_agent)

graph.add_edge(START, "Router")


# Router → next node based on route
def route_decision(state: SupportState) -> str:
    route = (state.get("route") or "").lower()

    # Only data
    if "simple_data" in route:
        return "DataAgent"

    # Data then support
    if "data_then_support" in route:
        return "DataAgent"

    # Pure support
    if "support_only" in route:
        return "SupportAgent"

    # Fallback: try support
    return "SupportAgent"


graph.add_conditional_edges(
    "Router",
    route_decision,
    {
        "DataAgent": "DataAgent",
        "SupportAgent": "SupportAgent",
    },
)

# DataAgent → either SupportAgent or END
def data_next(state: SupportState) -> str:
    if state.get("needs_support"):
        return "SupportAgent"
    return "__end__"


graph.add_conditional_edges(
    "DataAgent",
    data_next,
    {
        "SupportAgent": "SupportAgent",
        "__end__": END,
    },
)

graph.add_edge("SupportAgent", END)

router_system = graph.compile()


# =====================================================
# 8. Run required test scenarios
# =====================================================
def run_scenarios():
    test_queries = [
        # Simple Query
        "Get customer information for ID 5",

        # Coordinated Query (data + support)
        "I'm customer 12345 and need help upgrading my account",

        # Complex Query: active customers with open tickets
        "Show me all active customers who have open tickets",

        # Escalation
        "I've been charged twice, please refund immediately!",

        # Multi-Intent
        "Update my email to new@email.com and show my ticket history for customer 1",
    ]

    print("\nRunning LangGraph-based Multi-Agent System...\n")

    for q in test_queries:
        print("=" * 60)
        print(f"USER QUERY: {q}")
        print("=" * 60)

        result = router_system.invoke(init_state(q))

        print("\n--- Agent Log ---")
        for entry in result.get("agent_log", []):
            print(entry)

        print("\n--- Final Response ---")
        print(result.get("response", "<no response>"))
        print("\n")


if __name__ == "__main__":
    run_scenarios()
