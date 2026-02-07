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

    def transcribe(self, audio_path, model_name="base"):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        self.load_model(model_name)
        
        print(f"Transcribing {audio_path}...")
        result = self.model.transcribe(audio_path)
        return result
