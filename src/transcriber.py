import whisper
import torch
import os

class Transcriber:
    def __init__(self):
        self.model = None
        self.current_model_name = None

    def load_model(self, model_name="base"):
        if self.model and self.current_model_name == model_name:
            return
            
        print(f"Loading Whisper model: {model_name}...")
        # Check for CUDA
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        self.model = whisper.load_model(model_name, device=device)
        self.current_model_name = model_name
        print("Model loaded.")

    def transcribe(self, audio_path, model_name="base", progress_callback=None):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        self.load_model(model_name)
        
        print(f"Transcribing {audio_path}...")
        
        # Calculate duration for progress
        audio = whisper.load_audio(audio_path)
        duration = len(audio) / 16000 # 16kHz
        print(f"Audio duration: {duration:.2f}s")

        # Capture verbose output to track progress
        import sys
        import io
        import re

        class ProgressCapture(io.StringIO):
            def __init__(self, callback, duration):
                super().__init__()
                self.callback = callback
                self.duration = duration
                self.pattern = re.compile(r"\[(\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}\.\d{3})\]")

            def write(self, text):
                super().write(text)
                sys.__stdout__.write(text) # Pass through
                
                # Parse timestamp
                match = self.pattern.search(text)
                if match and self.callback and self.duration > 0:
                    end_time_str = match.group(2)
                    minutes, seconds = end_time_str.split(":")
                    current_seconds = float(minutes) * 60 + float(seconds)
                    progress = min(current_seconds / self.duration, 1.0)
                    self.callback(progress)

        # Redirect stdout
        original_stdout = sys.stdout
        
        try:
            if progress_callback:
                sys.stdout = ProgressCapture(progress_callback, duration)
            
            result = self.model.transcribe(audio_path, verbose=True, fp16=False) # fp16=False to avoid CPU warning spam if possible, though warning is printed before
        finally:
            sys.stdout = original_stdout

        return result
