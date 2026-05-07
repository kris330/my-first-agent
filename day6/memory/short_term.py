from dataclasses import dataclass, field
from typing import Literal

MessageRole = Literal["system", "user", "assistant"]


@dataclass
class Message:
    role: MessageRole
    content: str


@dataclass
class ShortTermMemory:
    max_messages: int = 30
    _messages: list[Message] = field(default_factory=list)

    def add(self, role: MessageRole, content: str) -> None:
        self._messages.append(Message(role=role, content=content))
        self._trim()

    def _trim(self) -> None:
        non_system = [m for m in self._messages if m.role != "system"]
        while len(non_system) > self.max_messages:
            for i, msg in enumerate(self._messages):
                if msg.role != "system":
                    self._messages.pop(i)
                    break
            non_system = [m for m in self._messages if m.role != "system"]

    def to_api_format(self) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self._messages]

    def clear_non_system(self) -> None:
        self._messages = [m for m in self._messages if m.role == "system"]
