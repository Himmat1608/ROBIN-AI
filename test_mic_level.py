# test_mic_level.py
import speech_recognition as sr

r = sr.Recognizer()
r.dynamic_energy_threshold = True

mic = sr.Microphone()

print("Calibrating for 3 seconds... stay quiet")
with mic as source:
    r.adjust_for_ambient_noise(source, duration=3)

print(f"Your current ambient threshold: {r.energy_threshold:.0f}")
print("Now speak normally...")

with mic as source:
    try:
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
        text = r.recognize_google(audio)
        print(f"Heard: {text}")
    except sr.WaitTimeoutError:
        print("Timeout — mic not picking up voice")
    except sr.UnknownValueError:
        print("Heard audio but couldn't recognize speech")