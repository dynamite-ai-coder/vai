import time
from typing import List, Dict
from config import MAX_HISTORY_MESSAGES


class ConversationMemory:
    def __init__(self, max_messages: int = MAX_HISTORY_MESSAGES):
        self.max_messages = max_messages
        self.history: List[Dict[str, str]] = []
        self.timestamps: List[float] = []

    def add_user_message(self, content: str):
        self.history.append({"role": "user", "content": content})
        self.timestamps.append(time.time())
        self._trim()

    def add_assistant_message(self, content: str):
        self.history.append({"role": "assistant", "content": content})
        self.timestamps.append(time.time())
        self._trim()

    def get_messages(self, limit: int = None) -> List[Dict[str, str]]:
        if limit:
            return list(self.history[-limit:])
        return list(self.history)

    def get_context_string(self, limit: int = 20) -> str:
        msgs = self.get_messages(limit)
        lines = []
        for m in msgs:
            role = "User" if m["role"] == "user" else "Assistant"
            lines.append(f"{role}: {m['content']}")
        return "\n".join(lines)

    def clear(self):
        self.history.clear()
        self.timestamps.clear()

    def _trim(self):
        while len(self.history) > self.max_messages:
            self.history.pop(0)
            self.timestamps.pop(0)

    @property
    def message_count(self) -> int:
        return len(self.history)
