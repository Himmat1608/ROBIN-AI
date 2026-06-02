import sys
sys.path.insert(0, '.')
from core.intent_engine import IntentEngine

engine = IntentEngine()

test_cases = [
    "who am i to you",
    "what do you think",
    "volume up",
    "open chrome",
    "play music",
    "hey robin",
    "hey robin how are you",
    "what is the time"
]

print("=== Intent Classification Verification ===\n")
for text in test_cases:
    result = engine.analyze_intent(text)
    print(f"Input: {text!r}")
    print(f"Intent: {result['intent']}")
    print(f"Confidence: {result['confidence']}")
    print("-" * 30)
