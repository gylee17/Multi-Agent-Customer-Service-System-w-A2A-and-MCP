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
    messages: List[Message]  # messages produced by the agent
    done: bool = False       # whether the agent considers task complete

class Agent:
    role: Role

    def handle(self, message: Message, state: Dict[str, Any]) -> AgentResponse:
        """Process a message and optionally update state."""
        raise NotImplementedError
