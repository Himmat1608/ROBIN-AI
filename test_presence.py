import os
import json
import unittest
import datetime
import shutil
from unittest.mock import patch

from memory.presence import PresenceEngine, PRESENCE_FILE, DEFAULT_PRESENCE

class MockDateTime(datetime.datetime):
    _mock_now_val = None

    @classmethod
    def now(cls, tz=None):
        if cls._mock_now_val is not None:
            return cls._mock_now_val
        return super().now(tz)

class TestPresenceSystem(unittest.TestCase):
    def setUp(self):
        # Backup existing presence.json if it exists
        self.backup_path = PRESENCE_FILE + ".bak"
        if os.path.exists(PRESENCE_FILE):
            shutil.copy2(PRESENCE_FILE, self.backup_path)
            os.remove(PRESENCE_FILE)

    def tearDown(self):
        # Restore backup
        if os.path.exists(PRESENCE_FILE):
            os.remove(PRESENCE_FILE)
        if os.path.exists(self.backup_path):
            shutil.copy2(self.backup_path, PRESENCE_FILE)
            os.remove(self.backup_path)

    def test_default_creation_and_auto_repair(self):
        # Ensure file does not exist
        self.assertFalse(os.path.exists(PRESENCE_FILE))
        
        # Instantiate engine, should create the default file
        engine = PresenceEngine()
        self.assertTrue(os.path.exists(PRESENCE_FILE))
        self.assertEqual(engine.data["last_date"], DEFAULT_PRESENCE["last_date"])

        # Test corruption/invalid JSON handling
        with open(PRESENCE_FILE, "w", encoding="utf-8") as f:
            f.write("{invalid_json: true")
            
        # Re-instantiate, should repair and recreate default
        engine2 = PresenceEngine()
        self.assertEqual(engine2.data["session_count_today"], 0)

        # Test key repair
        del engine2.data["idle_ack_count"]
        engine2._save()
        
        engine3 = PresenceEngine()
        self.assertIn("idle_ack_count", engine3.data)
        self.assertEqual(engine3.data["idle_ack_count"], 0)

    def test_session_context_generation(self):
        engine = PresenceEngine()
        
        # Test time-of-day mapping using MockDateTime
        # Morning (6am–11am)
        MockDateTime._mock_now_val = datetime.datetime(2026, 5, 22, 8, 30, 0)
        with patch('memory.presence.datetime.datetime', MockDateTime):
            context = engine.get_session_context()
            self.assertEqual(context["time_of_day"], "morning")
            self.assertEqual(context["hour"], 8)
            self.assertTrue(context["is_first_session_today"])
            self.assertEqual(context["session_count_today"], 1)

        # Afternoon (11am–5pm)
        MockDateTime._mock_now_val = datetime.datetime(2026, 5, 22, 13, 0, 0)
        with patch('memory.presence.datetime.datetime', MockDateTime):
            context = engine.get_session_context()
            self.assertEqual(context["time_of_day"], "afternoon")

        # Evening (5pm–10pm)
        MockDateTime._mock_now_val = datetime.datetime(2026, 5, 22, 19, 0, 0)
        with patch('memory.presence.datetime.datetime', MockDateTime):
            context = engine.get_session_context()
            self.assertEqual(context["time_of_day"], "evening")

        # Night (10pm–12am)
        MockDateTime._mock_now_val = datetime.datetime(2026, 5, 22, 23, 0, 0)
        with patch('memory.presence.datetime.datetime', MockDateTime):
            context = engine.get_session_context()
            self.assertEqual(context["time_of_day"], "night")

        # Late night (12am–5am)
        MockDateTime._mock_now_val = datetime.datetime(2026, 5, 22, 2, 0, 0)
        with patch('memory.presence.datetime.datetime', MockDateTime):
            context = engine.get_session_context()
            self.assertEqual(context["time_of_day"], "late_night")
            self.assertTrue(context["late_night_session"])

    def test_gap_awareness_calculations(self):
        engine = PresenceEngine()
        
        # Set last session to 5 days ago
        five_days_ago = (datetime.datetime.now() - datetime.timedelta(days=5)).isoformat()
        engine.data["last_session"] = five_days_ago
        engine.data["last_date"] = (datetime.datetime.now() - datetime.timedelta(days=5)).date().isoformat()
        engine._save()
        
        context = engine.get_session_context()
        self.assertEqual(context["days_since_last"], 5)
        self.assertTrue(context["is_first_session_today"])

    def test_silence_probability_and_suppression(self):
        engine = PresenceEngine(silence_bias=True)
        context = engine.get_session_context()
        
        none_count = 0
        iterations = 100
        for _ in range(iterations):
            greeting = engine.get_presence_greeting(context)
            if greeting is None:
                none_count += 1
                
        self.assertGreater(none_count, 0)

        # Test bypass_silence works
        engine_no_bias = PresenceEngine(silence_bias=False)
        greetings = []
        for _ in range(20):
            g = engine_no_bias.get_presence_greeting(context, bypass_silence=True)
            if g:
                greetings.append(g)
        self.assertGreater(len(greetings), 0)

    def test_anti_repetition_behavior(self):
        engine = PresenceEngine(silence_bias=False)
        context = engine.get_session_context()
        
        g1 = engine.get_presence_greeting(context, bypass_silence=True)
        self.assertIsNotNone(g1)
        
        g2 = engine.get_presence_greeting(context, bypass_silence=True)
        if g2:
            self.assertNotEqual(g1, g2)

    def test_inactivity_handling(self):
        engine = PresenceEngine(silence_bias=False)
        
        # No idle greeting under 45 minutes
        self.assertIsNone(engine.get_idle_presence(30))
        
        # 45-90 minutes
        idle_g1 = engine.get_idle_presence(60)
        self.assertIn(idle_g1, ["Back to it?", "Need anything?"])
        
        # 2+ hours
        idle_g2 = engine.get_idle_presence(150)
        self.assertIn(idle_g2, ["Still there?", "Welcome back."])

    def test_contextual_reaction_safety(self):
        engine = PresenceEngine(silence_bias=False)
        
        self.assertEqual(engine.get_contextual_reaction("im home"), "Welcome home, boss.")
        self.assertEqual(engine.get_contextual_reaction("lets continue"), "Alright, boss.")
        self.assertEqual(engine.get_contextual_reaction("long day"), "Yeah... sounds like it.")
        self.assertEqual(engine.get_contextual_reaction("that was exhausting"), "Long day?")
        
        self.assertIsNone(engine.get_contextual_reaction("hello how are you doing"))

if __name__ == "__main__":
    unittest.main()
