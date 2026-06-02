from collections import deque

class ConversationMemory:
    """Manages short-term conversation history for context injection."""
    def __init__(self, max_exchanges: int = 5):
        self._history = deque(maxlen=max_exchanges)

    def add_interaction(self, user_input: str, response: str):
        self._history.append({"user": user_input, "robin": response})

    def get_context(self) -> str:
        if not self._history:
            return ""
        lines = []
        for exchange in self._history:
            lines.append(f"User: {exchange['user']}")
            lines.append(f"ROBIN: {exchange['robin']}")
        return "\n".join(lines)

    def clear(self):
        self._history.clear()
        
    def set_pending_context(self, key: str, value: str):
        """Store a pending conversation context."""
        self._pending = getattr(self, '_pending', {})
        self._pending[key] = value

def get_pending_context(self, key: str):
    """Retrieve and clear pending context."""
    self._pending = getattr(self, '_pending', {})
    return self._pending.pop(key, None)

