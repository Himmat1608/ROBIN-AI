import unittest
from unittest.mock import patch, MagicMock
import datetime
import os

import core.assistant
from core.assistant import RobinAssistant

class TestPhase6Lockdown(unittest.TestCase):
    def setUp(self):
        core.assistant._current_response_mode = "SHORT"

    @patch('core.assistant.speak')
    @patch('core.reasoning_engine.get_ai_response')
    @patch('os._exit')
    @patch('os.system')
    def test_lifecycle_shutdown_robin(self, mock_system, mock_exit, mock_get_ai_response, mock_speak):
        assistant = RobinAssistant()
        assistant.on_shutdown = MagicMock()
        
        res = assistant.process_input("shutdown robin")
        mock_get_ai_response.assert_not_called()
        self.assertEqual(res, "Good night, boss.")
        
        import time
        time.sleep(3.5)
        
        assistant.on_shutdown.assert_called_once()
        mock_exit.assert_not_called()
        mock_system.assert_not_called()

    @patch('core.assistant.speak')
    @patch('core.reasoning_engine.get_ai_response')
    @patch('os._exit')
    @patch('os.system')
    def test_lifecycle_good_night(self, mock_system, mock_exit, mock_get_ai_response, mock_speak):
        assistant = RobinAssistant()
        assistant.on_shutdown = MagicMock()
        
        res = assistant.process_input("good night")
        mock_get_ai_response.assert_not_called()
        self.assertEqual(res, "Good night, boss.")
        
        import time
        time.sleep(3.5)
        assistant.on_shutdown.assert_called_once()

    @patch('core.assistant.speak')
    @patch('core.reasoning_engine.get_ai_response')
    @patch('os._exit')
    @patch('os.system')
    def test_lifecycle_system_shutdown(self, mock_system, mock_exit, mock_get_ai_response, mock_speak):
        assistant = RobinAssistant()
        assistant.on_shutdown = MagicMock()
        
        res = assistant.process_input("shutdown the system")
        mock_get_ai_response.assert_not_called()
        self.assertEqual(res, "Shutting down the system, boss.")
        
        import time
        time.sleep(3.5)
        mock_system.assert_called_once()
        cmd = mock_system.call_args[0][0]
        self.assertTrue("shutdown /s" in cmd or "shutdown -h" in cmd)

    @patch('core.assistant.speak')
    @patch('core.reasoning_engine.get_ai_response')
    @patch('os._exit')
    @patch('os.system')
    def test_lifecycle_system_restart(self, mock_system, mock_exit, mock_get_ai_response, mock_speak):
        assistant = RobinAssistant()
        assistant.on_shutdown = MagicMock()
        
        res = assistant.process_input("restart the system")
        mock_get_ai_response.assert_not_called()
        self.assertEqual(res, "Restarting the system, boss.")
        
        import time
        time.sleep(3.5)
        mock_system.assert_called_once()
        cmd = mock_system.call_args[0][0]
        self.assertTrue("shutdown /r" in cmd or "shutdown -r" in cmd)

    @patch('core.assistant.speak')
    @patch('core.reasoning_engine.get_ai_response')
    def test_lifecycle_safety_guards(self, mock_get_ai_response, mock_speak):
        assistant = RobinAssistant()
        mock_get_ai_response.return_value = "Mock reasoning response."
        
        res1 = assistant.process_input("shut")
        self.assertNotEqual(res1, "Good night, boss.")
        self.assertNotEqual(res1, "Shutting down the system, boss.")
        
        res2 = assistant.process_input("restart")
        self.assertNotEqual(res2, "Restarting the system, boss.")
        
        res3 = assistant.process_input("good")
        self.assertNotEqual(res3, "Good night, boss.")

    @patch('core.assistant.speak')
    @patch('core.reasoning_engine.get_ai_response')
    def test_utility_time(self, mock_get_ai_response, mock_speak):
        assistant = RobinAssistant()
        res = assistant.process_input("what's the time")
        mock_get_ai_response.assert_not_called()
        self.assertIn("boss", res.lower())
        self.assertTrue("am" in res.lower() or "pm" in res.lower())

    @patch('core.assistant.speak')
    @patch('core.reasoning_engine.get_ai_response')
    def test_utility_date(self, mock_get_ai_response, mock_speak):
        assistant = RobinAssistant()
        res = assistant.process_input("what's the date")
        mock_get_ai_response.assert_not_called()
        self.assertIn("today is", res.lower())

    @patch('core.assistant.speak')
    @patch('core.reasoning_engine.get_ai_response')
    def test_identity_boss(self, mock_get_ai_response, mock_speak):
        assistant = RobinAssistant()
        res = assistant.process_input("who is your boss")
        mock_get_ai_response.assert_not_called()
        self.assertEqual(res, "You are, boss.")

    @patch('core.assistant.speak')
    @patch('core.assistant.user_profile')
    @patch('core.reasoning_engine.get_ai_response')
    def test_memory_name(self, mock_get_ai_response, mock_profile, mock_speak):
        mock_profile.get.return_value = "Himmat"
        assistant = RobinAssistant()
        res = assistant.process_input("what is my name brother")
        mock_get_ai_response.assert_not_called()
        self.assertIn("himmat", res.lower())

    @patch('core.assistant.speak')
    @patch('core.reasoning_engine.get_ai_response')
    def test_local_greeting_heyyyy(self, mock_get_ai_response, mock_speak):
        assistant = RobinAssistant()
        # Prevent presence greeting from overriding local greeting matching check
        assistant._presence_fired = True
        res = assistant.process_input("heyyyy")
        mock_get_ai_response.assert_not_called()
        self.assertIn(res, ["Yeah, boss?", "Hey.", "What's up, boss?", "Listening."])

    @patch('core.assistant.speak')
    @patch('core.reasoning_engine.get_ai_response')
    def test_long_response_story(self, mock_get_ai_response, mock_speak):
        long_summary = "One Piece is about Monkey D. Luffy " + ("and his straw hat crew " * 150)
        mock_get_ai_response.return_value = long_summary
        
        assistant = RobinAssistant()
        res = assistant.process_input("story of one piece")
        
        mock_get_ai_response.assert_called_once()
        self.assertTrue(len(res) > 200)
        self.assertEqual(res, long_summary.strip())

    @patch('core.assistant.speak')
    @patch('core.reasoning_engine.get_ai_response')
    def test_long_response_educational(self, mock_get_ai_response, mock_speak):
        long_edu = "Black holes are regions of space " + ("where gravity is incredibly dense " * 200)
        mock_get_ai_response.return_value = long_edu
        
        assistant = RobinAssistant()
        res = assistant.process_input("explain black holes")
        
        mock_get_ai_response.assert_called_once()
        self.assertEqual(len(res), 5000)
        self.assertEqual(res, long_edu[:5000])

if __name__ == '__main__':
    unittest.main()
