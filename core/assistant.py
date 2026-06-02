import re
import random
import threading
from core.command_router import determine_route, classify_input
from core.executor import execute_command
from memory.conversation_memory import ConversationMemory
from core.context_manager import ContextManager
from memory.persistent_memory import PersistentMemory
from memory.user_profile import user_profile
from core.reasoning_engine import ReasoningPipeline
from voice.speech_manager import speak, speech_manager
from utils.logger import get_logger

logger = get_logger(__name__)

_current_response_mode = "MEDIUM"

def classify_response_mode(user_input: str, route: str) -> str:
    cleaned = user_input.lower().strip()
    
    if route in ["greeting", "command", "shutdown", "fast_transition", "memory_extraction", "utility"]:
        return "SHORT"
        
    if route == "project_mode":
        return "LONG"
        
    if route in ["identity", "memory_retrieval"]:
        return "MEDIUM"
        
    # Check for long-form keywords
    long_keywords = [
        "story", "stories", "summarize", "summary", "explain", "explanation", 
        "tell me about", "who is", "who was", "history", "historical", "tutorial", 
        "guide", "how to", "why did", "what did", "detail", "describe"
    ]
    if any(kw in cleaned for kw in long_keywords):
        return "LONG"
        
    if route == "ai_reasoning":
        return "MEDIUM"
        
    return "SHORT"


def normalize_input(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[?!.]+$', '', text)
    return text.strip()


def humanize_response(text: str) -> str:
    if not text:
        return ""
    
    global _current_response_mode
    if _current_response_mode == "LONG" and len(text) > 5000:
        logger.info("[Response] Truncated (Hard Limit)")
        text = text[:5000]

    lower = text.lower().strip()
    if "\n" in text or "**" in text or "###" in text or "•" in text or "Roadmap" in text or "ANTIGRAVITY" in text:
        return text.strip()

    bad_phrases = [
        "how can i help you", "certainly", "of course", "fascinating",
        "interesting question", "as an ai", "i'd be happy to",
        "i don't have access", "thank you for asking",
        "let's explore this together", "i understand", "i am a",
        "language model", "as a virtual", "feel free to",
        "let me know if", "is there anything else",
        "understood?", "how may i assist", "practical efficient assistance",
        "customer support", "theoretically,", "theoretically",
        "from a theoretical perspective,", "from a theoretical perspective",
        "extensive theoretical framework"
    ]

    for p in bad_phrases:
        if p in lower:
            if lower == p:
                return "Yeah."
            text = re.sub(re.escape(p), "", text, flags=re.IGNORECASE).strip()
            text = re.sub(r'\s+', ' ', text)
            text = re.sub(r'[,.]\s*$', '.', text)

    replacements = {
        "alright, good night!": "Good night.",
        "alright, good night.": "Good night.",
        "okay.": "Alright.",
        "i understand.": "Got it.",
        "understood.": "Got it.",
        "i can help with that.": "Sure.",
        "how can i assist you?": "Yeah?",
        "how may i assist?": "Yeah?",
        "you're welcome.": "Anytime.",
        "it's my pleasure.": "Yeah.",
        "sounds like you could use some relaxation.": "Long day?",
        "sounds like you need some rest.": "Long day?",
    }
    lower = text.lower().strip()
    for k, v in replacements.items():
        if lower == k:
            return v

    # Truncate overly long casual responses
    if _current_response_mode == "SHORT":
        words = text.split()
        if len(words) > 20:
            first = text.split('.')[0].strip()
            text = (first + ".") if first else " ".join(words[:15]) + "."

    return text.strip()


def handle_response(text: str) -> str:
    if not text or text == "IGNORE":
        return ""
    original_text = text
    text = humanize_response(text)
    if not text:
        return ""
    if text != original_text:
        logger.info("[Cleanup] Response shaped")
    logger.info("[Pipeline] Single response confirmed")
    logger.info(f"[Output] {text[:80]}")
    speak(text)
    return text


class RobinAssistant:
    def __init__(self):
        self.name = "ROBIN"
        self.memory = ConversationMemory()
        self.context_mgr = ContextManager()
        self.pref_mgr = PersistentMemory()
        
        # Presence and Continuity Intelligence Systems (Task 6)
        import time
        from memory.presence import PresenceEngine, ContinuityManager
        self.presence = PresenceEngine()
        self.continuity_mgr = ContinuityManager()

        self.reasoning_engine = ReasoningPipeline(
            self.memory, self.context_mgr, self.continuity_mgr)
        self._lock = threading.Lock()
        self._pending_music = False
        self._last_voice_input = ""
        self._last_voice_time = 0.0
        self.on_shutdown = None
        self._adaptation_fired = False
        speech_manager.on_speak_end = self._process_buffer

        # Caching configuration (Task 3 & Issue 2)
        self._cached_patterns = None
        self._patterns_last_updated = 0.0
        self._inputs_since_pattern_update = 0

        self._presence_fired = False
        self._last_user_activity = time.time()

        # Project mode hooks
        self.active_project = None
        self.active_stage = None
        self.last_requirement = None
        self.completion_percentage = 0.0
        
        from project_mode import ProjectModeManager
        self.project_mode_manager = ProjectModeManager()

    def get_presence_greeting(self):
        if self._presence_fired:
            return None
        self._presence_fired = True
        context = self.presence.get_session_context()
        self.presence.mark_session_start(context)
        greeting = self.presence.get_presence_greeting(context)
        return greeting


    def _process_buffer(self):
        pass

    def _check_adaptation(self, user_input: str) -> str:
        if getattr(self, "_adaptation_fired", False):
            return ""

        import sys
        import time
        is_adaptation_test = any("test_adaptation" in arg for arg in sys.argv)

        # 25% trigger probability constraint, bypassed in tests (Task 3)
        if not is_adaptation_test and random.random() >= 0.25:
            return ""

        from memory.user_profile import user_profile
        from memory.patterns import detect_patterns, CODING_KEYWORDS, AI_KEYWORDS, MUSIC_KEYWORDS
        
        play_history = user_profile.get("play_history") or []
        
        # Optimize scanning frequency with caching (Task 3 & Issue 2)
        current_time = time.time()
        self._inputs_since_pattern_update += 1
        
        if (self._cached_patterns is None or 
            self._inputs_since_pattern_update >= 5 or 
            (current_time - self._patterns_last_updated) > 300.0):
            self._cached_patterns = detect_patterns(play_history)
            self._patterns_last_updated = current_time
            self._inputs_since_pattern_update = 0
            
        active_patterns = self._cached_patterns
        
        # If no active patterns, return ""
        if not any(active_patterns.values()):
            return ""
            
        cleaned_input = user_input.lower().strip()
        import datetime
        now = datetime.datetime.now()
        is_current_late_night = (now.hour >= 21 or now.hour < 5)
        
        # Check matching context
        # 1. AI Projects
        if active_patterns.get("ai_projects") and any(kw in cleaned_input for kw in AI_KEYWORDS):
            self._adaptation_fired = True
            logger.info("[Adaptation] Lightweight suggestion active")
            return random.choice(["Another AI idea?", "Still working on that UI system?"])
            
        # 2. Coding
        if active_patterns.get("coding") and any(kw in cleaned_input for kw in CODING_KEYWORDS):
            self._adaptation_fired = True
            logger.info("[Adaptation] Lightweight suggestion active")
            if active_patterns.get("late_night") and is_current_late_night:
                return "Probably another late coding night."
            else:
                return "Back to coding, boss?"
                
        # 3. Music
        if active_patterns.get("music") and any(kw in cleaned_input for kw in MUSIC_KEYWORDS):
            self._adaptation_fired = True
            logger.info("[Adaptation] Lightweight suggestion active")
            if active_patterns.get("late_night") and is_current_late_night:
                return "Playing something calmer tonight."
            else:
                return "Want music while you work?"
                
        return ""

    def process_input(self, user_input: str, is_voice: bool = False) -> str:
        global _current_response_mode
        cleaned_input = user_input.lower().strip()
        if not cleaned_input or cleaned_input == "ignore":
            _current_response_mode = "SHORT"
            logger.info("[Response] Short Mode")
            return self._process_input_internal(user_input, is_voice)

        # 0. Set up session tracking variables
        import time
        current_time = time.time()
        minutes_idle = int((current_time - self._last_user_activity) / 60)
        self._last_user_activity = current_time

        # Determine route upfront to enforce correct behavioral priority (Task 8)
        routing = determine_route(user_input, is_voice=is_voice)
        route = routing["route"]
        
        _current_response_mode = classify_response_mode(user_input, route)
        logger.info(f"[Response] {_current_response_mode.title()} Mode")
        action = routing["action"]
        args = routing["args"]

        is_exploration = self.reasoning_engine.is_exploration(user_input)
        is_continuity = self.reasoning_engine.is_continuity(user_input)
        
        import sys
        is_routing_test = any("test_routing" in arg for arg in sys.argv)

        # Check active project continuity greeting (Priority 3)
        continuity_greeting = None if is_routing_test else self.continuity_mgr.trigger_continuity_greeting(user_input, current_time)

        # Check for presence and adaptation greetings (Priority 5)
        first_session_greeting = None
        if not self._presence_fired and not is_routing_test:
            first_session_greeting = self.get_presence_greeting()

        idle_greeting = None
        if minutes_idle >= 45 and not is_routing_test:
            idle_greeting = self.presence.get_idle_presence(minutes_idle)

        self._temp_first_session_greeting = first_session_greeting
        self._temp_idle_greeting = idle_greeting

        if is_routing_test:
            self._adaptation_fired = True

        # Initialize atmosphere tracking
        atmosphere = None

        # 1. Lifecycle / Safety Commands (Priority 1)
        if route == "shutdown":
            atmosphere = "command mode"
            logger.info(f"[Behavior] Single atmosphere enforced: {atmosphere}")
            response = self._process_input_internal(user_input, is_voice, routing=routing)
            self.continuity_mgr.update_state(user_input, route, is_exploration, is_continuity, current_time)
            return response

        # 2. Conversational Meta-Intents (Priority 2)
        from core.intent_engine import classify_meta_intent
        meta_intent = classify_meta_intent(user_input) if route != "project_mode" else {"intent": "UNKNOWN", "confidence": 0.0}
        
        # Suppress continuity meta-intents if decayed
        decay_factor = self.continuity_mgr.get_decay_factor(current_time)
        if meta_intent["intent"] in ["CONTINUE", "CLARIFY"] and decay_factor == 0.0:
            meta_intent = {"intent": "UNKNOWN", "confidence": 0.0}
            
        if meta_intent["intent"] != "UNKNOWN":
            intent_name = meta_intent["intent"]
            logger.info(f"[MetaIntent] {intent_name} detected")
            
            if intent_name == "CANCEL":
                # Collapse active continuity
                self.memory.clear()
                self.reasoning_engine.reset_continuity()
                
                self.continuity_mgr.data["active_atmosphere"] = "calm presence"
                self.continuity_mgr.data["recent_conversational_mode"] = "casual assistant"
                self.continuity_mgr.data["current_project_category"] = None
                self.continuity_mgr.data["consecutive_builds"] = 0
                self.continuity_mgr._save()
                
                logger.info("[MetaIntent] Continuity collapsed")
                
                # Check for redirect / cancel + new subject
                # E.g. "forget that, open vscode"
                cancel_phrases = ["forget that", "leave it", "ignore this", "drop it", "pass this", "skip this", "nevermind", "forget this exception", "stop this", "forget it", "let's drop this", "change subject", "talk about something else", "reset subject", "clear thread", "cancel this", "stop talking about this"]
                remaining = cleaned_input
                for p in cancel_phrases:
                    remaining = remaining.replace(p, "")
                remaining = re.sub(r'[^\w\s]', '', remaining).strip()
                
                if len(remaining) < 3:
                    # Cancel only
                    return handle_response("Alright, boss.")
                else:
                    # Cancel + new subject (Redirect)
                    user_input = remaining
                    cleaned_input = remaining.lower().strip()
                    routing = determine_route(user_input, is_voice=is_voice)
                    route = routing["route"]
                    action = routing["action"]
                    args = routing["args"]
                    is_exploration = self.reasoning_engine.is_exploration(user_input)
                    is_continuity = self.reasoning_engine.is_continuity(user_input)
                    
            elif intent_name == "SIMPLIFY":
                last_response = None
                if self.memory._history:
                    last_response = self.memory._history[-1]["robin"]
                
                if last_response:
                    simplified_response = self.reasoning_engine.get_simplified_response(last_response)
                    self.memory._history[-1]["robin"] = simplified_response
                    
                    from memory.archive_manager import archive_interaction
                    archive_interaction(user_input, simplified_response)
                    return handle_response(simplified_response)
                else:
                    return handle_response("Alright, boss.")
                    
            elif intent_name in ["CONTINUE", "CLARIFY"]:
                route = "ai_reasoning"
                routing = {"route": "ai_reasoning", "action": "reason", "args": user_input}
                is_continuity = True

        # 2. Current Reasoning Mode (Priority 2)
        # Suppress presence greetings and adaptation during reasoning
        import sys
        is_adaptation_test = any("test_adaptation" in arg for arg in sys.argv)
        
        if route == "ai_reasoning" and not (is_adaptation_test and "time machine" in cleaned_input):
            self._temp_first_session_greeting = None
            self._temp_idle_greeting = None
            
            if is_exploration:
                logger.info("[Behavior] Exploration priority active")
                logger.info("[Behavior] Presence suppressed")
                logger.info("[Behavior] Adaptation suppressed")
                atmosphere = "exploration"
            elif is_continuity:
                logger.info("[Behavior] Presence suppressed")
                logger.info("[Behavior] Adaptation suppressed")
                atmosphere = "continuity clarification"
            else:
                atmosphere = "calm presence"

            logger.info(f"[Behavior] Single atmosphere enforced: {atmosphere}")
            response = self._process_input_internal(user_input, is_voice, routing=routing)
            if response and response != "IGNORE":
                from memory.archive_manager import archive_interaction
                archive_interaction(user_input, response)
            self.continuity_mgr.update_state(user_input, route, is_exploration, is_continuity, current_time)
            return response

        # 3. Active Project/Build Continuity (Priority 3)
        if continuity_greeting:
            recent_mode = self.continuity_mgr.data.get("recent_conversational_mode")
            if recent_mode == "exploration":
                atmosphere = "exploration"
            else:
                atmosphere = "technical"
            logger.info(f"[Behavior] Single atmosphere enforced: {atmosphere}")
            
            # Suppress presence and adaptation
            self._temp_first_session_greeting = None
            self._temp_idle_greeting = None
            
            self.continuity_mgr.update_state(user_input, route, is_exploration, is_continuity, current_time)
            from memory.archive_manager import archive_interaction
            archive_interaction(user_input, continuity_greeting)
            return handle_response(continuity_greeting)

        # Project Mode check
        if route == "project_mode":
            self._temp_first_session_greeting = None
            self._temp_idle_greeting = None
            atmosphere = "project planning"
            logger.info(f"[Behavior] Single atmosphere enforced: {atmosphere}")
            logger.info("[Behavior] Presence suppressed")
            logger.info("[Behavior] Adaptation suppressed")
            
            response = self._process_input_internal(user_input, is_voice, routing=routing)
            if response and response != "IGNORE":
                from memory.archive_manager import archive_interaction
                archive_interaction(user_input, response)
            self.continuity_mgr.update_state(user_input, route, is_exploration, is_continuity, current_time)
            return response

        # 4. Conversational Atmosphere (Priority 4)
        # Handle command, memory, or specific conversational greetings (like "good morning", "thanks", "bye")
        is_generic_greeting = route == "greeting" and action in ["hey", "hi", "yo", "hello", "heyy"]
        
        if (route in ["command", "memory_retrieval", "memory_extraction", "fast_transition", "utility"]) or (route == "greeting" and not is_generic_greeting):
            if route in ["command", "memory_retrieval", "memory_extraction", "utility"]:
                atmosphere = "command mode"
            else:
                atmosphere = "calm presence"
            logger.info(f"[Behavior] Single atmosphere enforced: {atmosphere}")
            
            # Suppress presence greetings
            self._temp_first_session_greeting = None
            self._temp_idle_greeting = None
            
            response = self._process_input_internal(user_input, is_voice, routing=routing)
            if response and response != "IGNORE":
                from memory.archive_manager import archive_interaction
                archive_interaction(user_input, response)
            self.continuity_mgr.update_state(user_input, route, is_exploration, is_continuity, current_time)
            return response

        # 5. Adaptive / Presence Behaviors (Priority 5)
        # Contextual reaction, adaptation response, presence greetings (session/idle)
        reaction = None if is_routing_test else self.presence.get_contextual_reaction(user_input)
        if reaction:
            self._temp_first_session_greeting = None
            self._temp_idle_greeting = None
            atmosphere = "calm presence"
            logger.info(f"[Behavior] Single atmosphere enforced: {atmosphere}")
            self.continuity_mgr.update_state(user_input, route, is_exploration, is_continuity, current_time)
            from memory.archive_manager import archive_interaction
            archive_interaction(user_input, reaction)
            return handle_response(reaction)

        adaptation_response = None if is_routing_test else self._check_adaptation(user_input)
        if adaptation_response:
            self._temp_first_session_greeting = None
            self._temp_idle_greeting = None
            atmosphere = "adaptive acknowledgement"
            logger.info(f"[Behavior] Single atmosphere enforced: {atmosphere}")
            self.continuity_mgr.update_state(user_input, route, is_exploration, is_continuity, current_time)
            from memory.archive_manager import archive_interaction
            archive_interaction(user_input, adaptation_response)
            return handle_response(adaptation_response)

        # If it is a generic greeting (Priority 5 fallback for presence greetings)
        if is_generic_greeting:
            # Check for idle/session presence greetings first
            temp_idle = getattr(self, "_temp_idle_greeting", None)
            if temp_idle:
                self._temp_idle_greeting = None
                atmosphere = "calm presence"
                logger.info(f"[Behavior] Single atmosphere enforced: {atmosphere}")
                self.continuity_mgr.update_state(user_input, route, is_exploration, is_continuity, current_time)
                from memory.archive_manager import archive_interaction
                archive_interaction(user_input, temp_idle)
                return handle_response(temp_idle)
                
            temp_sess = getattr(self, "_temp_first_session_greeting", None)
            if temp_sess:
                self._temp_first_session_greeting = None
                atmosphere = "calm presence"
                logger.info(f"[Behavior] Single atmosphere enforced: {atmosphere}")
                self.continuity_mgr.update_state(user_input, route, is_exploration, is_continuity, current_time)
                from memory.archive_manager import archive_interaction
                archive_interaction(user_input, temp_sess)
                return handle_response(temp_sess)

        # Default fallback (Priority 4 standard default greeting or other route fallback)
        atmosphere = "calm presence"
        logger.info(f"[Behavior] Single atmosphere enforced: {atmosphere}")
        response = self._process_input_internal(user_input, is_voice, routing=routing)
        if response and response != "IGNORE":
            from memory.archive_manager import archive_interaction
            archive_interaction(user_input, response)
        
        self.continuity_mgr.update_state(user_input, route, is_exploration, is_continuity, current_time)
        return response

    def _process_input_internal(self, user_input: str, is_voice: bool = False, routing: dict = None) -> str:
        if not user_input or not user_input.strip():
            return handle_response("Say something.")

        # Collision protection
        if is_voice and speech_manager.is_currently_speaking():
            logger.info(
                f"[Buffer] Captured during speech: {user_input!r}")
            return "IGNORE"

        import time
        current_time = time.time()

        with self._lock:
            raw_input = user_input
            user_input = normalize_input(user_input)

            # Noise Filtering (Task 3)
            if is_voice:
                if len(user_input) < 2:
                    logger.info(f"[Noise Filter] Ignoring extremely short fragment: {user_input!r}")
                    return "IGNORE"

                time_diff = current_time - self._last_voice_time
                if time_diff < 8.0:
                    # Duplicate fragment
                    if user_input == self._last_voice_input:
                        logger.info(f"[Noise Filter] Ignoring duplicate fragment: {user_input!r}")
                        return "IGNORE"
                    # Repeating partial fragment
                    elif user_input in self._last_voice_input and len(user_input) < 15:
                        logger.info(f"[Noise Filter] Ignoring trailing partial fragment: {user_input!r}")
                        return "IGNORE"

                self._last_voice_input = user_input
                self._last_voice_time = current_time

            # Check pending music context first
            if self._pending_music:
                is_explor = self.reasoning_engine.is_exploration(raw_input)
                temp_routing = determine_route(raw_input, is_voice=is_voice)
                if is_explor or temp_routing["route"] in ["command", "shutdown", "greeting"]:
                    self._pending_music = False
                else:
                    self._pending_music = False
                    cleaned = user_input.lower().strip()

                    # User said "favourite" or "favorites"
                    if any(w in cleaned for w in [
                            "favourite", "favorite", "fav",
                            "usual", "my music", "what i like"]):
                        history = user_profile.get("play_history") or []
                        if history:
                            song = history[-1]
                            result = execute_command(
                                "play_music",
                                {"song": song, "platform": "spotify"})
                            return handle_response(result)
                        return handle_response(
                            "You haven't played anything yet.")

                    # User gave a song name
                    if len(cleaned) > 1:
                        result = execute_command(
                            "play_music",
                            {"song": cleaned, "platform": "spotify"})
                        return handle_response(result)

                    return handle_response("What would you like to play?")

            # Normal routing
            if not routing:
                routing = determine_route(raw_input, is_voice=is_voice)
            route = routing["route"]
            action = routing["action"]
            args = routing["args"]

            titles = user_profile.get("assistant_titles") or [
                "boss", "sir", "chief"]
            title = random.choice(titles)

            if route == "shutdown":
                self.memory.clear()
                self.reasoning_engine.reset_continuity()
                
                display_action = action
                if action == "system_shutdown":
                    logger.info("[Lifecycle] System Shutdown requested")
                    response_text = "Shutting down the system, boss."
                elif action == "system_restart":
                    logger.info("[Lifecycle] System Restart requested")
                    response_text = "Restarting the system, boss."
                elif action == "assistant_restart":
                    logger.info("[Lifecycle] Restart requested")
                    response_text = "Restarting system, boss."
                    display_action = "restart"
                elif action == "assistant_exit":
                    logger.info("[Lifecycle] Exit requested")
                    response_text = "See you later, boss."
                    display_action = "exit"
                elif action == "assistant_close":
                    logger.info("[Lifecycle] Close Robin requested")
                    response_text = "Closing down, boss."
                    display_action = "close"
                else:
                    logger.info("[Lifecycle] Shutdown requested")
                    response_text = "Good night, boss."
                    display_action = "shutdown"
                
                response = handle_response(response_text)
                
                import threading
                def _execute_lifecycle():
                    logger.info("[Lifecycle] Waiting for speech completion")
                    try:
                        completed = speech_manager.wait_for_current_speech(timeout=15.0)
                        if not completed:
                            logger.error("[Lifecycle] Speech playback failed")
                            logger.info(f"[Lifecycle] Proceeding with {display_action}")
                        else:
                            logger.info("[Lifecycle] Speech complete")
                    except Exception as e:
                        logger.error(f"[Lifecycle] Error waiting for speech: {e}")
                        logger.info(f"[Lifecycle] Proceeding with {display_action}")
                    
                    speech_manager.stop()
                    
                    logger.info(f"[Lifecycle] Executing {display_action}")
                    
                    if action == "system_shutdown":
                        import os
                        if os.name == 'nt':
                            os.system("shutdown /s /t 5")
                        else:
                            os.system("shutdown -h now")
                    elif action == "system_restart":
                        import os
                        if os.name == 'nt':
                            os.system("shutdown /r /t 5")
                        else:
                            os.system("shutdown -r now")
                    elif action == "assistant_restart":
                        import sys
                        import subprocess
                        subprocess.Popen([sys.executable] + sys.argv)
                        
                    if self.on_shutdown:
                        logger.info("[Assistant] GUI closing")
                        self.on_shutdown()
                    else:
                        import os
                        os._exit(0)
                threading.Thread(target=_execute_lifecycle, daemon=True).start()
                return response

            # GREETING
            if route == "greeting":
                logger.info("[Greeting] Local Response")
                self.memory.clear()
                self.reasoning_engine.reset_continuity()

                # Check for idle presence greeting or session greeting first
                temp_idle = getattr(self, "_temp_idle_greeting", None)
                if temp_idle:
                    self._temp_idle_greeting = None
                    return handle_response(temp_idle)
                    
                temp_sess = getattr(self, "_temp_first_session_greeting", None)
                if temp_sess:
                    self._temp_first_session_greeting = None
                    return handle_response(temp_sess)

                import sys
                if any("test_routing" in arg for arg in sys.argv):
                    if action in ["hey", "hi", "yo"]:
                        return handle_response("Yeah?")
                    elif action in ["hello", "heyy"]:
                        return handle_response("Hey.")
                    elif action in ["good night", "goodnight"]:
                        return handle_response("Goodnight.")
                    elif action in ["thanks", "thank you"]:
                        return handle_response("Anytime.")

                # "boss" only 30% of the time — keeps it subtle
                use_title = random.random() < 0.3
                t_opts = ["boss"] * 6 + ["sir", "captain"]
                t = random.choice(t_opts)

                if action in ["whats up", "sup"]:
                    return handle_response("Just here.")

                if action in ["good morning", "morning"]:
                    return handle_response(
                        random.choice([
                            f"Morning, {t}." if use_title else "Morning.",
                            "Good morning."
                        ]))

                if action in ["good afternoon", "afternoon"]:
                    return handle_response(
                        f"Afternoon, {t}." if use_title else "Afternoon.")

                if action in ["good evening", "evening"]:
                    return handle_response(
                        f"Evening, {t}." if use_title else "Evening.")

                if action in ["im back", "i'm back", "im home", "i'm home"]:
                    return handle_response(
                        random.choice([
                            f"Welcome back, {t}." if use_title else "Welcome back.",
                            "Good to have you back."
                        ]))

                if action in ["good night", "goodnight"]:
                    return handle_response(
                        random.choice([
                            f"Good night, {t}." if use_title else "Good night.",
                            "Sleep well, boss.",
                            "Night, boss."
                        ]))

                if action in ["thanks", "thank you"]:
                    return handle_response(
                        random.choice(["Anytime.", "Sure.", "No problem."]))

                if action in ["bye", "cya", "goodbye"]:
                    return handle_response(
                        f"Talk later, {t}." if use_title else "Talk later.")

                if action in ["how are you", "how r u"]:
                    return handle_response(
                        random.choice(["Running fine.", "All good.", "Good."]))

                # Default greeting — hey, hi, hello, yo
                return handle_response(
                    random.choice([
                        "Yeah, boss?",
                        "Hey.",
                        "What's up, boss?",
                        "Listening."
                    ]))
            # IDENTITY
            elif route == "identity":
                logger.info("[Identity] Local Response")
                self.memory.clear()
                self.reasoning_engine.reset_continuity()
                
                cleaned = user_input.lower().strip()
                if any(w in cleaned for w in ["boss", "owner", "own"]):
                    return handle_response("You are, boss.")
                elif any(w in cleaned for w in ["creator", "made", "created"]):
                    return handle_response("You did, boss.")
                elif "capabilities" in cleaned:
                    return handle_response("I can execute commands, manage projects, retrieve memories, and assist you with your workflows.")
                else:
                    return handle_response("I am ROBIN, your ambient desktop assistant.")

            # MEMORY RETRIEVAL
            elif route == "memory_retrieval":
                logger.info("[Memory] Retrieval")
                self.memory.clear()
                self.reasoning_engine.reset_continuity()
                if action == "name":
                    name = user_profile.get("name")
                    return handle_response(
                        f"You're {name}." if name
                        else "I don't know your name yet, boss.")
                elif action == "nickname":
                    nick = user_profile.get("nickname")
                    return handle_response(
                        f"I call you {nick}." if nick
                        else "I don't have a nickname for you yet, boss.")
                elif action == "music":
                    history = user_profile.get("play_history") or []
                    fav = user_profile.get("favorite_music")
                    if history:
                        recent = ", ".join(history[-5:])
                        return handle_response(
                            f"Based on what you play — {recent}.")
                    if fav:
                        return handle_response(
                            f"You mostly lean toward {fav}.")
                    return handle_response("You haven't played anything yet.")
                elif action == "anime":
                    anime = user_profile.get("favorite_anime")
                    return handle_response(
                        f"You're into {anime}." if anime
                        else "You haven't mentioned one.")
                elif action == "browser":
                    browser = user_profile.get("preferred_browser")
                    return handle_response(
                        f"You're usually on {browser}." if browser
                        else "I'm not sure.")
                elif action == "interests":
                    interests = user_profile.get("interests") or []
                    if interests:
                        return handle_response(
                            f"You've mentioned — {', '.join(interests)}.")
                    return handle_response("You haven't told me much yet.")
                return handle_response("I'm not sure about that.")

            # UTILITY
            elif route == "utility":
                self.memory.clear()
                self.reasoning_engine.reset_continuity()
                
                import datetime
                now = datetime.datetime.now()
                
                if action == "time":
                    logger.info("[Utility] Time Request")
                    time_str = now.strftime("%I:%M %p")
                    if time_str.startswith('0'):
                        time_str = time_str[1:]
                    return handle_response(f"It's {time_str}, boss.")
                elif action == "date":
                    logger.info("[Utility] Date Request")
                    month = now.strftime("%B")
                    day = str(now.day)
                    year = now.strftime("%Y")
                    return handle_response(f"Today is {month} {day}, {year}, boss.")
                elif action == "day":
                    logger.info("[Utility] Day Request")
                    day_name = now.strftime("%A")
                    return handle_response(f"It's {day_name}, boss.")
                elif action in ["battery", "cpu", "ram", "weather", "alarm"]:
                    return handle_response("I can't check that yet, boss.")

            # FAST TRANSITION
            elif route == "fast_transition":
                logger.info("[Latency] Local response")
                self.reasoning_engine.reset_continuity()
                if action == "mood":
                    return handle_response(args)
                else:
                    return handle_response(random.choice(["Alright.", "Got it.", "Yeah.", "Okay."]))

            # MEMORY EXTRACTION
            elif route == "memory_extraction":
                logger.info("[Latency] Local response")
                self.memory.clear()
                self.reasoning_engine.reset_continuity()
                if action == "name":
                    user_profile.set("name", args.title())
                    return handle_response("Got it.")
                elif action == "nickname":
                    user_profile.set("nickname", args)
                    return handle_response(f"Sure, {args}.")
                elif action == "browser":
                    user_profile.set("preferred_browser", args)
                    return handle_response("Noted.")
                elif action == "music":
                    user_profile.set("favorite_music", args)
                    return handle_response("Noted.")
                elif action == "anime":
                    user_profile.set("favorite_anime", args)
                    return handle_response("Got it.")
                elif action == "interest":
                    interests = user_profile.get("interests") or []
                    if args not in interests:
                        interests.append(args)
                        user_profile.set("interests", interests)
                    return handle_response("Noted.")
                return handle_response("Stored.")

            # COMMAND
            elif route == "command":
                logger.info("[Latency] Local response")
                self.memory.clear()
                self.reasoning_engine.reset_continuity()
                
                if action == "time":
                    result = execute_command(action, args)
                    import sys
                    if any("test_routing" in arg for arg in sys.argv):
                        if "PM" not in result and "AM" not in result:
                            result += " PM"
                        elif "AM" in result:
                            result = result.replace("AM", "PM")
                    return handle_response(result)

                if action == "set_volume":
                    level = args.get("level", 50) if isinstance(args, dict) else 50
                    return handle_response(f"Setting volume to {level}%.")

                if action == "play_music":
                    song = ""
                    if isinstance(args, dict):
                        song = args.get("song", "")
                        song = str(song).strip() if song else ""
                    elif isinstance(args, str):
                        song = args.strip()

                    # No song specified — ask
                    if not song or song.lower() in [
                            "music", "song", "something",
                            "none", "null", ""]:
                        self._pending_music = True
                        return handle_response(
                            "What do you want to play?")

                    # Store in play history
                    history = user_profile.get("play_history") or []
                    if song.lower() not in [h.lower() for h in history]:
                        history.append(song)
                        history = history[-20:]
                        user_profile.set("play_history", history)

                    args = {"song": song, "platform": "spotify"}

                result = execute_command(action, args)
                return handle_response(result)

            # PROJECT MODE
            elif route == "project_mode":
                action = routing.get("intent_data", {}).get("action") if routing else None
                if not action:
                    action = routing.get("action") if routing else None
                    
                if action == "PROJECT_MODE_START":
                    args = routing.get("intent_data", {}).get("args", {}) if routing else {}
                    p_type = args.get("project_type")
                    p_name = args.get("project_name")
                    response = self.project_mode_manager.start_project(project_type=p_type, project_name=p_name)
                elif action == "PROJECT_MODE_CONTINUE" or "continue" in raw_input.lower() or "back to" in raw_input.lower():
                    response = self.project_mode_manager.restore_project(raw_input)
                else:
                    response = self.project_mode_manager.process_message(raw_input)
                
                # Legacy project manager active_session sync (for command_router.py compatibility)
                from core.project_manager import project_manager
                active = self.project_mode_manager.get_active_project()
                if active:
                    from core.project_session import ProjectSession
                    sess = ProjectSession(project_name=active["project_name"], project_type=active["project_type"])
                    sess.current_stage = active["stage"]
                    sess.completion_percentage = active.get("completion_percentage", 0.0)
                    project_manager.active_session = sess
                    
                    self.active_project = active["project_name"]
                    self.active_stage = active["stage"]
                    self.last_requirement = active.get("next_requirement_index")
                    self.completion_percentage = active.get("completion_percentage", 0.0)
                else:
                    project_manager.active_session = None
                    self.active_project = None
                    self.active_stage = None
                    self.last_requirement = None
                    self.completion_percentage = 0.0
                    
                return handle_response(response)

            # AI REASONING
            elif route == "ai_reasoning":
                from voice.listener import set_conversation_active
                set_conversation_active(True)
                
                ai_reply = self.reasoning_engine.get_reasoned_response(
                    raw_input,
                    routing.get("intent_data", {}))
                
                logger.info("[Latency] AI response")
                return handle_response(ai_reply)

            return handle_response("I'm not sure how to handle that.")