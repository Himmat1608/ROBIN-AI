# test_exploration.py
from core.reasoning_engine import ReasoningPipeline
from memory.conversation_memory import ConversationMemory
from core.context_manager import ContextManager

memory = ConversationMemory()
context = ContextManager()
pipeline = ReasoningPipeline(memory, context)

intent_data = {"intent": "CONVERSATION", "confidence": 0.6}

tests = [
    # Exploration — should allow deeper responses
    "what if black holes are gateways",
    "let's build a time machine",
    "imagine humans could live forever",
    "do you think AI will become conscious",
    "suppose gravity worked in reverse",

    # Normal conversation — should stay short
    "i'm tired",
    "i'm bored",
    "good night",

    # Factual — should stay concise
    "what is a black hole",
    "how does gravity work",
]

print("=== Exploration Mode Test ===\n")
for prompt in tests:
    response = pipeline.get_reasoned_response(prompt, intent_data)
    word_count = len(response.split())
    mode = "EXPLORATION" if any(p in prompt for p in [
        "what if", "imagine", "let's", "do you think",
        "suppose", "could", "how would"
    ]) else "NORMAL"
    print(f"[{mode}] Input: {prompt!r}")
    print(f"Response ({word_count} words): {response!r}")
    print()