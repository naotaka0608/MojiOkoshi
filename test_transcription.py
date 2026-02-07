from src.transcriber import Transcriber
import os

def test_transcriber():
    t = Transcriber()
    audio_file = "test_audio.wav"
    if not os.path.exists(audio_file):
        print(f"Error: {audio_file} not found. Run create_dummy_audio.py first.")
        return

    try:
        print("Starting transcription test...")
        # using tiny model for speed
        result = t.transcribe(audio_file, model_name="tiny")
        print("Transcription result (raw):")
        print(result["text"])
        print("Test Passed!")
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    test_transcriber()
