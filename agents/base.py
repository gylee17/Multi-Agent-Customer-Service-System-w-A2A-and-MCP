from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal

Role = Literal["user", "router", "data_agent", "support_agent"]


@dataclass
class Message:
    sender: Role
    recipient: Role
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentResponse:
    messages: List[Message]
    done: bool = False


class Agent:
    role: Role

    def handle(self, message: Message, state: Dict[str, Any]) -> AgentResponse:
        """Override in subclasses."""
        raise NotImplementedError
