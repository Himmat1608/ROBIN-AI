import re

BROWSERS = {"chrome", "brave", "firefox", "edge", "opera"}
PLATFORMS = {
    "spotify",
    "youtube",
    "apple music",
    "soundcloud"
}

KNOWN_ALIASES = {
    "youtube": "https://youtube.com",
    "github": "https://github.com",
    "reddit": "https://reddit.com"
}

ACTIONS = {
    "open": {"open", "launch", "start", "show"},
    "play": {"play"},
    "search": {"search", "google", "find", "look up"},
    "close": {"close", "quit", "exit", "kill"},
}

def parse_command(text: str) -> dict:
    result = {
        "action": None,
        "target": None,
        "browser": None,
        "platform": None,
        "url": None
    }

    text = text.lower().strip()

    if not text:
        return result

    # Detect URLs/domains before stripping anything
    domain_pattern = r'\b[a-zA-Z0-9.\-_]+\.[a-zA-Z]{2,4}\b'
    domain_match = re.search(domain_pattern, text)
    has_domain = bool(domain_match)

    words = text.split()

    # Detect action
    for action, verbs in ACTIONS.items():
        if words[0] in verbs:
            result["action"] = action
            words = words[1:]
            break

    if not result["action"]:
        return result

    # Remove filler words
    fillers = {"a", "an", "the", "some", "for", "me"}
    words = [w for w in words if w not in fillers]

    remaining = " ".join(words)

    # Multi-word browser/platform parsing
    for browser in BROWSERS:
        phrase = f" on {browser}"
        if remaining.endswith(phrase):
            result["browser"] = browser
            remaining = remaining[:-len(phrase)].strip()

    for platform in PLATFORMS:
        phrase = f" on {platform}"
        if remaining.endswith(phrase):
            result["platform"] = platform
            remaining = remaining[:-len(phrase)].strip()

    # Detect URL / Domain
    if remaining in KNOWN_ALIASES:
        result["url"] = KNOWN_ALIASES[remaining]
        result["target"] = remaining
    elif has_domain or re.search(domain_pattern, remaining):
        # Preserve domain exactly as-is
        result["target"] = remaining
    elif remaining:
        result["target"] = remaining

    return result
