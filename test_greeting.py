import unittest
from unittest.mock import patch
from core.assistant import RobinAssistant

class TestGreetings(unittest.TestCase):
    @patch('core.assistant.speak')
    @patch('core.brain.get_ai_response')
    def test_greeting_variations(self, mock_get_ai_response, mock_speak):
        assistant = RobinAssistant()
        
        greetings = [
            "hey",
            "hello",
            "heyy",
            "heyyyy",
            "yo",
            "hi",
            "hello robin",
            "hey robin",
            "heyy robin",
            "thanks",
            "good night",
            "goodnight",
            "bye",
            "cya",
        ]
        
        for g in greetings:
            with self.subTest(greeting=g):
                mock_get_ai_response.reset_mock()
                res = assistant.process_input(g)
                mock_get_ai_response.assert_not_called()
                self.assertIsNotNone(res)
                self.assertTrue(len(res) > 0)
                
if __name__ == '__main__':
    unittest.main()