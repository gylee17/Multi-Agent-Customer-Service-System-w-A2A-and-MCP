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
    run_query("Get customer information for ID 5")
