# test_adaptation.py
import os
import json
import shutil
import datetime
from core.assistant import RobinAssistant
from memory.user_profile import user_profile

# Paths
CONVERSATIONS_DIR = "memory/conversations"
HABITS_FILE = "memory/habits.json"
PROFILE_FILE = "memory/user_profile.json"

# Backups
backup_conv_dir = "memory/conversations_backup"
backup_habits = "memory/habits_backup.json"

def setup_test_environment(ai_count=0, coding_count=0, play_history=None):
    # Clean/create conversations dir
    if os.path.exists(CONVERSATIONS_DIR):
        shutil.rmtree(CONVERSATIONS_DIR)
    os.makedirs(CONVERSATIONS_DIR)
    
    # Create mock conversations to populate counts
    exchanges = []
    
    for i in range(ai_count):
        exchanges.append({
            "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=i)).isoformat(),
            "user": "let's build a time machine",
            "response": "Collaborating on time machine design."
        })
        
    for i in range(coding_count):
        exchanges.append({
            "timestamp": (datetime.datetime.now() - datetime.timedelta(hours=i)).isoformat(),
            "user": "write python code for a project",
            "response": "Writing code."
        })
        
    if exchanges:
        today_str = datetime.date.today().isoformat()
        with open(os.path.join(CONVERSATIONS_DIR, f"{today_str}.json"), "w") as f:
            json.dump(exchanges, f, indent=2)

    # Set play history
    if play_history is not None:
        user_profile.set("play_history", play_history)
        
    # Remove habits file to force detection run
    if os.path.exists(HABITS_FILE):
        os.remove(HABITS_FILE)

def backup_data():
    if os.path.exists(CONVERSATIONS_DIR):
        if os.path.exists(backup_conv_dir):
            shutil.rmtree(backup_conv_dir)
        shutil.copytree(CONVERSATIONS_DIR, backup_conv_dir)
    if os.path.exists(HABITS_FILE):
        shutil.copy2(HABITS_FILE, backup_habits)

def restore_data():
    if os.path.exists(CONVERSATIONS_DIR):
        shutil.rmtree(CONVERSATIONS_DIR)
    if os.path.exists(backup_conv_dir):
        shutil.copytree(backup_conv_dir, CONVERSATIONS_DIR)
        shutil.rmtree(backup_conv_dir)
    if os.path.exists(HABITS_FILE):
        os.remove(HABITS_FILE)
    if os.path.exists(backup_habits):
        shutil.copy2(backup_habits, HABITS_FILE)
        os.remove(backup_habits)

def run_tests():
    print("=== Adaptation System Tests ===\n")
    backup_data()
    
    try:
        # Test Case 1: Threshold not met (< 3 occurrences)
        print("Test Case 1: Checking if adaptation triggers when threshold is NOT met...")
        setup_test_environment(ai_count=2, coding_count=1)
        a1 = RobinAssistant()
        res1 = a1.process_input("let's build a time machine")
        print(f"User: let's build a time machine")
        print(f"ROBIN: {res1}")
        # Since count was 2, it shouldn't trigger adaptation ("Another AI idea?") yet
        if res1 in ["Another AI idea?", "Still working on that UI system?"]:
            print("FAIL: Adaptation triggered under threshold!")
        else:
            print("PASS: Adaptation did not trigger under threshold.")
            
        print("-" * 40)
        
        # Test Case 2: Threshold met (>= 3 occurrences)
        print("Test Case 2: Checking if adaptation triggers when threshold IS met...")
        setup_test_environment(ai_count=3)
        a2 = RobinAssistant()
        res2 = a2.process_input("let's build a time machine")
        print(f"User: let's build a time machine")
        print(f"ROBIN: {res2}")
        if res2 in ["Another AI idea?", "Still working on that UI system?"]:
            print("PASS: Adaptation triggered successfully when threshold met.")
        else:
            print("FAIL: Adaptation failed to trigger when threshold met!")
            
        print("-" * 40)
        
        # Test Case 3: Fire at maximum ONCE per session
        print("Test Case 3: Checking if adaptation fires at maximum ONCE per session...")
        res3 = a2.process_input("let's build a time machine")
        print(f"User: let's build a time machine (second time)")
        print(f"ROBIN: {res3}")
        if res3 in ["Another AI idea?", "Still working on that UI system?"]:
            print("FAIL: Adaptation triggered more than once in the same session!")
        else:
            print("PASS: Adaptation did not trigger again in the same session.")
            
        print("-" * 40)
        
        # Test Case 4: Habits JSON file creation and contents
        print("Test Case 4: Verifying habits.json file...")
        if os.path.exists(HABITS_FILE):
            with open(HABITS_FILE, "r") as f:
                habits = json.load(f)
            print(f"habits.json contents: {habits}")
            if habits.get("ai_projects", 0) >= 3:
                print("PASS: habits.json correctly tracked AI project count.")
            else:
                print("FAIL: habits.json has incorrect count.")
        else:
            print("FAIL: habits.json was not created!")
            
        print("-" * 40)
        
    finally:
        print("Cleaning up and restoring original conversation files...")
        restore_data()
        print("Restore complete.")

if __name__ == "__main__":
    run_tests()
