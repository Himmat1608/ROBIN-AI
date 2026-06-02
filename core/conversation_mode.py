from core.assistant_state_engine import state_engine, AssistantState
from utils.logger import get_logger

logger = get_logger(__name__)

class ConversationMode:
    """
    Handles natural discussion, conceptual explanations, and assistant personality.
    """
    
CONCEPTUAL_TRIGGERS = [
    "explain", "how does", "what is", "tell me about", "discuss",
    "black hole", "recursion", "quantum", "philosophy", "science",
    "thinking about", "i've been", "have you read", "have you seen",
    "what do you think", "opinion on", "thoughts on", "heard about",
    "just read", "just watched", "book", "movie", "film", "show",
    "recommend", "should i", "worth reading", "worth watching",
    "advice", "help me understand", "curious about", "wondering",
    "i'm feeling", "do you think", "is it worth", "any thoughts",
    "i'm thinking", "i feel", "i want to",
    "i was wondering", "have you heard",
    "what would", "i just", "honestly", "between us",
    "i'm bored", "i'm tired", "long day", "do you like", "have you ever", "what's your"
]

class ConversationMode:
    """
    Handles natural discussion, conceptual explanations, and assistant personality.
    """
    
    def should_handle(self, user_input: str) -> bool:
        cleaned = user_input.lower()

        if any(phrase in cleaned for phrase in [
            "let's talk",
            "talk to me",
            "chat with me",
            "i'm thinking",
            "i've been thinking",
            "can we talk"
        ]):
            state_engine.transition_to(
                AssistantState.CONVERSATION
            )
            return True

        if any(
            trigger in cleaned
            for trigger in CONCEPTUAL_TRIGGERS
        ):
            state_engine.transition_to(
                AssistantState.CONVERSATION
            )
            return True

        return False

    def get_personality_prompt(self) -> str:
        """Returns a system prompt tweak for conversational depth."""
        return (
            "You are ROBIN. Be calm, observant, and naturally intelligent. "
            "Speak briefly and practically. Avoid lecturing or robot-like transitions. "
            "If discussing complex ideas, stay grounded and concise. "
            "Be conversationally present but never over-explain. No chatbot filler."
        )

# Singleton instance
conversation_mode = ConversationMode()
