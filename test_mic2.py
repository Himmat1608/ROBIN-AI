# test_mic2.py
import speech_recognition as sr

r = sr.Recognizer()
r.dynamic_energy_threshold = False
r.energy_threshold = 50  # Very low — catches everything
r.pause_threshold = 1.0

mic = sr.Microphone()

print("Speak anything for 10 seconds...")
print("We'll measure your voice level\n")

with mic as source:
    print("Recording... speak now")
    audio = r.listen(source, timeout=10, phrase_time_limit=8)
    print("Got audio")
    
    try:
        text = r.recognize_google(audio)
        print(f"Heard: {text!r}")
        print("\nYour mic works at threshold 50")
        print("Recommended threshold: 80")
    except sr.UnknownValueError:
        print("Audio captured but unclear")
    except Exception as e:
        print(f"Error: {e}")