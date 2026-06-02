import unittest
from unittest.mock import patch, MagicMock

# Import the assistant module
import core.assistant
from core.assistant import RobinAssistant, _current_response_mode

class TestIdentity(unittest.TestCase):
    @patch('core.assistant.speak')
    @patch('core.assistant.get_logger')
    @patch('core.brain.get_ai_response')
    def test_identity_queries(self, mock_get_ai_response, mock_get_logger, mock_speak):
        # Set up assistant
        assistant = RobinAssistant()
        
        # Test identity questions
        identity_queries = [
            "who are you",
            "what are you",
            "who made you",
            "who created you",
            "who owns you",
            "who is your boss",
            "who is your creator",
            "what should i call you",
            "who's your boss",
            "who's your creator",
            "what are your capabilities",
            "tell me who you are"
        ]
        
        for query in identity_queries:
            with self.subTest(query=query):
                # Reset mock
                mock_get_ai_response.reset_mock()
                
                # Run input
                res = assistant.process_input(query)
                
                # 1. Assert get_ai_response (AI reasoning fallback) was NOT called
                mock_get_ai_response.assert_not_called()
                
                # 2. Assert response is not empty
                self.assertTrue(len(res) > 0)
                
                # 3. Assert global response mode is MEDIUM
                from core.assistant import _current_response_mode
                self.assertEqual(_current_response_mode, "MEDIUM")
                
                # 4. Check that response makes sense (doesn't say I'm not sure how to handle that)
                self.assertNotIn("I'm not sure how to handle that", res)

if __name__ == '__main__':
    unittest.main()
