import threading
from utils.logger import get_logger

logger = get_logger(__name__)

class AssistantState:
    COMMAND = "COMMAND"
    CONVERSATION = "CONVERSATION"
    FOCUS = "FOCUS"
    CODING = "CODING"
    MEDIA = "MEDIA"

class AssistantStateEngine:
    """
    Central engine to manage assistant states and behavioral flags.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AssistantStateEngine, cls).__new__(cls)
            cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        self._current_state = AssistantState.COMMAND
        self._lock = threading.Lock()
        self.state_history = []
        
        # State-specific behaviors
        self.behaviors = {
            AssistantState.COMMAND: {"concise": True, "ambient": False, "interruptible": True},
            AssistantState.CONVERSATION: {"concise": False, "ambient": True, "interruptible": True},
            AssistantState.FOCUS: {"concise": True, "ambient": False, "interruptible": False},
            AssistantState.CODING: {"concise": True, "ambient": True, "interruptible": True},
            AssistantState.MEDIA: {"concise": True, "ambient": True, "interruptible": True}
        }

    @property
    def current_state(self):
        with self._lock:
            return self._current_state

    def transition_to(self, new_state: str):
        """Switches the assistant to a new state."""
        if new_state not in [AssistantState.COMMAND, AssistantState.CONVERSATION, 
                             AssistantState.FOCUS, AssistantState.CODING, AssistantState.MEDIA]:
            logger.warning(f"Invalid state transition attempted: {new_state}")
            return

        with self._lock:
            if self._current_state != new_state:
                import datetime
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                logger.info(f"[{timestamp}] STATE_TRANSITION: {self._current_state} -> {new_state}")
                self.state_history.append((timestamp, self._current_state))
                self._current_state = new_state
                
                # Limit history size
                if len(self.state_history) > 20:
                    self.state_history.pop(0)

    def get_behavior_flag(self, flag: str):
        """Returns a behavioral flag for the current state."""
        return self.behaviors.get(self.current_state, {}).get(flag, False)

    def is_in_mode(self, state_name: str) -> bool:
        return self.current_state == state_name

# Singleton instance
state_engine = AssistantStateEngine()
