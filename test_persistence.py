# test_persistence.py
from core.assistant import RobinAssistant
import time

a = RobinAssistant()

print("\n==============================")
print(" PHASE 6.6 TEST SUITE")
print("==============================\n")


# ==========================================
# TEST 1 — Exploration Continuity
# ==========================================

print("TEST 1 — Exploration Continuity")

tests = [
    "what if black holes are gateways",
    "then what",
    "simple words",
]

for t in tests:
    r = a.process_input(t)
    print(f"\nUSER: {t}")
    print(f"ROBIN: {r}")

print("\n[PASS CONDITION]")
print("- Exploration atmosphere preserved")
print("- No chatbot reset")
print("- No random presence injection")
print("- No adaptation hijack")


# ==========================================
# TEST 2 — Exploration Resume
# ==========================================

print("\n==============================")
print("TEST 2 — Exploration Resume")
print("==============================")

a.process_input("what if immortality existed")

print("\n[Waiting 15 seconds to simulate short gap...]")
time.sleep(15)

r = a.process_input("lets continue that theory")

print("\nUSER: lets continue that theory")
print(f"ROBIN: {r}")

print("\n[PASS CONDITION]")
print("- Light continuity acknowledgement")
print("- No giant recap")
print("- No full conversational reset")


# ==========================================
# TEST 3 — Build Momentum
# ==========================================

print("\n==============================")
print("TEST 3 — Build Momentum")
print("==============================")

tests = [
    "lets build a website",
    "i want dark theme",
    "lets continue",
]

for t in tests:
    r = a.process_input(t)
    print(f"\nUSER: {t}")
    print(f"ROBIN: {r}")

print("\n[PASS CONDITION]")
print("- Build atmosphere maintained")
print("- Collaborative energy preserved")
print("- No generic chatbot greeting")


# ==========================================
# TEST 4 — Hard Reset Exploration → Command
# ==========================================

print("\n==============================")
print("TEST 4 — Hard Reset")
print("==============================")

a.process_input("what if time travel existed")

r = a.process_input("open chrome")

print("\nUSER: open chrome")
print(f"ROBIN: {r}")

print("\n[PASS CONDITION]")
print("- Exploration atmosphere collapses immediately")
print("- Clean command execution")
print("- No speculative bleed")


# ==========================================
# TEST 5 — Utility Reset
# ==========================================

print("\n==============================")
print("TEST 5 — Utility Reset")
print("==============================")

a.process_input("lets build an AI assistant")

r = a.process_input("what time is it")

print("\nUSER: what time is it")
print(f"ROBIN: {r}")

print("\n[PASS CONDITION]")
print("- Utility mode isolated")
print("- No build atmosphere contamination")


# ==========================================
# TEST 6 — Presence Suppression
# ==========================================

print("\n==============================")
print("TEST 6 — Presence Suppression")
print("==============================")

tests = [
    "what would happen if gravity stopped",
    "then what",
    "keep going",
]

for t in tests:
    r = a.process_input(t)
    print(f"\nUSER: {t}")
    print(f"ROBIN: {r}")

print("\n[PASS CONDITION]")
print("- No random presence messages")
print("- No adaptation interruption")
print("- Deep reasoning atmosphere preserved")


# ==========================================
# TEST 7 — Single Atmosphere Enforcement
# ==========================================

print("\n==============================")
print("TEST 7 — Single Atmosphere")
print("==============================")

r = a.process_input("lets build a time machine")

print("\nUSER: lets build a time machine")
print(f"ROBIN: {r}")

print("\n[PASS CONDITION]")
print("- ONLY exploration/build atmosphere active")
print("- No stacked greetings/adaptation")
print("- No unrelated project references")


# ==========================================
# TEST 8 — Adaptation Restraint
# ==========================================

print("\n==============================")
print("TEST 8 — Adaptation Restraint")
print("==============================")

spam_tests = [
    "hello robin",
    "open chrome",
    "play music",
    "what if mars was habitable",
    "good night",
    "lets build something",
    "open vscode",
    "continue",
]

for t in spam_tests:
    r = a.process_input(t)
    print(f"\nUSER: {t}")
    print(f"ROBIN: {r}")

print("\n[PASS CONDITION]")
print("- Adaptation appears rarely")
print("- No repetitive pattern references")
print("- No creepy persistence")


# ==========================================
# TEST 9 — Long Gap Decay
# ==========================================

print("\n==============================")
print("TEST 9 — Long Gap Decay")
print("==============================")

a.process_input("what if humans lived forever")

# Mock time-decay gap of 45+ minutes since real time.sleep is too slow
# (45 mins = 2700s, so we simulate gap of 2800s)
# Modify continuity manager data directly for this simulation
current_time = time.time()
a.continuity_mgr.data["last_interaction_time"] = current_time - 2800
a.continuity_mgr._save()

r = a.process_input("continue")

print("\nUSER: continue")
print(f"ROBIN: {r}")

print("\n[PASS CONDITION]")
print("- Continuity weakened naturally")
print("- No aggressive persistence")
print("- No giant memory dump")


# ==========================================
# TEST 10 — Silence Intelligence
# ==========================================

print("\n==============================")
print("TEST 10 — Silence Intelligence")
print("==============================")

a.process_input("lets discuss artificial gravity")

print("\n[DO NOTHING FOR 20–30 SECONDS]")
print("[PASS CONDITION]")
print("- ROBIN stays quiet")
print("- No forced engagement")
print("- No spam presence")


# ==========================================
# FINAL SUMMARY
# ==========================================

print("\n==============================")
print(" FINAL PHASE 6.6 VALIDATION")
print("==============================")

print("""
PASS IF ROBIN:
* Maintains atmosphere continuity
* Preserves conversational momentum
* Resets correctly during commands
* Avoids behavioral stacking
* Keeps adaptation restrained
* Maintains silence intelligently
* Feels grounded and coherent
* Avoids chatbot resets
* Preserves exploration immersion
* Maintains assistant realism
""")
