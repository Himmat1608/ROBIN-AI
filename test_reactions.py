# test_reactions.py
from core.assistant import RobinAssistant
import time

a = RobinAssistant()

print("=== Wake Word Reaction Variety Test ===")
print("Running 10 times to check variety:\n")

reactions_seen = set()
for i in range(10):
    result = a.process_input("hey")
    reactions_seen.add(result)
    print(f"Attempt {i+1}: {result!r}")
    time.sleep(4)  # Wait for speech to finish

print(f"\nUnique reactions seen: {len(reactions_seen)}")
print(f"Should be more than 1: {'✓' if len(reactions_seen) > 1 else '✗'}")
print(f"All reactions: {reactions_seen}")