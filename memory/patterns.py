import os
import json
import datetime
import random
from utils.logger import get_logger

logger = get_logger(__name__)

HABITS_FILE = os.path.join(os.path.dirname(__file__), "habits.json")
CONVERSATIONS_DIR = os.path.join(os.path.dirname(__file__), "conversations")

CODING_KEYWORDS = ["code", "coding", "vscode", "vs code", "programming", "python", "develop", "website", "project"]
AI_KEYWORDS = ["ai", "artificial intelligence", "time machine", "model", "llm", "neural", "deep learning", "machine learning", "openai", "ollama"]
MUSIC_KEYWORDS = ["play", "music", "spotify", "song"]

def detect_patterns(play_history):
    """
    Scans the conversation archive and play history to detect behavioral patterns.
    Saves results to memory/habits.json.
    """
    coding_count = 0
    ai_count = 0
    music_count = 0
    late_night_count = 0

    # 1. Scan conversation archive
    if os.path.exists(CONVERSATIONS_DIR):
        try:
            for filename in os.listdir(CONVERSATIONS_DIR):
                if filename.endswith(".json"):
                    file_path = os.path.join(CONVERSATIONS_DIR, filename)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            exchanges = json.loads(content)
                            for exchange in exchanges:
                                user_msg = exchange.get("user", "").lower()
                                timestamp_str = exchange.get("timestamp", "")
                                
                                # Check coding
                                if any(kw in user_msg for kw in CODING_KEYWORDS):
                                    coding_count += 1
                                
                                # Check AI
                                if any(kw in user_msg for kw in AI_KEYWORDS):
                                    ai_count += 1
                                    
                                # Check music
                                if any(kw in user_msg for kw in MUSIC_KEYWORDS):
                                    music_count += 1
                                    
                                # Check late night (9 PM to 5 AM)
                                if timestamp_str and "T" in timestamp_str:
                                    try:
                                        time_part = timestamp_str.split("T")[1]
                                        hour = int(time_part.split(":")[0])
                                        if hour >= 21 or hour < 5:
                                            late_night_count += 1
                                    except Exception:
                                        pass
        except Exception as e:
            logger.warning(f"Error scanning conversation archive: {e}")

    # 2. Check play history from user profile
    if play_history:
        # Avoid double counting if already counted via keywords
        # But play_history contains explicit songs, so let's add them
        music_count += len(play_history)

    # 3. Read current habits from habits.json
    old_habits = {}
    if os.path.exists(HABITS_FILE):
        try:
            with open(HABITS_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    old_habits = json.loads(content)
        except Exception:
            pass

    new_habits = {
        "coding_sessions": coding_count,
        "music_plays": music_count,
        "ai_projects": ai_count,
        "late_night_sessions": late_night_count,
        "last_updated": datetime.datetime.now().isoformat()
    }

    # If habits changed, write to habits.json and log
    changed = False
    for k in ["coding_sessions", "music_plays", "ai_projects", "late_night_sessions"]:
        if old_habits.get(k) != new_habits[k]:
            changed = True
            break

    if changed or not old_habits:
        try:
            with open(HABITS_FILE, "w", encoding="utf-8") as f:
                json.dump(new_habits, f, indent=2, ensure_ascii=False)
            logger.info("[Adaptation] Behavioral memory updated")
        except Exception as e:
            logger.error(f"Failed to write to {HABITS_FILE}: {e}")

    # Identify active patterns (threshold >= 3)
    active_patterns = {
        "coding": coding_count >= 3,
        "ai_projects": ai_count >= 3,
        "music": music_count >= 3,
        "late_night": late_night_count >= 3
    }
    
    return active_patterns
