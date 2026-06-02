import re
from config import Config
from utils.helpers import clean_input
from core.intent_engine import IntentEngine
from utils.logger import get_logger

logger = get_logger(__name__)
_intent_engine = IntentEngine()

# Exploration phrases that must NEVER route to system commands
EXPLORATION_PHRASES = {
    "what if", "imagine", "let's make", "let's build",
    "lets make", "lets build",
    "do you think", "suppose", "could humans", "how would we",
    "what would happen", "could we", "is it possible",
    "how would you", "let's create", "let's design",
    "lets create", "lets design",
    "what would", "if we could", "if humans"
}

def is_greeting_query(cleaned: str) -> tuple[bool, str]:
    if re.match(r'^h+e+y+$', cleaned):
        return True, "hey"
    if re.match(r'^h+e+l+o+$', cleaned):
        return True, "hello"
    if re.match(r'^h+i+$', cleaned):
        return True, "hi"
    if re.match(r'^y+o+$', cleaned):
        return True, "yo"
        
    greetings_map = {
        "hello": "hello", "hey": "hey", "heyy": "hey", "hi": "hi", "yo": "yo", 
        "whats up": "whats up", "sup": "sup", "what's up": "whats up",
        "good morning": "good morning", "morning": "morning", 
        "good afternoon": "good afternoon", "afternoon": "afternoon",
        "good evening": "good evening", "evening": "evening", 
        "im back": "im back", "i'm back": "im back", "im home": "im home", "i'm home": "im home",
        "good night": "good night", "goodnight": "good night", 
        "thanks": "thanks", "thank you": "thanks", 
        "bye": "bye", "cya": "bye", "goodbye": "bye"
    }
    
    if cleaned in greetings_map:
        return True, greetings_map[cleaned]
        
    # Check if starts with a greeting keyword and is very short (1-2 words)
    words = cleaned.split()
    if words and len(words) <= 2:
        first = words[0]
        if first in ["hey", "hi", "hello", "yo"] or re.match(r'^h+e+y+$|^h+e+l+o+$|^h+i+$|^y+o+$', first):
            return True, "hey"
            
    return False, ""


def is_identity_query(cleaned: str) -> bool:
    identity_keywords = [
        "who are you", "what are you", "who made you", "who created you", 
        "who owns you", "who is your boss", "who is your creator", 
        "what should i call you", "who's your boss", "who's your creator",
        "what are your capabilities", "tell me who you are"
    ]
    if cleaned in identity_keywords:
        return True
        
    words = cleaned.split()
    if not words:
        return False
        
    has_question_start = words[0] in ["who", "what", "tell", "how"] or cleaned.startswith("who's") or cleaned.startswith("what's")
    has_you_or_your = any(w in cleaned for w in ["you", "your", "ur"])
    
    if has_question_start and has_you_or_your and any(w in cleaned for w in ["creator", "boss", "created", "made", "own", "owner", "call"]):
        return True
        
    if any(phrase in cleaned for phrase in ["who are you", "what are you", "who's your creator", "who's your boss"]):
        return True
        
    return False


def is_memory_retrieval_query(cleaned: str) -> tuple[bool, str]:
    name_queries = [
        "what is my name", "what's my name", "whats my name", "tell me my name", 
        "remind me my name", "do you know my name", "who am i", "what is my nickname", 
        "remember my name", "can you tell me my name", "whats my nickname", 
        "what's my nickname", "tell me my nickname", "remember me", "what is my name brother",
        "tell me my name please"
    ]
    if cleaned in name_queries:
        action = "nickname" if ("nickname" in cleaned or "call me" in cleaned) else "name"
        return True, action
        
    is_name_topic = "name" in cleaned or "nickname" in cleaned or "who am i" in cleaned or "remember me" in cleaned
    is_memory_cue = any(cue in cleaned for cue in ["what", "whats", "tell", "remind", "know", "remember", "who", "my", "brother", "can you"])
    
    if is_name_topic and is_memory_cue:
        action = "nickname" if ("nickname" in cleaned or "call me" in cleaned) else "name"
        return True, action
        
    return False, ""


def is_utility_query(cleaned: str) -> tuple[bool, str]:
    time_queries = [
        "what's the time", "what time is it", "tell me the time", "current time", "time", "time now", "what is the time"
    ]
    is_time = cleaned in time_queries or (
        "time" in cleaned and any(w in cleaned for w in ["what", "whats", "tell", "current", "now"])
    )
    if is_time:
        return True, "time"
        
    date_queries = [
        "today's date", "what is today's date", "what date is it", "whats today's date", "what is the date", "tell me the date", "current date"
    ]
    is_date = cleaned in date_queries or (
        "date" in cleaned and any(w in cleaned for w in ["what", "whats", "today", "current", "tell"])
    )
    if is_date:
        return True, "date"
        
    day_queries = [
        "what day is today", "what day is it", "what day is it today", "tell me the day", "what is the day", "what day today"
    ]
    is_day = cleaned in day_queries or (
        "day" in cleaned and any(w in cleaned for w in ["what", "today", "tell"]) and "date" not in cleaned
    )
    if is_day:
        return True, "day"
        
    return False, ""


def determine_route(raw_input: str, is_voice: bool = False) -> dict:
    """
    Authority Central: Determines the ONE execution path for the input.
    Returns route as one of: "greeting", "memory_retrieval", "memory_extraction", "utility", "command", "project_mode", "ai_reasoning", "identity"
    """
    cleaned = clean_input(raw_input).lower().strip()
    
    # 0. Wake Word / Trigger Handling (Preserved as-is)
    triggers = ["hey robin", "heyy robin", "hi robin", "hello robin", "yo robin", "robin", "rovin", "navi"]
    found_trigger = None
    for t in triggers:
        if cleaned.startswith(t):
            found_trigger = t
            break
            
    if found_trigger:
        prompt = cleaned[len(found_trigger):].strip()
        if prompt.startswith(",") or prompt.startswith(":"):
            prompt = prompt[1:].strip()
        cleaned = prompt if prompt else "hello"

    # --- DETERMINISTIC COMMAND INTERCEPTION ---
    # 0. Lifecycle Commands
    if cleaned in ("shutdown robin", "shut down robin"):
        return {
            "route": "shutdown",
            "action": "assistant_shutdown",
            "args": None
        }
    elif cleaned in ("exit robin", "terminate robin"):
        return {
            "route": "shutdown",
            "action": "assistant_exit",
            "args": None
        }
    elif cleaned == "close robin":
        return {
            "route": "shutdown",
            "action": "assistant_close",
            "args": None
        }
    elif cleaned == "restart robin":
        return {
            "route": "shutdown",
            "action": "assistant_restart",
            "args": None
        }
    # 1. Close all tabs in chrome / edge
    match = re.match(r"^close\s+all\s+tabs\s+in\s+(chrome|edge)$", cleaned)
    if match:
        browser = match.group(1)
        return {
            "route": "command",
            "action": "close_all_tabs",
            "args": {"browser": browser}
        }
        
    # 2. Close all tabs / close all browser tabs
    if cleaned in ("close all tabs", "close all browser tabs"):
        return {
            "route": "command",
            "action": "close_all_tabs",
            "args": {"browser": None}
        }
        
    # 3. Close website tab (e.g. close youtube tab)
    match = re.match(r"^close\s+([a-z0-9\s]+)\s+tab$", cleaned)
    if match:
        website = match.group(1).strip()
        if website not in ("current", "last"):
            return {
                "route": "command",
                "action": "close_named_tab",
                "args": {"website": website}
            }
            
    # 4. Close current tab / close tab
    if cleaned in ("close current tab", "close tab"):
        return {
            "route": "command",
            "action": "close_current_tab",
            "args": None
        }
        
    # 5. Close last tab
    if cleaned == "close last tab":
        return {
            "route": "command",
            "action": "close_last_tab",
            "args": None
        }
        
    # 6. Close current app
    if cleaned == "close current app":
        return {
            "route": "command",
            "action": "close_current_app",
            "args": None
        }
        
    # 7. Close all windows of X
    match = re.match(r"^close\s+all\s+windows\s+of\s+([a-z0-9\s]+)$", cleaned)
    if match:
        app = match.group(1).strip()
        return {
            "route": "command",
            "action": "close_app_all_windows",
            "args": app
        }
        
    # 8. Minimize / Maximize / Restore / Focus app
    for prefix in ("minimize ", "maximize ", "restore ", "focus ", "bring ", "switch to "):
        if cleaned.startswith(prefix):
            target = cleaned[len(prefix):].strip()
            if prefix == "bring " and target.endswith(" to front"):
                target = target[:-9].strip()
                action = "focus_app"
            elif prefix in ("focus ", "switch to "):
                action = "focus_app"
            elif prefix == "minimize ":
                action = "minimize_app"
            elif prefix == "maximize ":
                action = "maximize_app"
            elif prefix == "restore ":
                action = "restore_app"
            else:
                continue
                
            return {
                "route": "command",
                "action": action,
                "args": target
            }
            
    # 9. Close app
    if cleaned.startswith("close "):
        target = cleaned[6:].strip()
        if len(target.split()) < 4:
            return {
                "route": "command",
                "action": "close_app",
                "args": target
            }

    # Analyze intent early for lifecycle (shutdown) and commands
    intent_data = _intent_engine.analyze_intent(cleaned)

    # 1. LIFECYCLE & SAFETY ROUTING
    # 1.1 Shutdown
    if intent_data["intent"] in ["ASSISTANT_SHUTDOWN_INTENT", "GOOD_NIGHT_INTENT", "SYSTEM_SHUTDOWN_INTENT", "SYSTEM_RESTART_INTENT"]:
        logger.info(f"[Routing] Shutdown - {intent_data['intent']}")
        return {
            "route": "shutdown",
            "action": intent_data["action"],
            "args": None,
            "intent_data": intent_data
        }

    # 1.2 Greetings
    has_greeting, greet_action = is_greeting_query(cleaned)
    if has_greeting:
        logger.info("[Routing] Greeting")
        return {"route": "greeting", "action": greet_action, "args": None}

    # 1.3 Fast Transitions and Moods
    fast_transitions = ["go on", "yeah", "okay", "alright", "continue", "got it", "right", "understood", "sure"]
    exact_moods = {
        "i'm tired": "Long day?",
        "im tired": "Long day?",
        "i'm bored": "Want music or silence?",
        "im bored": "Want music or silence?",
        "i'm stressed": "Take a breath.",
        "i am tired": "Long day?",
        "i am bored": "Want music or silence?",
        "long day": "Yeah? Rough one?",
        "rough day": "What happened?",
        "can't sleep": "Mind won't stop?",
        "cannot sleep": "Mind won't stop?",
        "feeling off": "Since when?",
        "not good": "What's wrong?",
        "overwhelmed": "What's piling up?",
        "can't focus": "What's pulling your attention?",
    }
    if cleaned in fast_transitions:
        if cleaned in ["continue", "go on"]:
            try:
                from memory.presence import ContinuityManager
                import time
                mgr = ContinuityManager()
                decay = mgr.get_decay_factor(time.time())
                if decay > 0.0 and mgr.data.get("active_atmosphere") in ["exploration", "technical"]:
                    logger.info("[Routing] AI escalation (active atmosphere override)")
                    return {"route": "ai_reasoning", "action": "reason", "args": cleaned}
            except Exception as e:
                logger.error(f"Error checking continuity override: {e}")

        logger.info("[Routing] Fast-path")
        return {"route": "fast_transition", "action": "transition", "args": cleaned}
        
    if cleaned in exact_moods:
        logger.info("[Routing] Fast-path")
        return {"route": "fast_transition", "action": "mood", "args": exact_moods[cleaned]}

    # 2. IDENTITY ROUTING (Local Response, No AI call)
    if is_identity_query(cleaned):
        logger.info("[Routing] Identity")
        return {"route": "identity", "action": "identity", "args": cleaned}

    # 3. MEMORY RETRIEVAL & EXTRACTION
    # 3.1 Memory Retrieval Intent Family
    has_mem_retrieval, mem_action = is_memory_retrieval_query(cleaned)
    if has_mem_retrieval:
        logger.info(f"[Routing] Memory Retrieval ({mem_action.title()})")
        return {"route": "memory_retrieval", "action": mem_action, "args": None}

    # Music, anime, browser retrieval patterns
    memory_patterns = {
        "music": r"^what (music|songs) do i (like|play)$",
        "anime": r"^what'?s my favorite anime$",
        "browser": r"^what browser do i use$"
    }
    for key, pattern in memory_patterns.items():
        if re.match(pattern, cleaned):
            logger.info("[Routing] Memory")
            return {"route": "memory_retrieval", "action": key, "args": None}

    # 3.2 Memory Extraction Route (Storage)
    extraction_patterns = {
        "name": r"^my name is (.+)$",
        "nickname": r"^call me (.+)$",
        "browser": r"^my browser is (.+)$"
    }
    for key, pattern in extraction_patterns.items():
        match = re.search(pattern, cleaned)
        if match:
            logger.info("[Routing] Memory")
            return {"route": "memory_extraction", "action": key, "args": match.group(1).strip()}

    # 3.3 Project commands override
    from core.project_manager import project_manager
    is_project_active = project_manager.active_session is not None
    is_project_command = False
    if is_project_active:
        project_phrases = [
            "cancel project", "exit project mode", "start over", "new project",
            "show summary", "project status", "whats next", "what's next", "show roadmap", "current phase"
        ]
        if any(p in cleaned for p in project_phrases):
            is_project_command = True

    if is_project_command:
        logger.info("[Routing] Project Command Override")
        return {
            "route": "project_mode",
            "action": "project_mode",
            "args": cleaned,
            "intent_data": {"intent": "PROJECT_MODE_INTENT", "action": "project_mode", "confidence": 1.0}
        }

    # 4. UTILITY ROUTING
    has_utility, util_action = is_utility_query(cleaned)
    if has_utility:
        logger.info(f"[Routing] Utility ({util_action.title()})")
        return {"route": "utility", "action": util_action, "args": None}

    # 5. COMMANDS ROUTING
    # Check for high-confidence system intents or explicit command markers
    is_system = intent_data["intent"] in [
        "TIME_INTENT", "DATE_INTENT", "BATTERY_INTENT",
        "MEMORY_INTENT", "CPU_INTENT", "SYSTEM_STATUS_INTENT",
        "VOLUME_UP_INTENT", "VOLUME_DOWN_INTENT", "MUTE_INTENT",
        "MEDIA_CONTROL_INTENT"
    ]
    if (is_system and intent_data["confidence"] >= 0.6) or (intent_data["confidence"] >= 0.8 and intent_data["intent"] not in ["UNKNOWN", "PROJECT_MODE_INTENT"]):
        logger.info("[Routing] Command")
        return {
            "route": "command",
            "action": intent_data["action"],
            "args": intent_data.get("args") or cleaned,
            "intent_data": intent_data
        }

    # 6. PROJECT MODE ROUTING
    is_project_intent = intent_data["intent"] == "PROJECT_MODE_INTENT"
    if is_project_intent or is_project_active:
        logger.info("[Routing] Project Mode")
        return {
            "route": "project_mode",
            "action": "project_mode",
            "args": cleaned,
            "intent_data": intent_data
        }

    # 7. AI REASONING ROUTING (Last Resort)
    # Check for exploration first to prevent command false positives
    if any(p in cleaned for p in EXPLORATION_PHRASES):
        logger.info("[Routing] AI")
        return {"route": "ai_reasoning", "action": "explore", "args": cleaned}

    logger.info("[Routing] AI escalation")
    return {"route": "ai_reasoning", "action": "reason", "args": cleaned, "intent_data": intent_data}

def classify_input(user_input: str, is_voice: bool = False) -> dict:
    """Legacy wrapper for backward compatibility."""
    return determine_route(user_input, is_voice)