import re
from utils.logger import get_logger

logger = get_logger(__name__)

class IntentEngine:
    """
    Lightweight keyword/intent-based matching system with confidence scoring.
    """
    def __init__(self):
        # ... (rest of the init remains same)
        self.intents = {
            "TIME_INTENT": {
                "action": "time",
                "keywords": {"time", "current", "now", "clock", "hour", "minute"},
                "exact_phrases": [
                    "what's the time", "what time is it", "tell me the time", 
                    "current time", "time now", "what is the time", "time"
                ]
            },
            "DATE_INTENT": {
                "action": "date",
                "keywords": {"date", "today", "day", "month", "year"},
                "exact_phrases": [
                    "what's the date", "what is the date", "tell me the date",
                    "what day is it", "what is today", "current date"
                ]
            },
            "BATTERY_INTENT": {
                "action": "system_status",
                "keywords": {"battery", "power", "charge", "percentage"},
                "exact_phrases": ["battery level", "battery status", "check battery", "battery percentage"]
            },
            "MEMORY_INTENT": {
                "action": "system_status",
                "keywords": {"memory", "ram", "usage", "available"},
                "exact_phrases": ["memory usage", "ram status", "ram usage", "check ram"]
            },
            "CPU_INTENT": {
                "action": "system_status",
                "keywords": {"cpu", "processor", "performance", "load"},
                "exact_phrases": ["cpu usage", "processor load", "cpu status"]
            },
            "VOLUME_UP_INTENT": {
                "action": "volume_up",
                "keywords": {"volume", "increase", "raise", "higher", "louder", "up"},
                "exact_phrases": ["volume up", "increase volume", "raise the volume", "make it louder", "turn it up"]
            },
            "VOLUME_DOWN_INTENT": {
                "action": "volume_down",
                "keywords": {"volume", "decrease", "lower", "reduce", "down", "quieter"},
                "exact_phrases": ["volume down", "lower the volume", "reduce volume", "make it quieter", "turn it down"]
            },
            "SET_VOLUME_INTENT": {
                "action": "set_volume",
                "keywords": {"volume", "set", "to", "percent", "level", "max", "mute"},
                "exact_phrases": ["mute volume", "max volume"]
            },

            "MUTE_INTENT": {
                "action": "mute_audio",
                "keywords": {"mute", "silence", "quiet", "unmute"},
                "exact_phrases": ["mute audio", "silence the computer", "stop sound"]
            },
            "MEDIA_CONTROL_INTENT": {
                "action": "media_os_control",
                "keywords": {"pause", "resume", "play", "next", "previous", "skip", "track", "song"},
                "exact_phrases": ["pause music", "resume playback", "next song", "previous track", "skip this"]
            },
            "SYSTEM_STATUS_INTENT": {
                "action": "system_status",
                "keywords": {"system", "status", "health", "stats"},
                "exact_phrases": ["system status", "system stats", "how is the system"]
            },
            "BROWSER_INTENT": {
                "action": "open chrome",
                "keywords": {"open", "launch", "start", "browser", "chrome", "web"},
                "exact_phrases": ["open chrome", "launch chrome", "start browser", "open browser", "start chrome"]
            },
            "SEARCH_INTENT": {
                "action": "search google",
                "keywords": {"search", "google", "look up", "find"},
                "exact_phrases": []
            },
            "PLAY_MUSIC_INTENT": {
                "action": "play_music",
                "keywords": {"play", "music", "song", "spotify", "apple", "youtube"},
                "exact_phrases": ["play music", "play a song", "play spotify", "start music"]
            },
            "CODING_INTENT": {
                "action": "coding_mode",
                "keywords": {"start", "coding", "mode", "workspace", "code", "dev"},
                "exact_phrases": ["start coding mode", "coding workspace", "let's code", "open coding mode"]
            },
            "STUDY_MODE_INTENT": {
                "action": "study_mode",
                "keywords": {"study", "mode", "focus", "learn"},
                "exact_phrases": ["study mode", "start study mode", "open study mode"]
            },
            "APP_INTENT": {
                "action": "open_app",
                "keywords": {"open", "launch", "start", "app", "spotify", "discord", "slack", "code", "vs", "explorer", "files", "manager", "whatsapp", "brave", "chrome", "notepad"},
                "exact_phrases": [
                    "open spotify", "launch spotify", "start spotify", 
                    "open vs code", "open code", "open explorer", "open file explorer", "open files", "open file manager", 
                    "open whatsapp", "launch whatsapp", "open brave", "launch brave",
                    "open chrome", "launch chrome", "open notepad"
                ]
            },
            "SET_PREF_INTENT": {
                "action": "set_preference",
                "keywords": {"set", "change", "update", "default", "preference", "to", "prefer"},
                "exact_phrases": []
            }
        }
        
    def analyze_intent(self, user_input: str) -> dict:
        """
        Analyzes the user input and returns the most likely intent with a confidence score.
        """
        cleaned = user_input.lower().strip()
        # Remove trailing or excessive punctuation, but preserve domains (e.g. .com)
        cleaned = re.sub(r'[?!]+', '', cleaned)
        cleaned = re.sub(r'(?<=\w)\.(?=\s|$)', '', cleaned)
            
        words = cleaned.split()
        word_set = set(words)

        # 0. HIGH PRIORITY LIFECYCLE DETECTION
        assistant_shutdown_phrases = {
            "shutdown robin", "shut down robin", "close robin", "exit robin", "terminate robin"
        }
        good_night_phrases = {
            "good night", "goodnight robin", "night robin", "goodnight"
        }
        system_shutdown_phrases = {
            "shutdown the system", "shut down the computer", "turn off the laptop", "power off the computer",
            "shutdown system", "shut down system", "turn off computer", "power off computer", "turn off laptop"
        }
        system_restart_phrases = {
            "restart the system", "restart system", "restart computer", "reboot system", "reboot laptop", "restart my pc", "reboot computer"
        }

        if cleaned in assistant_shutdown_phrases:
            logger.info("[IntentEngine] Assistant Shutdown matched")
            return {"intent": "ASSISTANT_SHUTDOWN_INTENT", "action": "assistant_shutdown", "confidence": 1.0}
        
        if cleaned in good_night_phrases:
            logger.info("[IntentEngine] Good Night matched")
            return {"intent": "GOOD_NIGHT_INTENT", "action": "good_night", "confidence": 1.0}
            
        if cleaned in system_shutdown_phrases:
            logger.info("[IntentEngine] System Shutdown matched")
            return {"intent": "SYSTEM_SHUTDOWN_INTENT", "action": "system_shutdown", "confidence": 1.0}

        if cleaned in system_restart_phrases:
            logger.info("[IntentEngine] System Restart matched")
            return {"intent": "SYSTEM_RESTART_INTENT", "action": "system_restart", "confidence": 1.0}
        
        # Project intent detection
        # Check for false triggers first (informational queries)
        info_triggers = [
            "explain ", "how do ", "how does ", "what is ", "what are ", "why do ", "how work",
            "tell me about "
        ]
        has_info_trigger = any(it in cleaned for it in info_triggers) or cleaned.endswith(" work") or cleaned.endswith(" works")
        
        if not has_info_trigger:
            # Check for explicit continuity commands first
            is_continuity = False
            if (cleaned.startswith("continue ") or cleaned.startswith("back to ") or "continue building" in cleaned):
                keywords = ["website", "app", "dashboard", "project", "assistant", "saas", "portfolio", "game", "building"]
                if any(kw in cleaned for kw in keywords):
                    is_continuity = True
            
            if is_continuity:
                logger.info("[IntentEngine] Project continuity detected")
                return {
                    "intent": "PROJECT_MODE_INTENT",
                    "action": "PROJECT_MODE_CONTINUE",
                    "confidence": 1.0,
                    "args": cleaned
                }
            
            # Check for build intents
            from core.project_detector import ProjectDetector
            detector = ProjectDetector()
            detection = detector.detect_project_intent(cleaned)
            if detection["intent_detected"]:
                logger.info(f"[IntentEngine] Project intent detected (conf={detection['confidence']})")
                
                p_type = detection["project_type"]
                p_name = detection["project_name"]
                
                # Map detector types to our supported types
                if p_type == "SaaS Product" or (p_type and "saas" in cleaned):
                    p_type = "SaaS"
                elif p_type == "Dashboard" or (p_type and "dashboard" in cleaned):
                    p_type = "Dashboard"
                elif p_type == "AI Assistant" or (p_type and ("ai" in cleaned or "assistant" in cleaned)):
                    p_type = "AI Product"
                elif p_type and "portfolio" in cleaned:
                    p_type = "Portfolio"
                elif p_type and ("e-commerce" in cleaned or "ecommerce" in cleaned or "store" in cleaned):
                    p_type = "E-commerce"
                elif p_type == "Website":
                    # Ambiguous website start -> trigger discovery
                    p_type = None
                elif p_type:
                    p_type = "Custom"
                
                return {
                    "intent": "PROJECT_MODE_INTENT",
                    "action": "PROJECT_MODE_START",
                    "confidence": detection["confidence"],
                    "args": {
                        "project_type": p_type,
                        "project_name": p_name
                    }
                }
        
        # 1. Conversational Filter (Prevent false commands)
        question_starts = {"who", "what", "how", "why", "where", "when", "which", "do", "does", "is", "are"}
        is_conversational_question = words and words[0] in question_starts and len(words) > 3
        
        best_match = {"intent": "UNKNOWN", "action": None, "confidence": 0.0}
        
        # 1. Structured Parsing Attempt
        from utils.command_parser import parse_command
        parsed = parse_command(cleaned)
        
        if parsed["action"]:
            logger.info(f"[IntentEngine] Command parser matched: {parsed['action']}")
            if parsed["action"] == "open":
                if parsed["url"]:
                    return {
                        "intent": "WEB_INTENT", 
                        "action": "open_url", 
                        "confidence": 1.0, 
                        "args": {"url": parsed["url"], "browser": parsed["browser"], "target": parsed.get("target")}
                    }
                return {
                    "intent": "APP_INTENT", 
                    "action": "open_app", 
                    "confidence": 0.9, 
                    "args": {"app": parsed["target"], "browser": parsed["browser"]}
                }
            elif parsed["action"] == "play":
                return {
                    "intent": "PLAY_MUSIC_INTENT", 
                    "action": "play_music", 
                    "confidence": 0.95, 
                    "args": {"song": parsed["target"], "platform": parsed["platform"] or "spotify"}
                }
        
        # 1.5. Parameter extraction for Volume (Must run before exact matches)
        if "volume" in cleaned:
            match = re.search(r'\b(\d+)\b', cleaned)
            if match:
                vol_level = int(match.group(1))
                logger.info(f"[IntentEngine] Extracted volume level: {vol_level}")
                return {"intent": "SET_VOLUME_INTENT", "action": "set_volume", "confidence": 1.0, "args": {"level": vol_level}}
            elif "max" in cleaned:
                return {"intent": "SET_VOLUME_INTENT", "action": "set_volume", "confidence": 1.0, "args": {"level": 100}}
            elif "mute" in cleaned:
                return {"intent": "SET_VOLUME_INTENT", "action": "set_volume", "confidence": 1.0, "args": {"level": 0}}
        
        # 2. Exact Phrase Matching (Highest Confidence)
        for intent_name, data in self.intents.items():
            for phrase in data["exact_phrases"]:
                if phrase == cleaned or (len(phrase.split()) > 1 and f" {phrase} " in f" {cleaned} "):
                    logger.info(f"[IntentEngine] Exact match: {intent_name}")
                    return {"intent": intent_name, "action": data["action"], "confidence": 1.0}
                
        # 3. Strong Prefix Matching
        if cleaned.startswith("open ") or cleaned.startswith("launch "):
            app_target = cleaned.split(" ", 1)[-1].strip()
            if app_target and len(words) < 6:
                logger.info("[IntentEngine] Prefix match: APP_INTENT")
                return {"intent": "APP_INTENT", "action": "open_app", "confidence": 0.95}
        if cleaned.startswith("play "):
            if len(words) < 8:
                logger.info("[IntentEngine] Prefix match: PLAY_MUSIC_INTENT")
                return {"intent": "PLAY_MUSIC_INTENT", "action": "play_music", "confidence": 0.95}
        if cleaned.startswith("search "):
            logger.info("[IntentEngine] Prefix match: SEARCH_INTENT")
            return {"intent": "SEARCH_INTENT", "action": "search google", "confidence": 0.95}

        # 4. Keyword Overlap Matching
        for intent_name, data in self.intents.items():
            overlap_words = word_set.intersection(data["keywords"])
            overlap = len(overlap_words)
            if overlap > 0:
                score = overlap / max(1, len(words))
                
                # Penalty for generic keywords in long sentences
                if overlap == 1 and list(overlap_words)[0] in {"to", "up", "down", "on", "in", "set"}:
                    if len(words) > 3: score *= 0.1
                
                if score > best_match["confidence"]:
                    best_match = {
                        "intent": intent_name, 
                        "action": data["action"], 
                        "confidence": min(0.8, score + 0.2)
                    }
        
        # Final validation
        if is_conversational_question and best_match["confidence"] < 0.9:
            logger.info(f"[IntentEngine] Conversational filter blocked {best_match['intent']} (conf={best_match['confidence']})")
            return {"intent": "UNKNOWN", "action": None, "confidence": 0.0}
            
        if best_match["confidence"] < 0.5 and best_match["intent"] != "UNKNOWN":
            logger.info(f"[IntentEngine] Confidence too low for {best_match['intent']}: {best_match['confidence']}")
            return {"intent": "UNKNOWN", "action": None, "confidence": 0.0}

        if best_match["intent"] != "UNKNOWN":
            logger.info(f"[IntentEngine] Matched {best_match['intent']} (conf={best_match['confidence']})")
            
        return best_match

META_INTENT_FAMILIES = {
    "CANCEL": {
        "keywords": {"forget", "leave", "ignore", "drop", "pass", "skip", "nevermind", "cancel", "stop", "discard", "reset", "clear", "redirect"},
        "phrases": ["forget that", "leave it", "ignore this", "drop it", "pass this", "skip this", "nevermind", "forget this exception", "stop this", "forget it", "let's drop this", "change subject", "talk about something else", "reset subject", "clear thread", "cancel this", "stop talking about this"]
    },
    "SIMPLIFY": {
        "keywords": {"english", "simple", "easy", "dumb", "normal", "plain", "layman", "shorten", "simplify"},
        "phrases": ["simple words", "easy version", "dumb it down", "normal language", "plain english", "in simple terms", "layman terms", "make it simple", "explain simply", "english please", "speak english"]
    },
    "CONTINUE": {
        "keywords": {"continue", "keep", "go", "next", "then", "more", "resume", "proceed"},
        "phrases": ["then what", "continue", "go on", "and then", "what happens next", "keep going", "keep talking", "go ahead", "tell me more"]
    },
    "CLARIFY": {
        "keywords": {"mean", "explain", "why", "how", "what", "clarify", "detail", "elaborate"},
        "phrases": ["what do you mean", "explain that", "why though", "how exactly", "tell me why", "can you elaborate", "elaborate on that", "what does that mean"]
    }
}

def classify_meta_intent(user_input: str) -> dict:
    cleaned = user_input.lower().strip()
    cleaned_nopunct = re.sub(r'[?!.,]', '', cleaned)
    words = cleaned_nopunct.split()
    word_set = set(words)
    
    if not words:
        return {"intent": "UNKNOWN", "confidence": 0.0}
        
    # 1. Phrase / Substring Matching
    for intent, data in META_INTENT_FAMILIES.items():
        for phrase in data["phrases"]:
            if phrase == cleaned_nopunct or f" {phrase} " in f" {cleaned_nopunct} ":
                return {"intent": intent, "confidence": 1.0}
                
    # 2. Token Overlap and Similarity Scoring
    best_intent = "UNKNOWN"
    best_score = 0.0
    
    for intent, data in META_INTENT_FAMILIES.items():
        overlap = word_set.intersection(data["keywords"])
        if overlap:
            score = len(overlap) / len(word_set)
            
            # Boosts
            if words[0] in data["keywords"]:
                score += 0.2
            if len(words) <= 2:
                score += 0.3
                
            if score > best_score:
                best_score = score
                best_intent = intent
                
    confidence = min(1.0, best_score)
    if confidence >= 0.6:
        return {"intent": best_intent, "confidence": confidence}
        
    return {"intent": "UNKNOWN", "confidence": 0.0}
