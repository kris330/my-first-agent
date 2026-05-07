from dataclasses import dataclass, field
from typing import Literal

MessageRole = Literal["system", "user", "assistant"]


@dataclass
class Message:
    role: MessageRole
    content: str


@dataclass
class ShortTermMemory:
    """
    保存对话历史，控制上限，防止超过 token 限制。
    system 消息永远保留，超出上限时删除最旧的非 system 消息。
    """
    max_messages: int = 20
    _messages: list[Message] = field(default_factory=list)

    def add(self, role: MessageRole, content: str) -> None:
        self._messages.append(Message(role=role, content=content))
        self._trim()

    def _trim(self) -> None:
        """超过上限时，删除最旧的非 system 消息。"""
        non_system = [m for m in self._messages if m.role != "system"]
        while len(non_system) > self.max_messages:
            for i, msg in enumerate(self._messages):
                if msg.role != "system":
                    self._messages.pop(i)
                    break
            non_system = [m for m in self._messages if m.role != "system"]

    def to_api_format(self) -> list[dict]:
        """转成 OpenAI API 需要的格式。"""
        return [{"role": m.role, "content": m.content} for m in self._messages]

    def clear_non_system(self) -> None:
        """清除所有非 system 消息（开始新对话时使用）。"""
        self._messages = [m for m in self._messages if m.role == "system"]

    def message_count(self) -> int:
        return len([m for m in self._messages if m.role != "system"])
