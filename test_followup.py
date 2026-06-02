# test_followup.py
from voice.listener import listen
import time

print("Say 'then what' or 'why' after the prompt...")
for i in range(5):
    print(f"Listening attempt {i+1}...")
    result = listen(timeout=4, phrase_time_limit=6)
    print(f"Result: {result!r}")
    time.sleep(0.5)