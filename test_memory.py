# test_memory.py
from memory.conversation_memory import ConversationMemory

m = ConversationMemory()

# Test 1 — add and retrieve
m.add_interaction("what is black hole", "A region where gravity traps light.")
m.add_interaction("i'm tired", "Long day?")
m.add_interaction("open chrome", "Opening Chrome.")

context = m.get_context()
print("=== Context Output ===")
print(context)
print()

# Test 2 — max 5 exchanges
m.add_interaction("play music", "Playing.")
m.add_interaction("volume down", "Lowering volume.")
m.add_interaction("sixth message", "sixth reply")

context2 = m.get_context()
lines = context2.strip().split("\n")
exchange_count = len([l for l in lines if l.startswith("User:")])
print(f"Exchange count (should be 5 max): {exchange_count}")
print()

# Test 3 — empty memory
m2 = ConversationMemory()
print(f"Empty context (should be empty string): {m2.get_context()!r}")