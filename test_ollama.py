import requests
payload = {
    'model': 'qwen2.5:3b',
    'prompt': 'what is gravity',
    'stream': False
}
r = requests.post('http://localhost:11434/api/generate', json=payload, timeout=30)
print('Status:', r.status_code)
print('Response:', r.text[:200])
