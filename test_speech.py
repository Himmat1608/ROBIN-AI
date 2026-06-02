# save as test_speech.py
from voice.speech_manager import speak, speech_manager
import time

print("=== Speech Test ===")
speak("Opening Chrome.")
time.sleep(6)
speak("It's eight fifty eight PM.")
time.sleep(6)
speak("A black hole is a region where gravity is so strong that nothing can escape.")
time.sleep(12)
print("=== Done ===")