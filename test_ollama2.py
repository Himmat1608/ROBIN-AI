# test_ollama2.py
import requests

payload = {
    "model": "qwen2.5:3b",
    "prompt": "what is gravity",
    "stream": False,
    "options": {
        "num_ctx": 512,
        "num_predict": 100,
        "temperature": 0.7
    }
}

r = requests.post(
    "http://localhost:11434/api/generate",
    json=payload,
    timeout=30
)
print("Status:", r.status_code)
print("Response:", r.json().get('response', '')[:200])