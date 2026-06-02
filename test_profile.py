from core.assistant import RobinAssistant
import os

# Clean up existing profile for a fresh test
profile_path = "memory/user_profile.json"
if os.path.exists(profile_path):
    os.remove(profile_path)

a = RobinAssistant()

tests = [
    "my name is Himmat Singh",
    "what's my name",
    "call me boss",
    "i like RnB music",
    "what music do i like",
    "what browser do i use",
]

print("=== ROBIN IDENTITY TEST ===\n")

for t in tests:
    print(f"Input: {t!r}")
    result = a.process_input(t)
    # Note: result might be "IGNORE" or similar depending on handle_response
    # But process_input returns the string from handle_response
    print(f"Result: {result!r}")
    print("-" * 30)

# Simulate music play history for retrieval test
from memory.user_profile import user_profile
user_profile.set("play_history", ["Chicago", "Ghazals", "Poison"])
print("\nInput: 'what kind of music do i like'")
result = a.process_input("what kind of music do i like")
print(f"Result: {result!r}")
