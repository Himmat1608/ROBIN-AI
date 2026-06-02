# save as test_listen.py
from voice.listener import listen
import time

print("Say something now...")
for i in range(3):
    result = listen(timeout=4, phrase_time_limit=6)
    print(f"Attempt {i+1}: {result!r}")
    time.sleep(0.5)