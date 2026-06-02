import os
import json
import time
import unittest
from core.assistant import RobinAssistant
from memory.presence import ContinuityManager, CONTINUITY_FILE

class TestContinuity(unittest.TestCase):
    def setUp(self):
        # Backup continuity file if exists
        self.backup_path = CONTINUITY_FILE + ".bak"
        if os.path.exists(CONTINUITY_FILE):
            os.rename(CONTINUITY_FILE, self.backup_path)
            
    def tearDown(self):
        # Restore continuity file
        if os.path.exists(CONTINUITY_FILE):
            os.remove(CONTINUITY_FILE)
        if os.path.exists(self.backup_path):
            os.rename(self.backup_path, CONTINUITY_FILE)

    def test_continuity_manager_decay(self):
        mgr = ContinuityManager()
        
        # Fresh initialization
        self.assertEqual(mgr.data["active_atmosphere"], "calm presence")
        
        # Update state with project
        current_time = time.time()
        mgr.update_state("let's write some python code", "ai_reasoning", is_exploration=False, is_continuity=False, current_time=current_time)
        self.assertEqual(mgr.data["current_project_category"], "coding")
        self.assertEqual(mgr.data["active_atmosphere"], "technical")
        self.assertEqual(mgr.data["recent_conversational_mode"], "project/build")
        
        # Test strong continuity decay factor (e.g. 5 minutes gap)
        five_min_later = current_time + 300
        factor = mgr.get_decay_factor(five_min_later)
        self.assertEqual(factor, 1.0)
        
        # Test light continuity decay factor (e.g. 30 minutes gap)
        thirty_min_later = current_time + 1800
        factor = mgr.get_decay_factor(thirty_min_later)
        self.assertEqual(factor, 0.5)
        
        # Test minimal/no continuity decay factor (e.g. 50 minutes gap)
        fifty_min_later = current_time + 3000
        factor = mgr.get_decay_factor(fifty_min_later)
        self.assertEqual(factor, 0.0)
        
        # Verify decay resets state
        mgr.decay_atmosphere_if_needed(fifty_min_later)
        self.assertEqual(mgr.data["active_atmosphere"], "calm presence")
        self.assertIsNone(mgr.data["current_project_category"])

    def test_continuity_greeting_trigger(self):
        mgr = ContinuityManager()
        current_time = time.time()
        
        # Active project state
        mgr.update_state("let's build a UI system", "ai_reasoning", is_exploration=False, is_continuity=False, current_time=current_time)
        
        # Gap < 60s should NOT trigger greeting (silence intelligence)
        g1 = mgr.trigger_continuity_greeting("hey", current_time + 30)
        self.assertIsNone(g1)
        
        # Gap 5 mins (300s) should trigger project/build continuity greeting
        g2 = mgr.trigger_continuity_greeting("hey", current_time + 300)
        self.assertIsNotNone(g2)
        self.assertTrue(any(phrase in g2 for phrase in ["project", "build", "assistant"]))
        
        # Verify repetition safety: subsequent check uses a different phrase
        g3 = mgr.trigger_continuity_greeting("hey", current_time + 300)
        self.assertIsNotNone(g3)
        self.assertNotEqual(g2, g3)

    def test_priority_resolution_flow(self):
        assistant = RobinAssistant()
        current_time = time.time()
        
        # 1. Simulate a coding build turn
        res1 = assistant.process_input("run compile build command on python project")
        # Should be command/ai route depending on classifier. 
        # Let's check state updates
        self.assertEqual(assistant.continuity_mgr.data["current_project_category"], "coding")
        self.assertEqual(assistant.continuity_mgr.data["active_atmosphere"], "technical")
        
        # 2. Trigger project continuity re-entry greeting
        # Temporarily mock last interaction time to 5 minutes ago to satisfy re-entry gap
        assistant.continuity_mgr.data["last_interaction_time"] = current_time - 300
        assistant.continuity_mgr._save()
        
        res2 = assistant.process_input("hey")
        # Should return a project continuity greeting like "Back to the project?" or "Continuing the build?"
        self.assertTrue(any(phrase in res2 for phrase in ["project", "build", "assistant"]))

if __name__ == "__main__":
    unittest.main()