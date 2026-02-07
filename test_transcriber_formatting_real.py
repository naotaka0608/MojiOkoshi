
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Adjust path to find src
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.transcriber import Transcriber

class TestTranscriberFormatting(unittest.TestCase):
    def setUp(self):
        self.transcriber = Transcriber()
        
    @patch("src.transcriber.whisper")
    @patch("os.path.exists")
    def test_transcribe_formatting_no_diarization(self, mock_exists, mock_whisper):
        # Setup mocks
        mock_exists.return_value = True
        
        # Mock model
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model
        
        # Mock audio load (just need a length)
        mock_whisper.load_audio.return_value = [0] * 16000 # 1 sec
        

        # Mock transcribe result - NO PUNCTUATION
        mock_model.transcribe.return_value = {
            "text": "こんにちは元気ですかはい、元気です", 
            "segments": [
                {"text": "こんにちは", "start": 0, "end": 1},
                {"text": "元気ですか", "start": 1, "end": 2},
                {"text": "はい、元気です", "start": 2, "end": 3}
            ]
        }
        
        # Run transcribe
        # We need to create a dummy file for os.path.exists to pass, or just rely on mock
        result = self.transcriber.transcribe("dummy.mp3", model_name="tiny")
        
        print(f"Result text: {result['text']!r}")
        
        # Check assertions
        # Expect newlines between segments even without formatting
        expected = "こんにちは\n元気ですか\nはい、元気です"
        
        self.assertEqual(result["text"], expected)


    def test_add_line_breaks_helper(self):
        # Only ? and ？ and 。 are supported currently
        text = "Hello? How are you. I am fine."
        formatted = self.transcriber._add_line_breaks(text)
        # . is not replaced
        self.assertEqual(formatted, "Hello?\n How are you. I am fine.")
        
        text_jp = "こんにちは。元気？はい。"
        formatted_jp = self.transcriber._add_line_breaks(text_jp)
        self.assertEqual(formatted_jp, "こんにちは。\n元気？\nはい。\n")

if __name__ == "__main__":
    unittest.main()
