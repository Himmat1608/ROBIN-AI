import unittest
from unittest.mock import patch, MagicMock

class SyncThread:
    def __init__(self, target, daemon=True):
        self.target = target
    def start(self):
        # Run target synchronously
        self.target()

import core.assistant
from core.assistant import RobinAssistant

class TestLifecycleRefinement(unittest.TestCase):
    def setUp(self):
        from core.project_manager import project_manager
        project_manager.active_session = None

    @patch('core.assistant.speak')
    @patch('core.assistant.get_logger')
    @patch('core.reasoning_engine.get_ai_response')
    @patch('os.system')
    @patch('threading.Thread', SyncThread)
    @patch('time.sleep', return_value=None)
    def test_lifecycle_commands(self, mock_sleep, mock_system, mock_get_ai_response, mock_get_logger, mock_speak):
        # Setup mock AI response
        mock_get_ai_response.return_value = "AI fallback response"
        
        # Initialize assistant
        assistant = RobinAssistant()
        
        # Override on_shutdown to prevent terminating unittest process
        assistant.on_shutdown = MagicMock()
        
        # Test Assistant Shutdown commands
        assistant_shutdown_cases = [
            "shutdown robin",
            "shut down robin",
            "close robin",
            "exit robin",
            "terminate robin",
            "close the robin",
            "turn off the robin"
        ]
        
        for cmd in assistant_shutdown_cases:
            with self.subTest(cmd=cmd):
                mock_system.reset_mock()
                mock_get_ai_response.reset_mock()
                assistant.on_shutdown.reset_mock()
                
                resp = assistant.process_input(cmd)
                
                # Check response is correct
                self.assertIn(resp, ["Bye, boss.", "Good night, boss."])
                # Check no AI reasoning was called
                mock_get_ai_response.assert_not_called()
                # Check no system shutdown command was executed
                mock_system.assert_not_called()
                # Check that assistant shutdown sequence was executed (on_shutdown called)
                assistant.on_shutdown.assert_called_once()

        # Test Good Night commands
        good_night_cases = [
            "good night",
            "goodnight robin",
            "night robin"
        ]
        
        for cmd in good_night_cases:
            with self.subTest(cmd=cmd):
                mock_system.reset_mock()
                mock_get_ai_response.reset_mock()
                assistant.on_shutdown.reset_mock()
                
                resp = assistant.process_input(cmd)
                
                self.assertEqual(resp, "Good night, boss.")
                mock_get_ai_response.assert_not_called()
                mock_system.assert_not_called()
                assistant.on_shutdown.assert_called_once()

        # Test System Shutdown commands
        system_shutdown_cases = [
            "shutdown the system",
            "shut down the computer",
            "turn off the laptop",
            "power off the computer"
        ]
        
        for cmd in system_shutdown_cases:
            with self.subTest(cmd=cmd):
                mock_system.reset_mock()
                mock_get_ai_response.reset_mock()
                assistant.on_shutdown.reset_mock()
                
                resp = assistant.process_input(cmd)
                
                self.assertEqual(resp, "Shutting down the system, boss.")
                mock_get_ai_response.assert_not_called()
                
                # Ensure Windows shutdown command is executed
                mock_system.assert_called_once()
                args, kwargs = mock_system.call_args
                self.assertIn("shutdown", args[0])
                
                # Check that assistant process shutdown also runs
                assistant.on_shutdown.assert_called_once()

        # Test safety/non-triggering inputs
        safety_cases = [
            "shut",
            "good",
            "shutdown the",
            "turn off"
        ]
        
        for cmd in safety_cases:
            with self.subTest(cmd=cmd):
                mock_system.reset_mock()
                mock_get_ai_response.reset_mock()
                assistant.on_shutdown.reset_mock()
                
                resp = assistant.process_input(cmd)
                
                # Ensure it did NOT route to shutdown
                self.assertNotIn("boss.", resp)
                mock_system.assert_not_called()
                assistant.on_shutdown.assert_not_called()

if __name__ == '__main__':
    unittest.main()
