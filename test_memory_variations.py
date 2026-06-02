import unittest
from unittest.mock import patch, MagicMock

# Import modules
import core.assistant
from core.assistant import RobinAssistant, _current_response_mode

class TestMemoryVariations(unittest.TestCase):
    @patch('core.assistant.speak')
    @patch('core.assistant.get_logger')
    @patch('core.assistant.user_profile')
    @patch('core.brain.get_ai_response')
    def test_memory_retrieval_variations(self, mock_get_ai_response, mock_profile, mock_get_logger, mock_speak):
        # Setup mock profile
        def mock_get(key, default=None):
            if key == "name":
                return "Himmat"
            if key == "nickname":
                return "boss"
            return default
        mock_profile.get.side_effect = mock_get

        # Set up assistant
        assistant = RobinAssistant()
        
        # Test queries
        queries = [
            ("what is my name", "Himmat"),
            ("what's my name", "Himmat"),
            ("whats my name", "Himmat"),
            ("tell me my name", "Himmat"),
            ("remind me my name", "Himmat"),
            ("do you know my name", "Himmat"),
            ("who am i", "Himmat"),
            ("what is my nickname", "boss"),
            ("remember my name", "Himmat"),
            ("can you tell me my name", "Himmat"),
            ("whats my nickname", "boss"),
            ("what's my nickname", "boss"),
            ("tell me my nickname", "boss"),
            ("remember me", "Himmat"),
            ("what is my name brother", "Himmat"),
            ("tell me my name please", "Himmat")
        ]
        
        for query, expected_substring in queries:
            with self.subTest(query=query):
                # Reset mock
                mock_get_ai_response.reset_mock()
                
                # Run input
                res = assistant.process_input(query)
                
                # 1. Assert get_ai_response (AI reasoning fallback) was NOT called
                mock_get_ai_response.assert_not_called()
                
                # 2. Assert response contains the expected substring
                self.assertIn(expected_substring.lower(), res.lower())
                
                # 3. Assert global response mode is MEDIUM
                from core.assistant import _current_response_mode
                self.assertEqual(_current_response_mode, "MEDIUM")

if __name__ == '__main__':
    unittest.main()
