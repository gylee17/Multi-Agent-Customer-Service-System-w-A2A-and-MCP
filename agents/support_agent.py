from typing import Dict, Any, List
from .base import Agent, Message, AgentResponse

class SupportAgent(Agent):
    role = "support_agent"

    def handle(self, message: Message, state: Dict[str, Any]) -> AgentResponse:
        logs: List[Message] = []

        intent = message.metadata.get("intent")
        logs.append(Message(
            sender="support_agent",
            recipient="router",
            content=f"[SupportAgent] Handling intent: {intent}",
            metadata={"debug": True}
        ))

        if intent == "simple_support":
            cid = message.metadata.get("customer_id")
            customer = message.metadata.get("customer")
            response_text = f"I can help with your account (customer_id={cid})."
            if customer:
                response_text += f" I see we have {customer['name']} on file."

            logs.append(Message(
                sender="support_agent",
                recipient="router",
                content=response_text,
                metadata={"final_response": True}
            ))
            return AgentResponse(messages=logs, done=True)

        if intent == "billing_cancellation":
            # This is where negotiation happens
            logs.append(Message(
                sender="support_agent",
                recipient="router",
                content="[SupportAgent] I need billing context to proceed.",
                metadata={"request": "billing_context"}
            ))
            return AgentResponse(messages=logs, done=False)

        logs.append(Message(
            sender="support_agent",
            recipient="router",
            content="[SupportAgent] Unknown intent",
            metadata={"intent": intent}
        ))
        return AgentResponse(messages=logs, done=True)
