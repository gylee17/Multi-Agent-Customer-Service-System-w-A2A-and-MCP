from typing import Dict, Any, List
from .base import Agent, Message, AgentResponse
from mcp_server.tools import (
    get_customer,
    list_customers,
    update_customer,
    create_ticket,
    get_customer_history,
)

class CustomerDataAgent(Agent):
    role = "data_agent"

    def handle(self, message: Message, state: Dict[str, Any]) -> AgentResponse:
        logs: List[Message] = []

        intent = message.metadata.get("intent")
        logs.append(Message(
            sender="data_agent",
            recipient="router",
            content=f"[DataAgent] Received intent: {intent}",
            metadata={"debug": True}
        ))

        if intent == "get_customer":
            cid = message.metadata["customer_id"]
            customer = get_customer(cid)
            logs.append(Message(
                sender="data_agent",
                recipient="router",
                content="customer_info",
                metadata={"customer": customer}
            ))
            return AgentResponse(messages=logs, done=True)

        if intent == "get_customer_history":
            cid = message.metadata["customer_id"]
            history = get_customer_history(cid)
            logs.append(Message(
                sender="data_agent",
                recipient="router",
                content="customer_history",
                metadata={"history": history}
            ))
            return AgentResponse(messages=logs, done=True)

        # You can add more intents here: list_premium, update_customer, create_ticket, etc.

        logs.append(Message(
            sender="data_agent",
            recipient="router",
            content="[DataAgent] Unknown intent",
            metadata={"intent": intent}
        ))
        return AgentResponse(messages=logs, done=True)
