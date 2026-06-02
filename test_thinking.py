# test_thinking.py
from core.brain import get_ai_response
import time

explorations = [
    "let's make a time machine",
    "could humans become immortal",
    "what if black holes are gateways",
    "how would we colonize mars",
    "what if we could talk to animals",
    "suppose gravity worked in reverse",
    "imagine if sleep wasn't necessary",
]

casuals = [
    "i'm tired",
    "i'm bored",
    "long day",
]

factuals = [
    "what is a black hole",
    "how does gravity work",
    "what is quantum physics",
]

print("=== EXPLORATION ===\n")
for p in explorations:
    r = get_ai_response(p)
    print(f"Q: {p}")
    print(f"A: {r}")
    print(f"Words: {len(r.split())}")
    print()

print("=== CASUAL ===\n")
for p in casuals:
    r = get_ai_response(p)
    print(f"Q: {p}")
    print(f"A: {r}")
    print()

print("=== FACTUAL ===\n")
for p in factuals:
    r = get_ai_response(p)
    print(f"Q: {p}")
    print(f"A: {r}")
    print()