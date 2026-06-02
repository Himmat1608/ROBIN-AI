import json
import os
from utils.logger import get_logger

logger = get_logger(__name__)

PROFILE_FILE = os.path.join(
    os.path.dirname(__file__),
    "user_profile.json"
)

DEFAULT_PROFILE = {
    "name": None,
    "nickname": "Sanji",
    "assistant_titles": ["boss", "sir", "captain"],
    "favorite_music": None,
    "preferred_browser": "chrome",
    "interests": [],
    "play_history": []
}

class UserProfile:
    def __init__(self):
        self.profile = self._load()

    def _load(self):
        if not os.path.exists(PROFILE_FILE):
            return dict(DEFAULT_PROFILE)
        try:
            with open(PROFILE_FILE, 'r') as f:
                data = json.load(f)
                # Ensure all default keys exist
                for key in DEFAULT_PROFILE:
                    if key not in data:
                        data[key] = DEFAULT_PROFILE[key]
                return data
        except (json.JSONDecodeError, Exception) as e:
            logger.error(f"Error loading profile: {e}")
            return dict(DEFAULT_PROFILE)

    def _save(self):
        try:
            with open(PROFILE_FILE, 'w') as f:
                json.dump(self.profile, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving profile: {e}")

    def get(self, key):
        return self.profile.get(key)

    def set(self, key, value):
        if key not in self.profile:
            return False

        # Validation logic for strings
        if isinstance(value, str):
            value = value.strip().rstrip('?!.')
            if len(value) > 40:
                return False
            if key == "name":
                value = value.title()

        #list Handling
        if isinstance(self.profile[key], list):
            if isinstance(value, list):
                # Replace list (for bulk updates/init)
                self.profile[key] = value
            else:
                # Append single item
                if value not in self.profile[key]:
                    self.profile[key].append(value)
            
            # Caps
            if key == "interests":
                self.profile[key] = self.profile[key][-10:]
            elif key == "play_history":
                self.profile[key] = self.profile[key][-20:]
        else:
            self.profile[key] = value

        self._save()
        return True

    def get_all(self):
        return dict(self.profile)

    def has(self, key):
        return self.profile.get(key) is not None

    def get_habits(self):
        """Returns the behavioral habits data from habits.json."""
        habits_file = os.path.join(os.path.dirname(__file__), "habits.json")
        if os.path.exists(habits_file):
            try:
                with open(habits_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

user_profile = UserProfile()
