# test_meta_intent.py
from core.assistant import RobinAssistant
import time

a = RobinAssistant()

print("\n==============================")
print(" CONVERSATIONAL META-INTENT TESTS")
print("==============================\n")

# ==========================================
# TEST 1 — CANCEL Thread
# ==========================================
print("TEST 1 — CANCEL Thread")
a.process_input("let's build a time machine")
print("USER: let's build a time machine")
print(f"ROBIN (continuity active): {a.continuity_mgr.data.get('active_atmosphere')}")

r = a.process_input("forget this exception")
print("USER: forget this exception")
print(f"ROBIN: {r}")
print(f"Active Atmosphere after cancel: {a.continuity_mgr.data.get('active_atmosphere')}")
print("PASS if ROBIN replies 'Alright, boss.' and atmosphere is 'calm presence'.\n")

# ==========================================
# TEST 2 — SIMPLIFY Response
# ==========================================
print("==============================")
print("TEST 2 — SIMPLIFY Response")
print("==============================")
r1 = a.process_input("what if time travel existed")
print(f"USER: what if time travel existed")
print(f"ROBIN: {r1}")

r2 = a.process_input("english")
print(f"USER: english")
print(f"ROBIN (simplified): {r2}")
print("PASS if ROBIN simplified/rephrased the previous response.\n")

# ==========================================
# TEST 3 — CONTINUE Thread
# ==========================================
print("==============================")
print("TEST 3 — CONTINUE Thread")
print("==============================")
r3 = a.process_input("then what")
print(f"USER: then what")
print(f"ROBIN (continued): {r3}")
print("PASS if ROBIN continues speculating about the simplified time travel concept.\n")

# ==========================================
# TEST 4 — CLARIFY response
# ==========================================
print("==============================")
print("TEST 4 — CLARIFY response")
print("==============================")
r4 = a.process_input("what do you mean")
print(f"USER: what do you mean")
print(f"ROBIN (clarified): {r4}")
print("PASS if ROBIN elaborates/clarifies the theory.\n")

# ==========================================
# TEST 5 — REDIRECT / Cancel + New Subject
# ==========================================
print("==============================")
print("TEST 5 — REDIRECT / Cancel + New Subject")
print("==============================")
a.process_input("let's speculate on wormholes")
print(f"Active Atmosphere: {a.continuity_mgr.data.get('active_atmosphere')}")

r5 = a.process_input("nevermind, what time is it")
print(f"USER: nevermind, what time is it")
print(f"ROBIN: {r5}")
print(f"Active Atmosphere: {a.continuity_mgr.data.get('active_atmosphere')}")
print("PASS if ROBIN outputs the current time and collapses the speculation atmosphere.\n")

print("\n==============================")
print(" META-INTENT TESTS COMPLETE")
print("==============================\n")