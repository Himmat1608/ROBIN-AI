import unittest
from unittest.mock import patch, MagicMock

import core.assistant
from core.assistant import humanize_response, classify_response_mode
from core.reasoning_engine import ReasoningPipeline

class TestResponseLength(unittest.TestCase):
    def setUp(self):
        core.assistant._current_response_mode = "SHORT"

    def test_response_mode_classification(self):
        # Verify classification modes
        self.assertEqual(classify_response_mode("what's the time", "utility"), "SHORT")
        self.assertEqual(classify_response_mode("who are you", "identity"), "MEDIUM")
        self.assertEqual(classify_response_mode("what is my name brother", "memory_retrieval"), "MEDIUM")
        self.assertEqual(classify_response_mode("what is the story of One Piece", "ai_reasoning"), "LONG")
        self.assertEqual(classify_response_mode("explain black holes", "ai_reasoning"), "LONG")

    def test_short_mode_truncation(self):
        core.assistant._current_response_mode = "SHORT"
        long_casual_text = "This is the first sentence of a long response. And this is the second sentence which has more words and should be truncated by the humanize response function."
        res = humanize_response(long_casual_text)
        self.assertTrue(len(res.split()) < len(long_casual_text.split()))
        self.assertTrue(res.endswith("."))

    def test_medium_mode_bypasses_casual_truncation(self):
        core.assistant._current_response_mode = "MEDIUM"
        long_casual_text = "This is a very long casual response that has way more than twenty words and should definitely not be truncated in medium mode."
        res = humanize_response(long_casual_text)
        self.assertEqual(res, long_casual_text)

    def test_medium_mode_cleanup_limits(self):
        core.assistant._current_response_mode = "MEDIUM"
        memory = MagicMock()
        context_mgr = MagicMock()
        pipeline = ReasoningPipeline(memory, context_mgr)
        
        ten_sentences = " ".join([f"This is sentence number {i}." for i in range(1, 11)])
        cleaned = pipeline._cleanup_response(ten_sentences, is_exploration=False, user_input="hello")
        
        sentences = cleaned.strip().split(". ")
        self.assertEqual(len(sentences), 8)
        
        long_word_text = " ".join(["word"] * 300) + "."
        cleaned_words = pipeline._cleanup_response(long_word_text, is_exploration=False, user_input="hello")
        self.assertEqual(len(cleaned_words.split()), 250)

    @patch('core.assistant.logger')
    def test_long_mode_hard_limit(self, mock_logger):
        core.assistant._current_response_mode = "LONG"
        long_text = "a" * 6000
        res = humanize_response(long_text)
        self.assertEqual(len(res), 5000)
        mock_logger.info.assert_any_call("[Response] Truncated (Hard Limit)")

if __name__ == '__main__':
    unittest.main()
