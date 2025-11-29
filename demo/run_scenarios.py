from agents.base import Message
from agents.router_agent import RouterAgent


def run_query(query: str, state=None):
    if state is None:
        state = {}

    router = RouterAgent()
    msg = Message(sender="user", recipient="router", content=query, metadata={})
    resp = router.handle(msg, state)

    print("\n=== Conversation Log ===")
    for m in resp.messages:
        print(f"{m.sender} → {m.recipient}: {m.content} | meta={m.metadata}")

    print("\n=== Final Answer to User ===")
    final_msgs = [m for m in resp.messages if m.recipient == "user"]
    print(final_msgs[-1].content if final_msgs else "(no user message)")


if __name__ == "__main__":
    queries = [
        # Simple Query
        "Get customer information for ID 5",
        # Scenario 1: Task Allocation
        "I need help with my account, customer ID 12345",
        # Scenario 2: Negotiation / Escalation
        "I want to cancel my subscription but I'm having billing issues",
        # Scenario 3: Multi-Step Coordination
        "What's the status of all high-priority tickets for premium customers?",
        # Complex Query
        "Show me all active customers who have open tickets",
        # Escalation
        "I've been charged twice, please refund immediately!",
        # Multi-Intent
        "Update my email to new@email.com and show my ticket history",
    ]

    for q in queries:
        print("\n\n==============================")
        print("User query:", q)
        print("==============================")
        run_query(q)
