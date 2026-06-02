# test_ollama3.py
import requests
import sys
sys.path.insert(0, '.')
from config import Config

# Simulate what brain.py does
prompt = "what is gravity"
context = ""
system_prompt = "You are ROBIN, a calm assistant."

full_prompt = f"{system_prompt}\n\nUser: {prompt}\nROBIN:"

print("Model:", Config.AI_MODEL_NAME)
print("URL:", Config.OLLAMA_API_URL)
print("Prompt length:", len(full_prompt))

payload = {
    "model": Config.AI_MODEL_NAME,
    "prompt": full_prompt,
    "stream": False,
    "options": {
        "num_ctx": 512,
        "num_predict": 100,
        "temperature": 0.7
    }
}

r = requests.post(
    Config.OLLAMA_API_URL,
    json=payload,
    timeout=30
)
print("Status:", r.status_code)
if r.status_code == 200:
    print("Response:", r.json().get('response', '')[:200])
else:
    print("Error:", r.text[:200])