import time
import speech_recognition as sr
from voice.speech_manager import speech_manager
from utils.logger import get_logger

logger = get_logger(__name__)

_recognizer = sr.Recognizer()
_recognizer.dynamic_energy_threshold = False
_recognizer.energy_threshold = 80
_recognizer.pause_threshold = 1.0
_recognizer.phrase_threshold = 0.1
_recognizer.non_speaking_duration = 0.3

_mic = None

WAKE_WORDS = {
    "robin", "rovin", "aerobin", "hey robin", "heyy robin",
    "naveen", "navin", "navi", "robyn", "robbin",
    "cabin", "rabin", "raven", "ribbon", "navine"
}

DIRECT_COMMANDS = {
    "open", "play", "pause", "stop", "close", "search",
    "what time", "what's the time", "time", "date",
    "volume up", "volume down", "mute", "raise", "lower",
    "increase", "decrease", "reduce",
    "good night", "goodnight", "goodbye", "bye",
    "hello", "hi", "hey", "thanks",
    "what is", "what are", "what was", "what's",
    "how", "why", "who", "when", "where",
    "tell me", "explain", "define",
    "i'm", "i am", "i feel", "i want", "i need",
    "let's", "lets", "can you", "could you",
    "show me", "find", "look up",
    "next", "previous", "skip", "resume",
    "coding mode", "study mode", "focus mode",
}

_active_mode = False
_active_mode_time = 0
_in_conversation = False
ACTIVE_MODE_TIMEOUT = 8
CONVERSATION_TIMEOUT = 30


def _get_mic():
    global _mic
    if _mic is None:
        _mic = sr.Microphone()
        logger.info(f"Microphone initialized. Energy threshold: {_recognizer.energy_threshold}")
    return _mic


def _is_wake_word(text: str) -> bool:
    text = text.strip().lower()
    for wake in WAKE_WORDS:
        if text == wake or text.startswith(wake + " "):
            return True
    first_word = text.split()[0] if text.split() else ""
    return first_word in WAKE_WORDS


def _strip_wake_word(text: str) -> str:
    text = text.strip().lower()
    for wake in sorted(WAKE_WORDS, key=len, reverse=True):
        if text.startswith(wake):
            remainder = text[len(wake):].strip()
            if remainder.startswith(",") or remainder.startswith(":"):
                remainder = remainder[1:].strip()
            return remainder
    return text


def _is_direct_command(text: str) -> bool:
    text = text.strip().lower()
    for cmd in DIRECT_COMMANDS:
        if text.startswith(cmd):
            return True
    return False


def set_conversation_active(active: bool):
    global _in_conversation, _active_mode_time
    _in_conversation = active
    if active:
        _active_mode_time = time.time()
    logger.info(
        f"[Listener] Conversation mode: {'ON' if active else 'OFF'}")


def trigger_active_mode():
    global _active_mode, _active_mode_time, _in_conversation
    _in_conversation = True
    _active_mode_time = time.time()
    logger.info("[Listener] Listening restored after speech")


def listen(timeout: int = 3, phrase_time_limit: int = 6) -> str:
    global _active_mode, _active_mode_time, _in_conversation

    # Expire active mode
    if _active_mode and time.time() - _active_mode_time > ACTIVE_MODE_TIMEOUT:
        logger.info("Active mode timed out.")
        _active_mode = False

    # Expire conversation mode
    if (_in_conversation
            and time.time() - _active_mode_time > CONVERSATION_TIMEOUT):
        logger.info("[Listener] Conversation window closed.")
        _in_conversation = False

    try:
        if speech_manager.is_currently_speaking():
            return None

        mic = _get_mic()
        with mic as source:
            audio = _recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )

        text = _recognizer.recognize_google(audio)

        if not text or len(text.strip()) < 2:
            return None

        result = text.lower().strip()
        logger.info(f"Heard: {result!r}")

        # Wake word detected
        if _is_wake_word(result):
            command = _strip_wake_word(result)
            if command and len(command) > 1:
                logger.info(f"Wake + Command: {command}")
                _active_mode_time = time.time()
                _in_conversation = True
                return command
            logger.info("Wake word detected. Awaiting command...")
            _active_mode = True
            _active_mode_time = time.time()
            return "hey"

        # Active mode — anything goes
        if _active_mode:
            _active_mode = False
            _in_conversation = True
            _active_mode_time = time.time()
            logger.info(f"Command after wake: {result}")
            return result

        # Conversation mode — let EVERYTHING through
        if _in_conversation:
            _active_mode_time = time.time()
            logger.info(
                f"[Conversation] Followup captured: {result!r}")
            return result

        # Direct commands — known imperatives without wake word
        if _is_direct_command(result):
            logger.info(f"Direct command: {result}")
            _in_conversation = True
            _active_mode_time = time.time()
            return result

        return None

    except sr.WaitTimeoutError:
        return None
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        logger.error(f"Recognition service error: {e}")
        return None
    except Exception as e:
        logger.error(f"Listener error: {e}")
        return None