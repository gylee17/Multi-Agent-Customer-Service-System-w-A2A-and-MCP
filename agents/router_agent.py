from typing import Dict, Any, List
from .base import Agent, Message, AgentResponse
from .data_agent import CustomerDataAgent
from .support_agent import SupportAgent
from mcp_server.tools import get_customer_history


class RouterAgent(Agent):
    role = "router"

    def __init__(self):
        self.data_agent = CustomerDataAgent()
        self.support_agent = SupportAgent()

    def _log(self, logs: List[Message], text: str):
        logs.append(
            Message(
                sender="router",
                recipient="router",
                content=f"[Router] {text}",
                metadata={"debug": True},
            )
        )

    # Utility: extract first integer after a phrase
    def _extract_id_after_phrase(self, text: str, phrase: str, default: int = 1) -> int:
        try:
            part = text.split(phrase, 1)[-1]
            digits = "".join(ch for ch in part if ch.isdigit())
            return int(digits) if digits else default
        except Exception:
            return default

    def _extract_email(self, text: str) -> str:
        # Very simple heuristic: take the first token with '@'
        for token in text.replace(",", " ").split():
            if "@" in token:
                return token.strip()
        return ""

    # ------------------------------------------------------------------
    # Main handler
    # ------------------------------------------------------------------
    def handle(self, message: Message, state: Dict[str, Any]) -> AgentResponse:
        logs: List[Message] = []
        user_query = message.content

        # Scenario 1: Task allocation
        if "I need help with my account" in user_query and "customer ID" in user_query:
            return self._handle_task_allocation(message, state, logs)

        # Scenario 2: Negotiation / Escalation
        if "cancel my subscription" in user_query and "billing" in user_query:
            return self._handle_billing_cancellation(message, state, logs)

        # Scenario 3: Multi-step high-priority tickets
        if "status of all high-priority tickets for premium customers" in user_query:
            return self._handle_high_priority_for_premium(message, state, logs)

        # Complex query: active customers with open tickets
        if "Show me all active customers who have open tickets" in user_query:
            return self._handle_active_with_open_tickets(message, state, logs)

        # Escalation: charged twice
        if "charged twice" in user_query and "refund" in user_query:
            return self._handle_urgent_refund(message, state, logs)

        # Multi-intent: update email + history
        if "Update my email to" in user_query and "show my ticket history" in user_query:
            return self._handle_update_email_and_history(message, state, logs)

        # Simple query used in assignment
        if "Get customer information for ID" in user_query:
            return self._handle_simple_get_customer(message, state, logs)

        # Fallback
        self._log(logs, "Defaulting to simple support")
        support_msg = Message(
            sender="router",
            recipient="support_agent",
            content="General support",
            metadata={"intent": "simple_support", "customer_id": None},
        )
        sup_resp = self.support_agent.handle(support_msg, state)
        logs.extend(sup_resp.messages)
        final_text = sup_resp.messages[-1].content
        logs.append(
            Message(
                sender="router",
                recipient="user",
                content=final_text,
                metadata={"scenario": "fallback"},
            )
        )
        return AgentResponse(messages=logs, done=True)

    # ------------------------------------------------------------------
    # Simple get_customer (already working)
    # ------------------------------------------------------------------
    def _handle_simple_get_customer(self, message, state, logs):
        text = message.content
        cid = self._extract_id_after_phrase(text, "ID", default=1)
        self._log(logs, f"Simple get_customer for id={cid}")

        data_msg = Message(
            sender="router",
            recipient="data_agent",
            content="Get customer info",
            metadata={"intent": "get_customer", "customer_id": cid},
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

        logs.append(
            Message(
                sender="router",
                recipient="user",
                content=final_text,
                metadata={"scenario": "simple_query"},
            )
        )
        return AgentResponse(messages=logs, done=True)

    # ------------------------------------------------------------------
    # Scenario 1: Task allocation
    # ------------------------------------------------------------------
    def _handle_task_allocation(self, message, state, logs):
        text = message.content
        cid = self._extract_id_after_phrase(text, "customer ID", default=1)
        self._log(logs, f"Scenario 1: task allocation for customer_id={cid}")

        # Router → DataAgent
        data_msg = Message(
            sender="router",
            recipient="data_agent",
            content="Get customer info",
            metadata={"intent": "get_customer", "customer_id": cid},
        )
        data_resp = self.data_agent.handle(data_msg, state)
        logs.extend(data_resp.messages)

        customer = None
        for m in data_resp.messages:
            if m.content == "customer_info":
                customer = m.metadata["customer"]

        # Router → SupportAgent
        support_msg = Message(
            sender="router",
            recipient="support_agent",
            content="Handle support for this account",
            metadata={
                "intent": "simple_support",
                "customer_id": cid,
                "customer": customer,
            },
        )
        sup_resp = self.support_agent.handle(support_msg, state)
        logs.extend(sup_resp.messages)

        final_text = sup_resp.messages[-1].content
        logs.append(
            Message(
                sender="router",
                recipient="user",
                content=final_text,
                metadata={"scenario": "task_allocation"},
            )
        )
        return AgentResponse(messages=logs, done=True)

    # ------------------------------------------------------------------
    # Scenario 2: Negotiation / Escalation
    # ------------------------------------------------------------------
    def _handle_billing_cancellation(self, message, state, logs):
        self._log(logs, "Scenario 2: cancellation + billing negotiation")

        # Router → SupportAgent: can you handle?
        support_msg = Message(
            sender="router",
            recipient="support_agent",
            content=message.content,
            metadata={"intent": "billing_cancellation"},
        )
        sup_resp = self.support_agent.handle(support_msg, state)
        logs.extend(sup_resp.messages)

        # Check if SupportAgent requested billing context
        needs_billing = any(
            m.metadata.get("request") == "billing_context" for m in sup_resp.messages
        )

        history = []
        if needs_billing:
            cid = state.get("customer_id", 1)  # simplified assumption
            data_msg = Message(
                sender="router",
                recipient="data_agent",
                content="Get customer history",
                metadata={"intent": "get_customer_history", "customer_id": cid},
            )
            data_resp = self.data_agent.handle(data_msg, state)
            logs.extend(data_resp.messages)

            for m in data_resp.messages:
                if m.content == "customer_history":
                    history = m.metadata["history"]

        final_text = (
            "I can help cancel your subscription and review your billing history. "
            "Based on your recent tickets, I’ll prioritize resolving the billing issues."
        )

        logs.append(
            Message(
                sender="router",
                recipient="user",
                content=final_text,
                metadata={"scenario": "negotiation_escalation", "tickets": history},
            )
        )
        return AgentResponse(messages=logs, done=True)

    # ------------------------------------------------------------------
    # Scenario 3: Multi-step high-priority tickets
    # ------------------------------------------------------------------
    def _handle_high_priority_for_premium(self, message, state, logs):
        self._log(logs, "Scenario 3: multi-step coordination for high-priority tickets")

        # Step 1: get premium customers
        data_msg = Message(
            sender="router",
            recipient="data_agent",
            content="Get premium customers",
            metadata={"intent": "get_premium_customers"},
        )
        data_resp = self.data_agent.handle(data_msg, state)
        logs.extend(data_resp.messages)

        premium_customers = []
        for m in data_resp.messages:
            if m.content == "premium_customers":
                premium_customers = m.metadata["customers"]

        premium_ids = [c["id"] for c in premium_customers]

        # Step 2: collect high-priority tickets
        high_tickets = []
        for cid in premium_ids:
            history = get_customer_history(cid)
            for t in history:
                if t["priority"] == "high":
                    high_tickets.append(t)

        # Step 3: summary via SupportAgent
        support_msg = Message(
            sender="router",
            recipient="support_agent",
            content="Summarize high-priority tickets",
            metadata={"intent": "ticket_summary", "tickets": high_tickets},
        )
        sup_resp = self.support_agent.handle(support_msg, state)
        logs.extend(sup_resp.messages)

        final_text = (
            sup_resp.messages[-1].content if sup_resp.messages else "No high-priority tickets found."
        )
        logs.append(
            Message(
                sender="router",
                recipient="user",
                content=final_text,
                metadata={"scenario": "multi_step"},
            )
        )
        return AgentResponse(messages=logs, done=True)

    # ------------------------------------------------------------------
    # Complex query: active customers with open tickets
    # ------------------------------------------------------------------
    def _handle_active_with_open_tickets(self, message, state, logs):
        self._log(logs, "Complex query: active customers with open tickets")

        # Get all active customers
        data_msg = Message(
            sender="router",
            recipient="data_agent",
            content="Get active customers",
            metadata={"intent": "get_active_customers"},
        )
        data_resp = self.data_agent.handle(data_msg, state)
        logs.extend(data_resp.messages)

        active_customers = []
        for m in data_resp.messages:
            if m.content == "active_customers":
                active_customers = m.metadata["customers"]

        open_by_customer = {}
        for c in active_customers:
            cid = c["id"]
            history = get_customer_history(cid)
            open_tickets = [t for t in history if t["status"] == "open"]
            if open_tickets:
                open_by_customer[cid] = {
                    "customer": c,
                    "tickets": open_tickets,
                }

        if not open_by_customer:
            final_text = "No active customers currently have open tickets."
        else:
            lines = []
            for cid, info in open_by_customer.items():
                cust = info["customer"]
                tickets = info["tickets"]
                lines.append(
                    f"Customer {cid} ({cust['name']}): {len(tickets)} open ticket(s)"
                )
            final_text = "Active customers with open tickets:\n" + "\n".join(lines)

        logs.append(
            Message(
                sender="router",
                recipient="user",
                content=final_text,
                metadata={"scenario": "complex_active_open"},
            )
        )
        return AgentResponse(messages=logs, done=True)

    # ------------------------------------------------------------------
    # Escalation: charged twice, refund immediately
    # ------------------------------------------------------------------
    def _handle_urgent_refund(self, message, state, logs):
        self._log(logs, "Escalation: urgent double-charge refund")

        cid = state.get("customer_id", 1)
        issue = message.content

        # Create high-priority ticket via DataAgent
        data_msg = Message(
            sender="router",
            recipient="data_agent",
            content="Create urgent billing ticket",
            metadata={
                "intent": "create_ticket",
                "customer_id": cid,
                "issue": issue,
                "priority": "high",
            },
        )
        data_resp = self.data_agent.handle(data_msg, state)
        logs.extend(data_resp.messages)

        ticket = None
        for m in data_resp.messages:
            if m.content == "ticket_created":
                ticket = m.metadata["ticket"]

        # SupportAgent constructs escalation response
        support_msg = Message(
            sender="router",
            recipient="support_agent",
            content="Urgent billing escalation",
            metadata={"intent": "urgent_billing_escalation", "ticket": ticket},
        )
        sup_resp = self.support_agent.handle(support_msg, state)
        logs.extend(sup_resp.messages)

        final_text = sup_resp.messages[-1].content
        logs.append(
            Message(
                sender="router",
                recipient="user",
                content=final_text,
                metadata={"scenario": "urgent_refund"},
            )
        )
        return AgentResponse(messages=logs, done=True)

    # ------------------------------------------------------------------
    # Multi-intent: update email + show ticket history
    # ------------------------------------------------------------------
    def _handle_update_email_and_history(self, message, state, logs):
        self._log(logs, "Multi-intent: update email + show history")

        cid = state.get("customer_id", 1)
        new_email = self._extract_email(message.content)

        # Step 1: update email
        update_msg = Message(
            sender="router",
            recipient="data_agent",
            content="Update customer email",
            metadata={
                "intent": "update_customer_email",
                "customer_id": cid,
                "email": new_email,
            },
        )
        update_resp = self.data_agent.handle(update_msg, state)
        logs.extend(update_resp.messages)

        update_ok = False
        for m in update_resp.messages:
            if m.content == "customer_updated":
                update_ok = m.metadata["success"]

        # Step 2: get history
        history_msg = Message(
            sender="router",
            recipient="data_agent",
            content="Get customer history",
            metadata={"intent": "get_customer_history", "customer_id": cid},
        )
        history_resp = self.data_agent.handle(history_msg, state)
        logs.extend(history_resp.messages)

        history = []
        for m in history_resp.messages:
            if m.content == "customer_history":
                history = m.metadata["history"]

        # Step 3: SupportAgent formats combined reply
        support_msg = Message(
            sender="router",
            recipient="support_agent",
            content="Update + history combined reply",
            metadata={
                "intent": "update_and_history_reply",
                "update_ok": update_ok,
                "history": history,
            },
        )
        sup_resp = self.support_agent.handle(support_msg, state)
        logs.extend(sup_resp.messages)

        final_text = sup_resp.messages[-1].content
        logs.append(
            Message(
                sender="router",
                recipient="user",
                content=final_text,
                metadata={"scenario": "multi_intent"},
            )
        )
        return AgentResponse(messages=logs, done=True)
