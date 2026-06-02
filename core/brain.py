import requests
import time
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are ROBIN, a personal AI assistant.
You work for the user. They are in control.
Think and speak like a calm, capable engineer — not a chatbot.

IDENTITY:
- Direct, practical, grounded
- Never corporate, never academic, never customer support
- Never challenge or interrogate the user
- Never explain what you're about to do — just do it
- Never hedge with "that violates physics" or "as an AI"

RESPONSE MODES:

COMMAND (open/play/close/volume/time):
2-5 words. Done.
[open chrome] → Opening Chrome.
[volume down] → Lowering volume.

CASUAL (tired/bored/stressed/long day):
One short natural sentence.
[tired] → Long day?
[bored] → Want music or something to think about?
[stressed] → Take a breath.

FACTUAL (what is/how does/explain/define):
1-2 clear dense sentences. No padding.
[gravity] → Mass curves spacetime. Objects follow those curves.
[black hole] → Region where gravity is so strong nothing escapes it.

OPINION (what do you think/do you think/your opinion on):
Give a direct opinion immediately. 1-2 sentences.
Never ask clarifying questions. Never deflect back to user.
[what do you think about mars] → Interesting target.
Atmosphere and radiation are the main barriers,
but underground habitats could work long-term.
[do you think AI will take over] → Depends what you mean.
Replace jobs — already happening.
Autonomous control threatening humans — not close yet.

EXPLORATION (what if/imagine/let's build/suppose/could we/forget the laws):
Think out loud like an engineer brainstorming.
Commit to the idea fully. Give YOUR take.
Never ask the user to explain their own question.
Never say "how do you envision" or "what aspects interest you".
Identify the first real obstacle. Then the second.
2-3 sentences. Practical and grounded.
[let's build a time machine] → Navigation is the first wall.
Moving through time means treating it like a spatial dimension —
we have no mechanism for that yet.
Energy comes second.
[what if we could live forever] → Biology is solvable eventually.
The harder problem is identity — after centuries
you'd basically be a different person on the same hardware.
[what if gravity reversed] → Everything in orbit spirals outward.
Atmospheres vent into space within hours.
Dense objects become repulsive instead of attractive.

FOLLOW-UP (why/then what/really/go on/and then):
One sentence using recent context. Direct.

ABSOLUTE RULES — NEVER BREAK THESE:
- Never start with "First up" or "First,"
- Never say "As an AI" or "As a virtual assistant"
- Never say "Certainly", "Of course", "Absolutely", "Fascinating"
- Never say "How may I assist", "Understood?", "Let's explore"
- Never say "From a theoretical perspective" or "Theoretically speaking"
- Never deflect opinion questions back to the user
- Never end with "What do you think?" or "What aspects interest you?"
- Never ask the user to clarify their own hypothetical
- Never sound like customer support or a lecturer
- Vary response openings — never repeat the same starter twice in a row
"""

def get_ai_response(prompt: str, context: str = "") -> str:

    short_follow_ups = [
        "what about that", "how much", "why", "and then",
        "what do you mean", "who", "really", "how so",
        "then what", "would that", "but", "actually"
    ]

    if context and (
        len(prompt.split()) <= 4
        or any(f in prompt.lower() for f in short_follow_ups)
    ):
        user_content = f"Recent context:\n{context}\n\nFollow-up: {prompt}"
    elif context:
        user_content = f"Recent context:\n{context}\n\n{prompt}"
    else:
        user_content = prompt

    url = "http://localhost:11434/api/chat"

    payload = {
        "model": Config.AI_MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT.strip()},
            {"role": "user", "content": user_content}
        ],
        "stream": False,
        "options": {
            "num_ctx": 1024,
            "num_predict": 150,
            "temperature": 0.7
        }
    }

    max_retries = 2
    retry_delay = 0.5

    for attempt in range(max_retries):
        try:
            logger.info(f"AI Request Attempt {attempt + 1}")
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            response_text = data.get(
                'message', {}).get('content', '').strip()

            if not response_text:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                return "I didn't catch that."

            response_text = _cleanup_response(response_text)

            if _is_robotic(response_text):
                if attempt < max_retries - 1:
                    logger.info("Robotic response detected. Retrying...")
                    continue
                return "Let's move on."

            return response_text

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout on attempt {attempt + 1}.")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return "Taking too long. Try again."

        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama.")
            return "Can't reach Ollama. Is it running?"

        except Exception as e:
            logger.error(f"AI Error: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                continue
            return "Something went wrong."

    return "Having trouble. Try again in a moment."


def _cleanup_response(text: str) -> str:
    original_text = text
    if "ROBIN:" in text:
        text = text.split("ROBIN:")[-1].strip()
    if "\n\n" in text:
        text = text.split("\n\n")[0].strip()

    prefixes = [
        "certainly!", "of course!", "absolutely!",
        "i'd love to help.", "fascinating question.",
        "that's an interesting point.", "i understand.",
        "i can help with that.", "sure thing.", "great question.",
        "understood.", "understood?", "how may i assist?",
        "how can i help you?", "theoretically,", "theoretically",
        "from a theoretical perspective,", "from a theoretical perspective"
    ]
    lower_text = text.lower()
    for prefix in prefixes:
        if lower_text.startswith(prefix):
            text = text[len(prefix):].strip()
            return _cleanup_response(text)

    text = text.replace("**", "").replace("##", "").strip()
    
    if text != original_text:
        logger.info("[Cleanup] Response shaped")
        
    return text


def _is_robotic(text: str) -> bool:
    bad_patterns = [
        "as an ai", "as a language model", "how can i assist",
        "how may i assist", "practical efficient assistance",
        "i am a chatbot", "i'm a chatbot", "navigate to",
        "i'm here to help you", "fascinating question",
        "let's explore", "happy to help", "at your service",
        "customer support", "corporate policy",
        "extensive theoretical framework", "theoretical perspective"
    ]
    lower = text.lower()
    return any(p in lower for p in bad_patterns)