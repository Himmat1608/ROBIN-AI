# test_direct.py
import sys
sys.path.insert(0, '.')
from voice.listener import _is_direct_command
tests = [
    "what is black hole",
    "raise the volume",
    "volume down to 50",
    "i am bored",
    "what are black holes",
]
for t in tests:
    print(f"{t!r} → {_is_direct_command(t)}")
