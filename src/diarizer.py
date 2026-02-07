import os
import torch
from pyannote.audio import Pipeline

class SpeakerDiarizer:
    def __init__(self, use_auth_token=None):
        self.pipeline = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.use_auth_token = use_auth_token or os.environ.get("HF_TOKEN")

    def load_pipeline(self):
        if self.pipeline:
            return

        print("Loading Diarization pipeline...")
        try:
            # Using the standard pretrained model. 
            # Note: This requires acceptance of terms on HF for pyannote/speaker-diarization-3.1
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                use_auth_token=self.use_auth_token
            )
            
            if self.pipeline:
                self.pipeline.to(self.device)
                print(f"Diarization pipeline loaded on {self.device}")
            else:
                print("Failed to load pipeline. Check HF_TOKEN.")
                raise ValueError("Could not load pyannote/speaker-diarization-3.1. Please ensure you have a valid HF_TOKEN and have accepted the model terms on Hugging Face.")
                
        except Exception as e:
            print(f"Error loading diarization pipeline: {e}")
            raise e

    def diarize(self, audio_path):
        if not self.pipeline:
            self.load_pipeline()
            
        print(f"Diarizing {audio_path}...")
        # Run diarization
        diarization = self.pipeline(audio_path)
        
        # Convert to a list of segments
        segments = []
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            # turn.start, turn.end, speaker
            segments.append({
                "start": turn.start,
                "end": turn.end,
                "speaker": speaker
            })
            
        return segments
