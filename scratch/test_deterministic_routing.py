import sys
sys.path.insert(0, '.')
from core.assistant import RobinAssistant
import logging

logging.basicConfig(level=logging.INFO)

assistant = RobinAssistant()

test_cases = [
    "hey robin",
    "what's my name",
    "my name is captain",
    "what is my name",
    "volume up",
    "who am i to you",
]

print("=== Deterministic Routing Final Verification ===\n")
for text in test_cases:
    print(f"\n>>> Input: {text!r}")
    response = assistant.process_input(text)
    print(f"Response: {response!r}")
