# test_pipeline.py
from core.assistant import RobinAssistant
a = RobinAssistant()

tests = [
    "what is black hole",
    "raise the volume",
    "volume down to 50",
    "i am bored",
]

for t in tests:
    print(f"\nInput: {t!r}")
    result = a.process_input(t)
    print(f"Result: {result!r}")

    