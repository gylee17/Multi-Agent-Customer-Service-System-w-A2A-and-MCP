from typing import Dict, Any, List
from .base import Agent, Message, AgentResponse


class SupportAgent(Agent):
    role = "support_agent"

    def handle(self, message: Message, state: Dict[str, Any]) -> AgentResponse:
        logs: List[Message] = []

        intent = message.metadata.get("intent")
        logs.append(
            Message(
                sender="support_agent",
                recipient="router",
                content=f"[SupportAgent] Handling intent: {intent}",
                metadata={"debug": True},
            )
        )

        # --- Simple support (Scenario 1 final responder) ---
        if intent == "simple_support":
            cid = message.metadata.get("customer_id")
            customer = message.metadata.get("customer")
            response_text = f"I can help with your account (customer_id={cid})."
            if customer:
                response_text += f" I see we have {customer['name']} on file."
            logs.append(
                Message(
                    sender="support_agent",
                    recipient="router",
                    content=response_text,
                    metadata={"final_response": True},
                )
            )
            return AgentResponse(messages=logs, done=True)

        # --- Upgrade account support (coordinated query) ---
        if intent == "upgrade_account":
            cid = message.metadata.get("customer_id")
            customer = message.metadata.get("customer")
            response_text = "I can help upgrade your account."
            if customer:
                response_text += f" I see your account under {customer['name']}."
            response_text += " I’ll submit an upgrade request based on your current status."
            logs.append(
                Message(
                    sender="support_agent",
                    recipient="router",
                    content=response_text,
                    metadata={"final_response": True},
                )
            )
            return AgentResponse(messages=logs, done=True)

        # --- Negotiation start: billing + cancellation ---
        if intent == "billing_cancellation":
            logs.append(
                Message(
                    sender="support_agent",
                    recipient="router",
                    content="[SupportAgent] I need billing context to proceed with cancellation + refund.",
                    metadata={"request": "billing_context"},
                )
            )
            return AgentResponse(messages=logs, done=False)

        # --- High-priority escalation response ---
        if intent == "urgent_billing_escalation":
            ticket = message.metadata.get("ticket")
            response_text = (
                "I’m sorry you were charged twice. "
                "I’ve created a high-priority ticket for our billing team to review and issue a refund."
            )
            if ticket:
                response_text += f" Your ticket ID is {ticket['id']}."
            logs.append(
                Message(
                    sender="support_agent",
                    recipient="router",
                    content=response_text,
                    metadata={"final_response": True},
                )
            )
            return AgentResponse(messages=logs, done=True)

        # --- Ticket summary (Scenario 3) ---
        if intent == "ticket_summary":
            tickets = message.metadata.get("tickets", [])
            if not tickets:
                text = "There are no high-priority tickets for these customers."
            else:
                lines = [
                    f"Ticket #{t['id']} (customer_id={t['customer_id']}): {t['issue']} "
                    f"[{t['status']}, {t['priority']}]"
                    for t in tickets
                ]
                text = "High-priority tickets:\n" + "\n".join(lines)
            logs.append(
                Message(
                    sender="support_agent",
                    recipient="router",
                    content=text,
                    metadata={"final_response": True},
                )
            )
            return AgentResponse(messages=logs, done=True)

        # --- Email update + history combined reply ---
        if intent == "update_and_history_reply":
            ok = message.metadata.get("update_ok", False)
            history = message.metadata.get("history", [])
            text = "I’ve updated your email address. " if ok else "I tried to update your email, but something went wrong. "
            if history:
                text += "Here is your ticket history:\n"
                text += "\n".join(
                    f"- Ticket #{t['id']}: {t['issue']} [{t['status']}, {t['priority']}]"
                    for t in history
                )
            else:
                text += "You currently have no tickets on file."
            logs.append(
                Message(
                    sender="support_agent",
                    recipient="router",
                    content=text,
                    metadata={"final_response": True},
                )
            )
            return AgentResponse(messages=logs, done=True)

        # Fallback
        logs.append(
            Message(
                sender="support_agent",
                recipient="router",
                content="[SupportAgent] Unknown intent",
                metadata={"intent": intent},
            )
        )
        return AgentResponse(messages=logs, done=True)
