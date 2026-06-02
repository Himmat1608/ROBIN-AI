import re
from utils.logger import get_logger

logger = get_logger(__name__)

# Action/Prefix triggers for building
BUILD_ACTIONS = [
    "let's build", "lets build",
    "let's create", "lets create",
    "let's make", "lets make",
    "let's design", "lets design",
    "let's structure", "lets structure",
    "start a project", "start a new project",
    "build a", "build an", "build some",
    "create a", "create an", "create some",
    "make a", "make an", "make some",
    "develop a", "develop an",
    "code a", "code an",
    "want to build", "want to create", "want to make",
    "planning to build", "planning to create", "planning to make",
    "new project", "start project"
]

# Noun targets for projects
PROJECT_TARGETS = {
    "Website": ["website", "webpage", "web site", "site", "portfolio", "blog", "e-commerce", "ecommerce", "web app"],
    "Mobile App": ["mobile app", "mobile application", "ios app", "android app", "phone app", "app"],
    "Desktop App": ["desktop app", "desktop application", "gui app", "electron app"],
    "AI Assistant": ["assistant", "bot", "chatbot", "agent", "ai assistant", "copilot", "gpt"],
    "Automation Tool": ["automation", "automation tool", "script", "crawler", "scraper", "task runner"],
    "SaaS Product": ["saas", "software as a service", "saas product", "subscription product"],
    "Dashboard": ["dashboard", "admin panel", "portal", "analytics dashboard"],
    "Game": ["game", "arcade game", "puzzle game", "unity game", "pygame"],
    "Startup Idea": ["startup", "startup idea", "business idea", "company idea"],
    "General Software Project": ["software", "system", "tool", "library", "application", "platform"]
}

class ProjectDetector:
    def __init__(self):
        pass

    def detect_project_intent(self, text: str) -> dict:
        """
        Analyzes user input to detect project-building intent.
        Returns a dict:
        {
            "intent_detected": bool,
            "confidence": float,
            "project_type": str (or None),
            "project_name": str (or None)
        }
        """
        cleaned = text.lower().strip()
        cleaned = re.sub(r'[?!.,]+', '', cleaned)
        cleaned_words = cleaned.split()
        
        # Penalize questions (general inquiries rather than building requests)
        question_words = {"how", "why", "what", "where", "when", "who", "which"}
        is_question = len(cleaned_words) > 0 and cleaned_words[0] in question_words
        
        # Check if the user is asking "how to build" or "what is" vs "let's build"
        # E.g. "how do i build a website" -> question. "let's build a website" -> intent.
        
        confidence = 0.0
        detected_type = None
        matched_action = None
        matched_target = None

        # 1. Check for action match
        for action in BUILD_ACTIONS:
            if action in cleaned:
                # Give higher base weight for very strong actions like "let's build"
                if action in ["let's build", "lets build", "let's create", "lets create", "start a project"]:
                    confidence = max(confidence, 0.8)
                else:
                    confidence = max(confidence, 0.6)
                matched_action = action
                break

        # 2. Check for target match and extract project type
        for category, keywords in PROJECT_TARGETS.items():
            for kw in keywords:
                # Match keyword as full word or boundary match
                pattern = r'\b' + re.escape(kw) + r'\b'
                if re.search(pattern, cleaned):
                    detected_type = category
                    matched_target = kw
                    confidence = max(confidence, 0.5)
                    break
            if detected_type:
                break

        # 3. Combine Action + Target for boost
        if matched_action and detected_type:
            confidence = 0.95
        elif matched_action and not detected_type:
            # If the user says "let's build something"
            if any(w in cleaned for w in ["something", "stuff", "thing", "project"]):
                confidence = 0.8
                detected_type = None
            else:
                # Weak action only
                confidence = 0.5
        elif not matched_action and detected_type:
            # Only target, check if it's high confidence prefix/suffix like "new website"
            if "new" in cleaned or "create" in cleaned:
                confidence = 0.8
            else:
                # E.g. "website project" or just "dashboard"
                confidence = 0.3

        # Apply question penalty unless explicitly "let's build" or similar commands
        if is_question:
            # E.g. "how do i build a website" -> penalize heavily
            # but "how about we build a website" -> keep high
            if not any(phrase in cleaned for phrase in ["let's", "lets", "how about we build", "why don't we build"]):
                confidence -= 0.4

        # Clean score boundaries
        confidence = max(0.0, min(1.0, confidence))
        
        # We consider confidence >= 0.70 to be a project build intent trigger
        intent_detected = confidence >= 0.70

        # Attempt to extract project name if possible
        # E.g. "let's build a website called MyPortfolio" or "let's create a game named Asteroids"
        project_name = None
        name_match = re.search(r'\b(?:called|named|project)\s+([a-zA-Z0-9_\-\s]+)$', text, re.IGNORECASE)
        if name_match:
            project_name = name_match.group(1).strip()
            
        return {
            "intent_detected": intent_detected,
            "confidence": confidence,
            "project_type": detected_type,
            "project_name": project_name
        }
