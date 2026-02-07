
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Adjust path to find src
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.transcriber import Transcriber

class TestProgressiveOutput(unittest.TestCase):
    def setUp(self):
        self.transcriber = Transcriber()
        self.captured_text = []
        
    def text_callback(self, text):
        print(f"Callback received: {text}")
        self.captured_text.append(text)

    @patch("src.transcriber.whisper")
    @patch("os.path.exists")
    def test_transcribe_progressive_output(self, mock_exists, mock_whisper):
        # Setup mocks
        mock_exists.return_value = True
        
        # Mock model
        mock_model = MagicMock()
        mock_whisper.load_model.return_value = mock_model
        
        # Mock audio load
        mock_whisper.load_audio.return_value = [0] * 16000 # 1 sec
        
        # Mock transcribe side effect to simulate verbose output
        def simulate_transcribe(*args, **kwargs):
            # Simulate Whisper verbose output
            # Note: transcriber redirects stdout, so print here should be caught by ProgressCapture
            print("[00:00.000 --> 00:02.000] Hello World")
            print("[00:02.000 --> 00:04.000] This is a test")
            return {"text": "Hello World\nThis is a test", "segments": []}
            
        mock_model.transcribe.side_effect = simulate_transcribe
        
        # Run transcribe with text_callback
        result = self.transcriber.transcribe(
            "dummy.mp3", 
            model_name="tiny", 
            text_callback=self.text_callback
        )
        
        # Verify
        expected_calls = ["Hello World", "This is a test"]
        self.assertEqual(self.captured_text, expected_calls)

if __name__ == "__main__":
    unittest.main()
