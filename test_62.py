# test_62.py
from core.assistant import RobinAssistant
a = RobinAssistant()

tests = [
    # Should sound natural, not academic
    "what is a black hole",
    "how does gravity work",

    # Should be concise, not corporate
    "i'm tired",
    "long day",

    # Should engage practically, not lecture
    "let's build a time machine",
    "what if we could live forever",

    # Should be short acknowledgements
    "hey",
    "thanks",
    "good night",

    # Should not say "certainly" or "as an AI"
    "what do you think about mars",
    "do you think AI will take over",
]

print("=== Phase 6.2 Response Quality Test ===\n")
for t in tests:
    result = a.process_input(t)
    words = len(result.split())
    bad = any(p in result.lower() for p in [
        "certainly", "as an ai", "fascinating",
        "how may i assist", "understood?",
        "practical efficient"
    ])
    flag = "BAD PHRASE DETECTED" if bad else ""
    print(f"Input: {t!r}")
    print(f"Response ({words}w): {result!r} {flag}")
    print()