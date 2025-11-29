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
        logs.append(
            Message(
                sender="data_agent",
                recipient="router",
                content=f"[DataAgent] Received intent: {intent}",
                metadata={"debug": True},
            )
        )

        # --- Basic customer lookup ---
        if intent == "get_customer":
            cid = message.metadata["customer_id"]
            customer = get_customer(cid)
            logs.append(
                Message(
                    sender="data_agent",
                    recipient="router",
                    content="customer_info",
                    metadata={"customer": customer},
                )
            )
            return AgentResponse(messages=logs, done=True)

        # --- Customer history (tickets) ---
        if intent == "get_customer_history":
            cid = message.metadata["customer_id"]
            history = get_customer_history(cid)
            logs.append(
                Message(
                    sender="data_agent",
                    recipient="router",
                    content="customer_history",
                    metadata={"history": history},
                )
            )
            return AgentResponse(messages=logs, done=True)

        # --- Premium customers (for this assignment, treat 'active' as premium) ---
        if intent == "get_premium_customers":
            customers = list_customers(status="active", limit=1000)
            logs.append(
                Message(
                    sender="data_agent",
                    recipient="router",
                    content="premium_customers",
                    metadata={"customers": customers},
                )
            )
            return AgentResponse(messages=logs, done=True)

        # --- All active customers ---
        if intent == "get_active_customers":
            customers = list_customers(status="active", limit=1000)
            logs.append(
                Message(
                    sender="data_agent",
                    recipient="router",
                    content="active_customers",
                    metadata={"customers": customers},
                )
            )
            return AgentResponse(messages=logs, done=True)

        # --- Create ticket ---
        if intent == "create_ticket":
            cid = message.metadata["customer_id"]
            issue = message.metadata["issue"]
            priority = message.metadata.get("priority", "medium")
            ticket = create_ticket(cid, issue, priority)
            logs.append(
                Message(
                    sender="data_agent",
                    recipient="router",
                    content="ticket_created",
                    metadata={"ticket": ticket},
                )
            )
            return AgentResponse(messages=logs, done=True)

        # --- Update customer email ---
        if intent == "update_customer_email":
            cid = message.metadata["customer_id"]
            new_email = message.metadata["email"]
            ok = update_customer(cid, {"email": new_email})
            logs.append(
                Message(
                    sender="data_agent",
                    recipient="router",
                    content="customer_updated",
                    metadata={"success": ok, "field": "email", "value": new_email},
                )
            )
            return AgentResponse(messages=logs, done=True)

        # Fallback
        logs.append(
            Message(
                sender="data_agent",
                recipient="router",
                content="[DataAgent] Unknown intent",
                metadata={"intent": intent},
            )
        )
        return AgentResponse(messages=logs, done=True)
