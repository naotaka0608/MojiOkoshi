import whisper
import torch
import os

class Transcriber:
    def __init__(self):
        # モデルとダイアライザー（話者分離用）の初期化
        # self.model はWhisperの音声認識モデルを保持します
        self.model = None
        self.current_model_name = None
        self.diarizer = None

    def load_model(self, model_name="base"):
        if self.model and self.current_model_name == model_name:
            return
            
        print(f"Loading Whisper model: {model_name}...")
        # CUDA（GPU）が使えるか確認します。使える場合はGPUを、使えない場合はCPUを使用します。
        # GPUを使うと処理が非常に高速になります。
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # モデルをメモリに読み込みます。これには少し時間がかかります。
        self.model = whisper.load_model(model_name, device=device)
        self.current_model_name = model_name
        print("Model loaded.")

    def _get_speaker_for_segment(self, start, end, diarization_segments):
        if not diarization_segments:
            return None
            
        # このセグメント範囲内のすべての話者を検索
        speakers = {}
        for seg in diarization_segments:
            # 重なりを確認
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
            
        # 最も長く話している話者を、そのセグメントの話者として採用します
        return max(speakers, key=speakers.get)


    def _add_line_breaks(self, text):
        """
        読点を挿入して読みやすくするために改行を追加する。
        """
        if not text:
            return ""
        
        # 句点と疑問符で改行を適用
        text = text.replace("。", "。\n")
        text = text.replace("?", "?\n") 
        text = text.replace("？", "？\n")
        return text


    def transcribe(self, audio_path, model_name="base", progress_callback=None, text_callback=None, hf_token=None):
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        self.load_model(model_name)
        
        print(f"Transcribing {audio_path}...")
        
        # 進捗バーの表示用に、音声ファイルの長さを計算します
        # whisper.load_audio は音声を読み込んで配列にします（16kHzにリサンプリングされます）
        audio = whisper.load_audio(audio_path)
        duration = len(audio) / 16000 # 16kHzで割って秒数を算出
        print(f"Audio duration: {duration:.2f}s")

        # 進捗を追跡するために詳細出力をキャプチャ
        import sys
        import io
        import re

        class ProgressCapture(io.StringIO):
            def __init__(self, progress_cb, text_cb, duration):
                super().__init__()
                self.progress_cb = progress_cb
                self.text_cb = text_cb
                self.duration = duration
                self.pattern = re.compile(r"\[(\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}\.\d{3})\]\s*(.*)")


            def write(self, text):
                super().write(text)
                if sys.__stdout__:
                    sys.__stdout__.write(text) # 通過させる
                
                # タイムスタンプとテキストを解析
                for match in self.pattern.finditer(text):
                    if self.progress_cb and self.duration > 0:
                        end_time_str = match.group(2)
                        minutes, seconds = end_time_str.split(":")
                        current_seconds = float(minutes) * 60 + float(seconds)
                        progress = min(current_seconds / self.duration, 1.0)
                        self.progress_cb(progress)
                    
                    if self.text_cb:
                        content = match.group(3).strip()
                        if content:
                            self.text_cb(content)

        # 標準出力（print関数の出力先）を一時的に書き換えます to capture progress
        # これにより、Whisperの内部ログから進捗状況を読み取ることができます
        original_stdout = sys.stdout
        
        try:
            if progress_callback or text_callback:
                sys.stdout = ProgressCapture(progress_callback, text_callback, duration)
            
            # ここで実際に文字起こし処理を実行します
            # verbose=True にすることで、進捗がコンソールに出力され、それをキャプチャします
            result = self.model.transcribe(audio_path, verbose=True, fp16=False)
            
            # 文字起こし完了直後に標準出力をリセット
            sys.stdout = original_stdout
            
            # HF_TOKENが利用可能な場合、ダイアライゼーションを実行
            # 注: 渡されたhf_tokenを優先し、次に環境変数を確認する（Diarizer内で確認）
            if hf_token or os.environ.get("HF_TOKEN"):
                try:
                    from .diarizer import SpeakerDiarizer
                    if not self.diarizer:
                        self.diarizer = SpeakerDiarizer(use_auth_token=hf_token)
                    
                    diarization_segments = self.diarizer.diarize(audio_path)
                    
                    # 結果をマージ
                    # 結果の"segments"キーには{start, end, text, ...}のリストが含まれる
                    formatted_text = ""
                    current_speaker = None
                    speaker_mapping = {} # SPEAKER_00をAさん、SPEAKER_01をBさんなどにマッピング
                    speaker_count = 0
                    
                    segments_with_speaker = []
                    
                    for segment in result["segments"]:
                        start = segment["start"]
                        end = segment["end"]
                        text = segment["text"]
                        
                        speaker_label = self._get_speaker_for_segment(start, end, diarization_segments)
                        
                        if speaker_label:
                            if speaker_label not in speaker_mapping:
                                # 簡略化された名前A、B、C...を割り当て
                                # または、必要ならラベルをそのまま使用するが、ユーザーはAさん Bさんを求めていた
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

                    # 最終テキストのフォーマット
                    # Aさん: ...
                    # ...
                    # (Break)
                    # Bさん: ...
                    
                    final_lines = []
                    
                    # 話者ごとにセグメントをグループ化
                    current_speaker = None
                    current_block_text = []
                    
                    for seg in segments_with_speaker:
                        speaker = seg["display_name"]
                        text = seg["text"].strip()
                        

                        if speaker != current_speaker:
                            # 現在のブロックがあればフラッシュ
                            if current_block_text:
                                block_content = "\n".join(current_block_text)
                                block_content = self._add_line_breaks(block_content)
                                
                                final_lines.append(f"{current_speaker}:")
                                final_lines.append(block_content)
                                final_lines.append("") # 話者間の空行
                            
                            current_speaker = speaker
                            current_block_text = []
                        
                        current_block_text.append(text)
                    

                    # 最後のブロックをフラッシュ
                    if current_block_text:
                        block_content = "\n".join(current_block_text)
                        block_content = self._add_line_breaks(block_content)
                        
                        final_lines.append(f"{current_speaker}:")
                        final_lines.append(block_content)
                    
                    result["text"] = "\n".join(final_lines)
                    print("Diarization applied and text formatted.")
                    
                except Exception as e:
                    print(f"Diarization failed: {e}")
                    # ダイアライゼーションが失敗した場合、元のテキストにフォールバックするが、改行は適用する
                    if "segments" in result:
                         text_from_segments = "\n".join([s["text"].strip() for s in result["segments"]])
                         result["text"] = self._add_line_breaks(text_from_segments)
                    else:
                         result["text"] = self._add_line_breaks(result["text"])
            else:
                # ダイアライゼーションなしだが、行のフォーマットは行う
                # 句読点がなくても改行を確実にするためにセグメントから再構築
                if "segments" in result:
                    text_from_segments = "\n".join([s["text"].strip() for s in result["segments"]])
                    result["text"] = self._add_line_breaks(text_from_segments)
                else:
                    result["text"] = self._add_line_breaks(result["text"])
                    
        finally:
            sys.stdout = original_stdout

        return result


