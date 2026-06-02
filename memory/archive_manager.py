import os
import json
import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

# Resolve memory/conversations/ path relative to this file
ARCHIVE_DIR = os.path.join(os.path.dirname(__file__), "conversations")

def archive_interaction(user_input: str, response: str):
    """Passively archives a single conversation interaction to date-based JSON files."""
    if not user_input or not response:
        return
    
    user_clean = user_input.strip()
    resp_clean = response.strip()
    
    if not user_clean or not resp_clean or resp_clean == "IGNORE":
        return

    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    today_str = datetime.date.today().isoformat()
    file_path = os.path.join(ARCHIVE_DIR, f"{today_str}.json")
    
    data = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    data = json.loads(content)
        except Exception as e:
            logger.warning(f"Failed to load archive file {file_path}: {e}")
            data = []

    # Check for consecutive duplicate interaction
    if data:
        last_entry = data[-1]
        if last_entry.get("user") == user_clean and last_entry.get("response") == resp_clean:
            return

    # Create new interaction entry
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "user": user_clean,
        "response": resp_clean
    }
    data.append(entry)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info("[Archive] Session updated")
        logger.info("[Archive] Conversation stored")
    except Exception as e:
        logger.error(f"Failed to write to archive file {file_path}: {e}")
