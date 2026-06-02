import sys
sys.path.insert(0, '.')
from core.assistant import RobinAssistant
import logging

# Setup logging to see [Routing] tags
logging.basicConfig(level=logging.INFO)

assistant = RobinAssistant()

test_cases = [
    "hey robin",
    "who am i to you",
    "volume up",
    "what is the time"
]

print("=== Assistant Routing Verification ===\n")
for text in test_cases:
    print(f"\n>>> Input: {text!r}")
    # We mock handle_response to not actually speak
    response = assistant.process_input(text)
    print(f"Response: {response!r}")
