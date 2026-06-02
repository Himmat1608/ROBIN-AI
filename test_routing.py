from core.assistant import RobinAssistant
a = RobinAssistant()

tests = [
    # Greetings — must NEVER call AI
    ("hey",                             "greeting",          "Yeah?"),
    ("hello",                           "greeting",          "Hey."),
    ("good night",                      "greeting",          "Goodnight."),
    ("thanks",                          "greeting",          "Anytime."),

    # Memory retrieval — must NEVER call AI
    ("what's my name",                  "memory_retrieval",  "Himmat"),
    ("what music do i like",            "memory_retrieval",  "play"),
    ("what browser do i use",           "memory_retrieval",  "brave"),

    # Memory extraction — must store and confirm
    ("my name is Himmat",               "memory_extraction", "Got it"),
    ("call me boss",                    "memory_extraction", "Sure"),

    # Commands — must execute, not go to AI
    ("open chrome",                     "command",           "Opening Chrome"),
    ("play blinding lights",            "command",           "Playing"),
    ("what time is it",                 "command",           "PM"),
    ("volume down",                     "command",           "Lowering"),

    # AI reasoning — only these go to AI
    ("let's build a time machine",      "ai_reasoning",      "navigat"),
    ("what if black holes are gateways","ai_reasoning",      "black hole"),
    ("i'm tired",                       "ai_reasoning",      "Long day"),
]

print("=== Routing Test ===\n")
passed = 0
failed = 0

for user_input, expected_route, expected_in_response in tests:
    result = a.process_input(user_input)
    response_ok = expected_in_response.lower() in result.lower()
    status = "P" if response_ok else "F"
    if response_ok:
        passed += 1
    else:
        failed += 1
    print(f"[{status}] {user_input!r}")
    print(f"    Expected: {expected_in_response!r}")
    print(f"    Got:      {result!r}")
    print()

print(f"Passed: {passed}/{passed+failed}")