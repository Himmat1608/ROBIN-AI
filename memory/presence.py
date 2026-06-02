import os
import json
import random
import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

PRESENCE_FILE = os.path.join(os.path.dirname(__file__), "presence.json")

DEFAULT_PRESENCE = {
    "last_session": "2026-05-18T23:45:00",
    "last_date": "2026-05-18",
    "session_count_today": 0,
    "last_greeting": None,
    "last_presence_type": None,
    "last_topic": None,
    "last_active_period": None,
    "idle_ack_count": 0
}

class PresenceEngine:
    def __init__(self, silence_bias=True):
        self.silence_bias = silence_bias
        self.data = self._load()

    def _load(self):
        if not os.path.exists(PRESENCE_FILE):
            logger.info("[Presence] File missing. Initializing default presence.")
            data = dict(DEFAULT_PRESENCE)
            self._save_data(data)
            return data
        try:
            with open(PRESENCE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Auto-repair logic
            repaired = False
            for k, v in DEFAULT_PRESENCE.items():
                if k not in data:
                    data[k] = v
                    repaired = True
                elif v is not None and not isinstance(data[k], type(v)):
                    data[k] = v
                    repaired = True
                    
            if repaired:
                logger.info("[Presence] Repaired presence data keys/types.")
                self._save_data(data)
            return data
        except Exception as e:
            logger.warning(f"[Presence] Corruption detected or load failed: {e}. Re-initializing.")
            try:
                self._save_data(DEFAULT_PRESENCE)
            except Exception:
                pass
            return dict(DEFAULT_PRESENCE)

    def _save(self):
        self._save_data(self.data)

    def _save_data(self, data):
        try:
            with open(PRESENCE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[Presence] Failed to save presence: {e}")

    def get_session_context(self) -> dict:
        now = datetime.datetime.now()
        hour = now.hour
        
        # Morning (6am–11am)
        # Afternoon (11am–5pm)
        # Evening (5pm–10pm)
        # Night (10pm–12am)
        # Late night (12am–5am)
        if 6 <= hour < 11:
            time_of_day = "morning"
        elif 11 <= hour < 17:
            time_of_day = "afternoon"
        elif 17 <= hour < 22:
            time_of_day = "evening"
        elif 22 <= hour < 24:
            time_of_day = "night"
        else:
            time_of_day = "late_night"
            
        days_since_last = 0
        minutes_since_last = 0
        last_session_str = self.data.get("last_session")
        if last_session_str:
            try:
                last_session_dt = datetime.datetime.fromisoformat(last_session_str)
                delta = now - last_session_dt
                days_since_last = delta.days
                minutes_since_last = int(delta.total_seconds() / 60)
            except Exception:
                pass
                
        current_date_str = now.date().isoformat()
        last_date_str = self.data.get("last_date")
        is_first_session_today = (current_date_str != last_date_str)
        
        if is_first_session_today:
            session_count_today = 1
        else:
            session_count_today = self.data.get("session_count_today", 0) + 1

        last_topic, last_command = self._detect_last_topic_and_command()
        
        likely_project_session = False
        from memory.user_profile import user_profile
        habits = user_profile.get_habits()
        coding_sessions = habits.get("coding_sessions", 0)
        ai_projects = habits.get("ai_projects", 0)
        
        if coding_sessions >= 3 or ai_projects >= 3 or last_topic in ["coding", "ai"]:
            likely_project_session = True
            
        late_night_session = (time_of_day == "late_night")
        
        context = {
            "time_of_day": time_of_day,
            "hour": hour,
            "days_since_last": days_since_last,
            "minutes_since_last": minutes_since_last,
            "is_first_session_today": is_first_session_today,
            "session_count_today": session_count_today,
            "last_topic": last_topic,
            "last_command": last_command,
            "likely_project_session": likely_project_session,
            "late_night_session": late_night_session
        }
        return context

    def _detect_last_topic_and_command(self) -> tuple:
        topic = self.data.get("last_topic")
        command = None
        
        try:
            conv_dir = os.path.join(os.path.dirname(__file__), "conversations")
            if os.path.isdir(conv_dir):
                files = sorted([f for f in os.listdir(conv_dir) if f.endswith(".json")])
                if files:
                    latest_file = os.path.join(conv_dir, files[-1])
                    with open(latest_file, "r", encoding="utf-8") as f:
                        interactions = json.load(f)
                    if interactions:
                        last_interaction = interactions[-1]
                        command = last_interaction.get("user", "")
                        last_user_input = command.lower()
                        
                        coding_kws = ["code", "coding", "vscode", "vs code", "programming", "python", "develop", "website", "project", "ui", "build"]
                        ai_kws = ["ai", "artificial intelligence", "time machine", "model", "llm", "neural", "deep learning", "machine learning", "openai", "ollama", "phi3"]
                        music_kws = ["play", "music", "spotify", "song", "volume"]
                        
                        if any(kw in last_user_input for kw in ai_kws):
                            topic = "ai"
                        elif any(kw in last_user_input for kw in coding_kws):
                            topic = "coding"
                        elif any(kw in last_user_input for kw in music_kws):
                            topic = "music"
        except Exception as e:
            logger.debug(f"[Presence] Quietly ignored error detecting last topic: {e}")
            
        return topic, command

    def mark_session_start(self, context: dict):
        self.data["last_session"] = datetime.datetime.now().isoformat()
        self.data["last_date"] = datetime.date.today().isoformat()
        self.data["session_count_today"] = context["session_count_today"]
        self.data["last_active_period"] = context["time_of_day"]
        if context.get("last_topic"):
            self.data["last_topic"] = context["last_topic"]
        self._save()

    def get_presence_greeting(self, context: dict, bypass_silence=False) -> str | None:
        if not bypass_silence and self.silence_bias:
            silence_prob = random.uniform(0.60, 0.75)
            if random.random() < silence_prob:
                logger.info("[Presence] Silence maintained")
                return None

        last_g = self.data.get("last_greeting")
        candidates = []

        # Gap Awareness
        days = context["days_since_last"]
        if days == 1 and random.random() < 0.4:
            candidates.append("Back again.")
        elif 3 <= days < 7 and random.random() < 0.5:
            candidates.append("Been a while.")
        elif days >= 7 and random.random() < 0.6:
            candidates.append("It's been a minute.")

        # Project Session Awareness
        if context["likely_project_session"] and random.random() < 0.3:
            topic = context["last_topic"]
            if topic == "coding":
                if context["late_night_session"]:
                    candidates.extend(["Another late build session?", "Still working on it?"])
                else:
                    candidates.extend(["Back to the project?", "Another build session?", "Still refining it?"])
            elif topic == "ai":
                candidates.extend(["Still working on that UI system?", "Another AI project session?"])
            elif topic == "music":
                candidates.append("Another music night?")

        # Time of day greetings
        time_of_day = context["time_of_day"]
        if time_of_day == "morning":
            candidates.extend(["Morning.", "Morning, boss.", "Early start."])
        elif time_of_day == "afternoon":
            candidates.append("Afternoon.")
        elif time_of_day == "evening":
            candidates.append("Evening.")
        elif time_of_day == "night":
            candidates.extend(["Still up?", "Late one."])
        elif time_of_day == "late_night":
            candidates.extend(["Still at it?", "Late night, boss."])

        candidates = [c for c in candidates if c and c != last_g]

        if not candidates:
            logger.info("[Presence] Silence maintained")
            return None

        greeting = random.choice(candidates)
        self.data["last_greeting"] = greeting
        self.data["last_presence_type"] = "session_greeting"
        self._save()
        
        logger.info("[Presence] Session greeting")
        return greeting

    def get_idle_presence(self, minutes_idle: int) -> str | None:
        if minutes_idle < 45:
            return None

        if self.silence_bias and random.random() > 0.20:
            logger.info("[Presence] Silence maintained")
            return None

        candidates = []
        if 45 <= minutes_idle < 120:
            candidates = ["Back to it?", "Need anything?"]
        else:
            candidates = ["Still there?", "Welcome back."]

        greeting = random.choice(candidates)
        if greeting == self.data.get("last_greeting"):
            remaining = [c for c in candidates if c != greeting]
            if remaining:
                greeting = random.choice(remaining)
            else:
                logger.info("[Presence] Silence maintained")
                return None

        self.data["last_greeting"] = greeting
        self.data["last_presence_type"] = "idle_presence"
        self.data["idle_ack_count"] = self.data.get("idle_ack_count", 0) + 1
        self._save()

        logger.info("[Presence] Idle awareness triggered")
        return greeting

    def get_contextual_reaction(self, user_input: str) -> str | None:
        cleaned = user_input.lower().strip().replace("'", "").replace("!", "").replace("?", "")
        
        is_transition = cleaned in ["lets continue", "lets keep going", "continue", "resume"]
        
        if not is_transition and self.silence_bias and random.random() > 0.4:
            logger.info("[Presence] Presence suppressed")
            return None

        if cleaned in ["im home", "i am home", "just got home"]:
            logger.info("[Presence] Contextual presence active")
            return "Welcome home, boss."
        elif cleaned in ["lets continue", "lets keep going", "continue", "resume"]:
            logger.info("[Presence] Contextual presence active")
            return "Alright, boss."
        elif cleaned in ["long day", "tough day", "exhausting day"]:
            logger.info("[Presence] Contextual presence active")
            return "Yeah... sounds like it."
        elif cleaned in ["that was exhausting", "im exhausted", "im so tired"]:
            logger.info("[Presence] Contextual presence active")
            return "Long day?"
            
        return None


CONTINUITY_FILE = os.path.join(os.path.dirname(__file__), "continuity.json")

DEFAULT_CONTINUITY = {
    "active_atmosphere": "calm presence",
    "recent_conversational_mode": "casual assistant",
    "current_project_category": None,
    "last_interaction_time": 0.0,
    "consecutive_builds": 0,
    "used_continuity_phrases": []
}


class ContinuityManager:
    """Manages lightweight session continuity, soft decay windows, and repetition safety."""
    
    def __init__(self):
        self.data = self._load()

    def _load(self):
        if not os.path.exists(CONTINUITY_FILE):
            logger.info("[Continuity] File missing. Initializing default continuity state.")
            data = dict(DEFAULT_CONTINUITY)
            self._save_data(data)
            return data
        try:
            with open(CONTINUITY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            # Auto-repair logic
            repaired = False
            for k, v in DEFAULT_CONTINUITY.items():
                if k not in data:
                    data[k] = v
                    repaired = True
                elif v is not None and not isinstance(data[k], type(v)):
                    data[k] = v
                    repaired = True
            if repaired:
                logger.info("[Continuity] Repaired continuity data keys/types.")
                self._save_data(data)
            return data
        except Exception as e:
            logger.warning(f"[Continuity] Load failed/corrupt: {e}. Re-initializing.")
            try:
                self._save_data(DEFAULT_CONTINUITY)
            except Exception:
                pass
            return dict(DEFAULT_CONTINUITY)

    def _save(self):
        self._save_data(self.data)

    def _save_data(self, data):
        try:
            with open(CONTINUITY_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"[Continuity] Failed to save continuity state: {e}")

    def get_decay_factor(self, current_time: float) -> float:
        last_time = self.data.get("last_interaction_time", 0.0)
        if last_time <= 0.0:
            return 0.0
        gap = current_time - last_time
        if gap < 900:  # 15 minutes
            return 1.0
        elif gap < 2700:  # 45 minutes
            return 0.5
        else:
            return 0.0

    def decay_atmosphere_if_needed(self, current_time: float):
        factor = self.get_decay_factor(current_time)
        if factor == 0.0:
            # Natural decay back to default atmosphere
            self.data["active_atmosphere"] = "calm presence"
            self.data["recent_conversational_mode"] = "casual assistant"
            self.data["current_project_category"] = None
            self.data["consecutive_builds"] = 0
            self._save()

    def update_state(self, user_input: str, route: str, is_exploration: bool, is_continuity: bool, current_time: float):
        # Apply decay first
        self.decay_atmosphere_if_needed(current_time)
        
        cleaned = user_input.lower().strip()
        
        if route == "ai_reasoning":
            if is_exploration:
                self.data["recent_conversational_mode"] = "exploration"
                self.data["active_atmosphere"] = "exploration"
            elif is_continuity:
                self.data["recent_conversational_mode"] = "clarification"
                self.data["active_atmosphere"] = "continuity clarification"
            else:
                # Detect project category
                coding_kws = ["code", "coding", "vscode", "vs code", "programming", "python", "develop", "website", "project", "ui", "build", "refine", "compile", "run test"]
                ai_kws = ["ai", "artificial intelligence", "time machine", "model", "llm", "neural", "deep learning", "machine learning", "openai", "ollama", "phi3"]
                
                category = None
                if any(kw in cleaned for kw in coding_kws):
                    category = "coding"
                elif any(kw in cleaned for kw in ai_kws):
                    category = "ai"

                if category:
                    self.data["current_project_category"] = category
                    self.data["recent_conversational_mode"] = "project/build"
                    self.data["active_atmosphere"] = "technical"
                    if any(kw in cleaned for kw in ["build", "run", "test", "compile", "refining", "execute"]):
                        self.data["consecutive_builds"] = self.data.get("consecutive_builds", 0) + 1
                else:
                    # Keep previous active atmosphere or fallback to calm presence if no active session
                    pass
        elif route == "greeting":
            # If greeting, don't immediately overwrite active_atmosphere, but update conversational mode
            self.data["recent_conversational_mode"] = "casual assistant"
        elif route in ["command", "shutdown"]:
            self.data["active_atmosphere"] = "calm presence"
            self.data["recent_conversational_mode"] = "casual assistant"
            self.data["current_project_category"] = None
            self.data["consecutive_builds"] = 0
            
        self.data["last_interaction_time"] = current_time
        self._save()

    def trigger_continuity_greeting(self, user_input: str, current_time: float) -> str | None:
        last_time = self.data.get("last_interaction_time", 0.0)
        if last_time <= 0.0:
            return None
            
        gap = current_time - last_time
        
        # Only trigger for re-entry, not active continuous turns (gap < 60s) or long gaps (gap >= 2700s)
        if gap < 60 or gap >= 2700:
            return None
            
        cleaned = user_input.lower().strip()
        reentry_phrases = ["hey", "hello", "yo", "hi", "continue", "resume", "im back", "i'm back", "whats up", "sup"]
        # Match only generic greetings/re-entry phrases
        if cleaned not in reentry_phrases and len(cleaned.split()) > 3:
            return None

        recent_mode = self.data.get("recent_conversational_mode")
        project_cat = self.data.get("current_project_category")
        
        candidates = []
        if recent_mode == "project/build" or project_cat in ["coding", "ai"]:
            # If assistant/UI specific
            if project_cat == "ai":
                candidates = [
                    "Back to the architecture?",
                    "Still refining the assistant?",
                    "Continuing the build?"
                ]
            else:
                candidates = [
                    "Back to the project?",
                    "Still on the same project?",
                    "Continuing the build?",
                    "Continuing where we left off?"
                ]
        elif recent_mode == "exploration":
            candidates = [
                "Back to the theory?",
                "Continuing where we left off?",
                "Back to the speculation?"
            ]
            
        # Avoid repetitions
        used = self.data.get("used_continuity_phrases", [])
        available = [c for c in candidates if c not in used]
        
        if not available:
            # If all used, reset list to allow them again
            available = candidates
            used = []
            
        if not available:
            return None
            
        selected = random.choice(available)
        
        # Track used phrases (limit size to 5)
        used.append(selected)
        if len(used) > 5:
            used.pop(0)
        self.data["used_continuity_phrases"] = used
        self._save()
        
        return selected
