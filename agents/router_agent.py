from typing import Dict, Any, List
from .base import Agent, Message, AgentResponse
from .data_agent import CustomerDataAgent
from .support_agent import SupportAgent
from mcp_server.tools import get_customer_history  # for more complex scenarios later

class RouterAgent(Agent):
    role = "router"

    def __init__(self):
        self.data_agent = CustomerDataAgent()
        self.support_agent = SupportAgent()

    def _log(self, logs: List[Message], text: str):
        logs.append(Message(
            sender="router",
            recipient="router",
            content=f"[Router] {text}",
            metadata={"debug": True}
        ))

    def handle(self, message: Message, state: Dict[str, Any]) -> AgentResponse:
        logs: List[Message] = []
        user_query = message.content

        # Basic intent routing – you’ll expand this
        if "Get customer information for ID" in user_query:
            return self._handle_simple_get_customer(message, state, logs)

        # You will add:
        # - Scenario 1: "I need help with my account, customer ID ..."
        # - Scenario 2: cancellation + billing
        # - Scenario 3: high-priority tickets for premium customers
        # (plus test scenarios like update email + history)

        self._log(logs, "Defaulting to simple support")
        support_msg = Message(
            sender="router",
            recipient="support_agent",
            content="General support",
            metadata={"intent": "simple_support", "customer_id": None}
        )
        sup_resp = self.support_agent.handle(support_msg, state)
        logs.extend(sup_resp.messages)
        final_text = sup_resp.messages[-1].content
        logs.append(Message(
            sender="router",
            recipient="user",
            content=final_text,
            metadata={"scenario": "fallback"}
        ))
        return AgentResponse(messages=logs, done=True)

    # ---- Simple test scenario ----
    def _handle_simple_get_customer(self, message, state, logs):
        text = message.content
        cid = int(text.split("ID")[-1].strip())
        self._log(logs, f"Simple get_customer for id={cid}")

        data_msg = Message(
            sender="router",
            recipient="data_agent",
            content="Get customer info",
            metadata={"intent": "get_customer", "customer_id": cid}
        )
        data_resp = self.data_agent.handle(data_msg, state)
        logs.extend(data_resp.messages)

        customer = None
        for m in data_resp.messages:
            if m.content == "customer_info":
                customer = m.metadata["customer"]

        if not customer:
            final_text = f"No customer found with ID {cid}."
        else:
            final_text = f"Customer {cid}: {customer['name']} ({customer['email']})"

        logs.append(Message(
            sender="router",
            recipient="user",
            content=final_text,
            metadata={"scenario": "simple_query"}
        ))
        return AgentResponse(messages=logs, done=True)
