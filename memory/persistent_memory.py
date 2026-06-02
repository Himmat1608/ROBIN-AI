import json
import os
from utils.logger import get_logger

logger = get_logger(__name__)

PREFS_FILE = os.path.join(
    os.path.dirname(__file__),
    "preferences.json"
)

DEFAULTS = {
    "music_platform": "spotify",
    "browser": "chrome"
}

class PersistentMemory:
    def __init__(self):
        self._data = self._load()

    def _load(self) -> dict:
        if not os.path.exists(PREFS_FILE):
            self._write(DEFAULTS)
            return dict(DEFAULTS)

        try:
            with open(PREFS_FILE, "r") as f:
                return json.load(f)

        except Exception:
            logger.warning(
                "Preferences file corrupted. Resetting."
            )
            self._write(DEFAULTS)
            return dict(DEFAULTS)

    def _write(self, data: dict):
        os.makedirs(os.path.dirname(PREFS_FILE), exist_ok=True)

        with open(PREFS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def get_preference(self, key: str, default=None):
        return self._data.get(key, default)

    def set_preference(self, key: str, value):
        self._data[key] = value
        self._write(self._data)

    def get_all(self) -> dict:
        return dict(self._data)
