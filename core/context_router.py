import re
from core.assistant_state import state
from core.assistant_state_engine import state_engine, AssistantState

class ContextRouter:
    """
    Analyzes input in the context of the current state and recent history.
    """
    
    FOLLOW_UP_PATTERNS = {
        r"\bpause it\b": "pause_media",
        r"\bresume it\b": "resume_media",
        r"\bplay it again\b": "play_last_song",
        r"\bclose it\b": "close_last_app",
        r"\bopen it again\b": "open_last_app",
        r"\bstop it\b": "stop_media",
        r"\bcontinue\b": "resume_media"
    }

    def resolve(self, cleaned_input: str) -> dict:
        """
        Attempts to resolve contextual references.
        """
        # 1. Check for explicit follow-up patterns
        for pattern, action in self.FOLLOW_UP_PATTERNS.items():
            if re.search(pattern, cleaned_input):
                return self._map_to_command(action)
        
        # 2. State-aware implicit resolution
        if state_engine.current_state == AssistantState.MEDIA:
            if cleaned_input in ["pause", "stop"]:
                return self._map_to_command("pause_media")
            if cleaned_input in ["next", "skip"]:
                return {"type": "COMMAND", "action": "media_os_control", "args": "next"}

        return None

    def _map_to_command(self, action: str) -> dict:
        if action in ["pause_media", "stop_media"]:
            return {
                "type": "COMMAND",
                "action": "media_control",
                "args": {"command": "pause", "platform": state.last_media_platform}
            }
        elif action == "resume_media":
            return {
                "type": "COMMAND",
                "action": "media_control",
                "args": {"command": "resume", "platform": state.last_media_platform}
            }
        elif action == "close_last_app":
            if state.last_app_opened:
                return {"type": "COMMAND", "action": "close_app", "args": state.last_app_opened}
        elif action == "open_last_app":
            if state.last_app_opened:
                return {"type": "COMMAND", "action": "open_app", "args": state.last_app_opened}
        
        return None

# Singleton instance
context_router = ContextRouter()
