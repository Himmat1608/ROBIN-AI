from core.context_router import context_router, ContextRouter
from core.assistant_state import state


class ContextManager(ContextRouter):

    def get_context_summary(self) -> str:
        parts = []
        if state.active_workflow:
            parts.append(f"Current mode: {state.active_workflow}")
        return " | ".join(parts) if parts else ""

    def extract_preferences(self, user_input: str):
        pass


context_mgr = context_router