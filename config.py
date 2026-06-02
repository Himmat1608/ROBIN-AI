import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OLLAMA_API_URL = "http://localhost:11434/api/generate"
    AI_MODEL_NAME = "qwen2.5:3b"
    AI_TRIGGERS = ["robin", "ai", "hey robin", "robin,"]
    EDGE_TTS_VOICE = "en-US-JennyNeural"