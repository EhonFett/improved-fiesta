from __future__ import annotations
import random
import time
from dataclasses import dataclass, field
from typing import Any

CHANNELS = ["general", "sprint-standup", "dev", "architecture", "production-incidents", "random"]


@dataclass
class ChatMessage:
    id: str
    channel: str
    author: str
    role: str
    text: str
    timestamp: float
    reactions: dict[str, list[str]] = field(default_factory=dict)  # emoji -> [names]
    thread: list["ChatMessage"] = field(default_factory=list)
    is_typing_placeholder: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "channel": self.channel,
            "author": self.author,
            "role": self.role,
            "text": self.text,
            "timestamp": self.timestamp,
            "reactions": self.reactions,
            "thread": [m.to_dict() for m in self.thread],
        }


class ChatSystem:
    def __init__(self) -> None:
        self._channels: dict[str, list[ChatMessage]] = {ch: [] for ch in CHANNELS}
        self._dms: dict[str, list[ChatMessage]] = {}
        self._msg_counter = 0
        self._pending_reactions: list[dict] = []
        self._subscribers: list = []  # async callbacks

    def _next_id(self) -> str:
        self._msg_counter += 1
        return f"msg-{self._msg_counter:06d}"

    def post(self, channel: str, author: str, role: str, text: str) -> ChatMessage:
        msg = ChatMessage(
            id=self._next_id(),
            channel=channel,
            author=author,
            role=role,
            text=text,
            timestamp=time.time(),
        )
        if channel not in self._channels:
            self._channels[channel] = []
        self._channels[channel].append(msg)
        return msg

    def add_reaction(self, msg_id: str, channel: str, emoji: str, author: str) -> bool:
        for msg in self._channels.get(channel, []):
            if msg.id == msg_id:
                msg.reactions.setdefault(emoji, [])
                if author not in msg.reactions[emoji]:
                    msg.reactions[emoji].append(author)
                return True
        return False

    def get_channel(self, channel: str, last_n: int = 50) -> list[ChatMessage]:
        return self._channels.get(channel, [])[-last_n:]

    def get_all_channels_summary(self) -> dict[str, int]:
        return {ch: len(msgs) for ch, msgs in self._channels.items()}

    def to_dict(self) -> dict:
        return {
            ch: [m.to_dict() for m in msgs[-100:]]
            for ch, msgs in self._channels.items()
        }
