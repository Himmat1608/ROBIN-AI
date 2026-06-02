# test_brain.py
from core.brain import get_ai_response

tests = [
    # Factual — should be clear and informative
    ("what is a black hole", ""),
    ("how does gravity work", ""),
    ("what is quantum physics", ""),

    # Conversational — should be casual and short
    ("i'm tired", ""),
    ("i'm bored", ""),
    ("long day", ""),

    # Follow-up with context
    ("what about tomorrow", "User: cheapest flight to bangalore\nROBIN: Around 4-6k."),
    ("why", "User: i'm tired\nROBIN: Long day?"),
]

print("=== Brain Response Tests ===\n")
for prompt, context in tests:
    response = get_ai_response(prompt, context)
    word_count = len(response.split())
    print(f"Input: {prompt!r}")
    print(f"Response: {response!r}")
    print(f"Words: {word_count} (should be under 30)")
    print()