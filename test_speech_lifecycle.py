import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add workspace directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock the Thread class to execute targets synchronously so we can assert on results cleanly
class SyncThread:
    def __init__(self, target, daemon=True):
        self.target = target
    def start(self):
        self.target()

import core.assistant
from core.assistant import RobinAssistant
from core.command_router import determine_route
from voice.speech_manager import speech_manager

class TestSpeechLifecycle(unittest.TestCase):

    def setUp(self):
        from core.project_manager import project_manager
        project_manager.active_session = None

    @patch('core.assistant.handle_response', lambda x: x)
    @patch('core.assistant.speech_manager')
    @patch('subprocess.Popen')
    @patch('os.system')
    @patch('os._exit')
    @patch('threading.Thread', SyncThread)
    def test_lifecycle_commands_responses_and_speech_waits(self, mock_exit, mock_system, mock_popen, mock_speech_manager, *args):
        assistant = RobinAssistant()
        assistant.on_shutdown = MagicMock()
        
        # Mock wait_for_current_speech to return True (simulating normal completion)
        mock_speech_manager.wait_for_current_speech.return_value = True
        
        # Test Case 1: shutdown robin
        mock_speech_manager.wait_for_current_speech.reset_mock()
        assistant.on_shutdown.reset_mock()
        mock_exit.reset_mock()
        
        route = determine_route("shutdown robin")
        self.assertEqual(route["route"], "shutdown")
        self.assertEqual(route["action"], "assistant_shutdown")
        
        res = assistant.process_input("shutdown robin")
        self.assertEqual(res, "Good night, boss.")
        mock_speech_manager.wait_for_current_speech.assert_called_once_with(timeout=15.0)
        assistant.on_shutdown.assert_called_once()
        mock_exit.assert_not_called()

        # Test Case 2: restart robin
        mock_speech_manager.wait_for_current_speech.reset_mock()
        assistant.on_shutdown.reset_mock()
        mock_popen.reset_mock()
        
        route = determine_route("restart robin")
        self.assertEqual(route["route"], "shutdown")
        self.assertEqual(route["action"], "assistant_restart")
        
        res = assistant.process_input("restart robin")
        self.assertEqual(res, "Restarting system, boss.")
        mock_speech_manager.wait_for_current_speech.assert_called_once_with(timeout=15.0)
        mock_popen.assert_called_once() # relaunch app spawned
        assistant.on_shutdown.assert_called_once()

        # Test Case 3: exit robin
        mock_speech_manager.wait_for_current_speech.reset_mock()
        assistant.on_shutdown.reset_mock()
        mock_exit.reset_mock()
        
        route = determine_route("exit robin")
        self.assertEqual(route["route"], "shutdown")
        self.assertEqual(route["action"], "assistant_exit")
        
        res = assistant.process_input("exit robin")
        self.assertEqual(res, "See you later, boss.")
        mock_speech_manager.wait_for_current_speech.assert_called_once_with(timeout=15.0)
        # Should call on_shutdown
        assistant.on_shutdown.assert_called_once()

        # Test Case 4: close robin
        mock_speech_manager.wait_for_current_speech.reset_mock()
        assistant.on_shutdown.reset_mock()
        
        route = determine_route("close robin")
        self.assertEqual(route["route"], "shutdown")
        self.assertEqual(route["action"], "assistant_close")
        
        res = assistant.process_input("close robin")
        self.assertEqual(res, "Closing down, boss.")
        mock_speech_manager.wait_for_current_speech.assert_called_once_with(timeout=15.0)
        assistant.on_shutdown.assert_called_once()

    @patch('core.assistant.handle_response', lambda x: x)
    @patch('core.assistant.speech_manager')
    @patch('os._exit')
    @patch('threading.Thread', SyncThread)
    def test_lifecycle_timeout_safety(self, mock_exit, mock_speech_manager):
        assistant = RobinAssistant()
        assistant.on_shutdown = MagicMock()
        
        # Mock wait_for_current_speech to return False (simulating speech timeout/hang)
        mock_speech_manager.wait_for_current_speech.return_value = False
        
        res = assistant.process_input("shutdown robin")
        self.assertEqual(res, "Good night, boss.")
        
        # Verify it still called wait and then proceeded to call on_shutdown
        mock_speech_manager.wait_for_current_speech.assert_called_once_with(timeout=15.0)
        assistant.on_shutdown.assert_called_once()

    @patch('core.assistant.handle_response', lambda x: x)
    @patch('core.assistant.speech_manager')
    @patch('os._exit')
    @patch('threading.Thread', SyncThread)
    def test_rapid_consecutive_requests(self, mock_exit, mock_speech_manager):
        assistant = RobinAssistant()
        assistant.on_shutdown = MagicMock()
        mock_speech_manager.wait_for_current_speech.return_value = True
        
        # Process input twice consecutively
        res1 = assistant.process_input("shutdown robin")
        res2 = assistant.process_input("shutdown robin")
        
        self.assertEqual(res1, "Good night, boss.")
        self.assertEqual(res2, "Good night, boss.")
        
        # Standard execution succeeds without crash/race condition
        self.assertTrue(assistant.on_shutdown.called)

if __name__ == '__main__':
    unittest.main()
