import unittest
from unittest.mock import patch
import datetime

from core.assistant import RobinAssistant

class TestUtilities(unittest.TestCase):
    @patch('core.assistant.speak')
    @patch('core.brain.get_ai_response')
    def test_utility_queries(self, mock_get_ai_response, mock_speak):
        assistant = RobinAssistant()
        
        # 1. Test time query
        res_time = assistant.process_input("what's the time")
        mock_get_ai_response.assert_not_called()
        self.assertIn("boss", res_time.lower())
        self.assertTrue("am" in res_time.lower() or "pm" in res_time.lower())
        
        # 2. Test date query
        res_date = assistant.process_input("today's date")
        mock_get_ai_response.assert_not_called()
        self.assertIn("today is", res_date.lower())
        
        # 3. Test day query
        res_day = assistant.process_input("what day is today")
        mock_get_ai_response.assert_not_called()
        self.assertIn("it's", res_day.lower())
        
if __name__ == '__main__':
    unittest.main()
