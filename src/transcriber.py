import whisper
import torch
import os

class Transcriber:
    def __init__(self):
        self.model = None
        self.current_model_name = None
        self.diarizer = None

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

    def _get_speaker_for_segment(self, start, end, diarization_segments):
        if not diarization_segments:
            return None
            
        # Find all speakers in this segment range
        speakers = {}
        for seg in diarization_segments:
            # Check overlap
            seg_start = seg["start"]
            seg_end = seg["end"]
            
            overlap_start = max(start, seg_start)
            overlap_end = min(end, seg_end)
            
            if overlap_end > overlap_start:
                duration = overlap_end - overlap_start
                speaker = seg["speaker"]
                speakers[speaker] = speakers.get(speaker, 0) + duration
        
        if not speakers:
            return None
            
        # Return speaker with max duration
        return max(speakers, key=speakers.get)


    def _add_line_breaks(self, text):
        """
        Add line breaks after punctuation marks for better readability.
        """
        if not text:
            return ""
        
        # Apply line break on period and question marks
        text = text.replace("。", "。\n")
        text = text.replace("?", "?\n") 
        text = text.replace("？", "？\n")
        return text

    def transcribe(self, audio_path, model_name="base", progress_callback=None, hf_token=None):
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
            
            result = self.model.transcribe(audio_path, verbose=True, fp16=False)
            
            # Reset stdout right after transcription is done
            sys.stdout = original_stdout
            
            # Perform Diarization if HF_TOKEN is available
            # Note: We prioritize the hf_token passed in, then env var (checked in Diarizer)
            if hf_token or os.environ.get("HF_TOKEN"):
                try:
                    from .diarizer import SpeakerDiarizer
                    if not self.diarizer:
                        self.diarizer = SpeakerDiarizer(use_auth_token=hf_token)
                    
                    diarization_segments = self.diarizer.diarize(audio_path)
                    
                    # Merge results
                    # "segments" key in result contains list of {start, end, text, ...}
                    formatted_text = ""
                    current_speaker = None
                    speaker_mapping = {} # Map SPEAKER_00 to Aさん, SPEAKER_01 to Bさん etc.
                    speaker_count = 0
                    
                    segments_with_speaker = []
                    
                    for segment in result["segments"]:
                        start = segment["start"]
                        end = segment["end"]
                        text = segment["text"]
                        
                        speaker_label = self._get_speaker_for_segment(start, end, diarization_segments)
                        
                        if speaker_label:
                            if speaker_label not in speaker_mapping:
                                # Assign simplified names A, B, C...
                                # Or just use the label if preferred, but user asked for Aさん Bさん
                                letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                                name = f"{letters[speaker_count % len(letters)]}さん"
                                speaker_mapping[speaker_label] = name
                                speaker_count += 1
                            
                            display_name = speaker_mapping[speaker_label]
                        else:
                            display_name = "不明" # Unknown

                        segments_with_speaker.append({
                            "display_name": display_name,
                            "text": text
                        })

                    # Format Final Text
                    # Aさん: ...
                    # ...
                    # (Break)
                    # Bさん: ...
                    
                    final_lines = []
                    
                    # Group segments by speaker
                    current_speaker = None
                    current_block_text = []
                    
                    for seg in segments_with_speaker:
                        speaker = seg["display_name"]
                        text = seg["text"].strip()
                        

                        if speaker != current_speaker:
                            # Flush current block if any
                            if current_block_text:
                                block_content = "\n".join(current_block_text)
                                block_content = self._add_line_breaks(block_content)
                                
                                final_lines.append(f"{current_speaker}:")
                                final_lines.append(block_content)
                                final_lines.append("") # Empty line between speakers
                            
                            current_speaker = speaker
                            current_block_text = []
                        
                        current_block_text.append(text)
                    

                    # Flush last block
                    if current_block_text:
                        block_content = "\n".join(current_block_text)
                        block_content = self._add_line_breaks(block_content)
                        
                        final_lines.append(f"{current_speaker}:")
                        final_lines.append(block_content)
                    
                    result["text"] = "\n".join(final_lines)
                    print("Diarization applied and text formatted.")
                    
                except Exception as e:
                    print(f"Diarization failed: {e}")
                    # Fallback to original text if diarization fails, BUT still apply line breaks
                    if "segments" in result:
                         text_from_segments = "\n".join([s["text"].strip() for s in result["segments"]])
                         result["text"] = self._add_line_breaks(text_from_segments)
                    else:
                         result["text"] = self._add_line_breaks(result["text"])
            else:
                # No diarization, but still format lines
                # Reconstruct from segments to ensure newlines even if no punctuation
                if "segments" in result:
                    text_from_segments = "\n".join([s["text"].strip() for s in result["segments"]])
                    result["text"] = self._add_line_breaks(text_from_segments)
                else:
                    result["text"] = self._add_line_breaks(result["text"])
                    
        finally:
            sys.stdout = original_stdout

        return result


