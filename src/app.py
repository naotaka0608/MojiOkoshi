import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading
import os
from .transcriber import Transcriber

# Extend CTk with DnD support
class CTkDhD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class App(CTkDhD):
    def __init__(self):
        super().__init__()

        # Theme & Color Setup
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        
        # Window Setup
        self.title("MojiOkoshi - Whisper")
        self.geometry("900x700")
        self.configure(fg_color="#F5F5F7") # Light grey-ish white (Apple style)

        # Fonts
        self.font_title = ("Meiryo UI", 28, "bold")
        self.font_norm = ("Meiryo UI", 14)
        self.font_small = ("Meiryo UI", 12)

        # Layout Grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1) # Text area expands

        # --- Header ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        
        self.logo_label = ctk.CTkLabel(self.header_frame, text="MojiOkoshi AI", font=self.font_title, text_color="#1D1D1F")
        self.logo_label.pack(side="left")

        self.model_var = ctk.StringVar(value="base")
        self.model_combo = ctk.CTkOptionMenu(self.header_frame, variable=self.model_var, 
                                            values=["tiny", "base", "small", "medium", "large"],
                                            width=100, font=self.font_small,
                                            fg_color="#FFFFFF", text_color="#1D1D1F", button_color="#007AFF", button_hover_color="#005ecb")
        self.model_combo.pack(side="right")
        ctk.CTkLabel(self.header_frame, text="Model:", font=self.font_small, text_color="#515154").pack(side="right", padx=10)

        # --- Drop Zone & Controls ---
        self.controls_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E5E5E5")
        self.controls_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=10)
        self.controls_frame.grid_columnconfigure(0, weight=1)

        # Drop Zone Visual
        self.drop_frame = ctk.CTkFrame(self.controls_frame, fg_color="#F5F9FF", corner_radius=10, border_width=2, border_color="#D1E3FF")
        self.drop_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        self.drop_frame.grid_columnconfigure(0, weight=1)
        
        # Drag & Drop Binding
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_file)

        self.drop_label = ctk.CTkLabel(self.drop_frame, text="ここにファイルをドラッグ＆ドロップ\nまたは", 
                                      font=("Meiryo UI", 16), text_color="#6E6E73")
        self.drop_label.pack(pady=(20, 10))

        self.select_file_btn = ctk.CTkButton(self.drop_frame, text="ファイルを選択", command=self.select_file, 
                                            font=self.font_norm, fg_color="#007AFF", hover_color="#005ecb", height=35)
        self.select_file_btn.pack(pady=(0, 20))

        # File Info & Action
        self.file_path_var = tk.StringVar(value="ファイルが選択されていません")
        self.file_label = ctk.CTkLabel(self.controls_frame, textvariable=self.file_path_var, font=self.font_small, text_color="#86868B", wraplength=600)
        self.file_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        self.transcribe_btn = ctk.CTkButton(self.controls_frame, text="文字起こし開始", command=self.start_transcription, state="disabled",
                                           font=("Meiryo UI", 15, "bold"), fg_color="#007AFF", hover_color="#005ecb", height=40, width=200, text_color="white")
        self.transcribe_btn.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="e")

        # Progress
        self.progress_bar = ctk.CTkProgressBar(self.controls_frame, height=10, progress_color="#007AFF", fg_color="#E5E5E5")
        self.progress_bar.grid(row=2, column=0, columnspan=2, padx=0, pady=0, sticky="ew")
        self.progress_bar.set(0)
        
        # --- Result Area ---
        self.result_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.result_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=(20, 30))
        self.result_frame.grid_rowconfigure(0, weight=1)
        self.result_frame.grid_columnconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self.result_frame, font=self.font_norm, corner_radius=10, fg_color="#FFFFFF", text_color="#1D1D1F", border_width=1, border_color="#E5E5E5")
        self.textbox.grid(row=0, column=0, sticky="nsew")
        
        # Footer Action
        self.footer_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.footer_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(self.footer_frame, text="準備完了", font=self.font_small, text_color="#86868B")
        self.status_label.pack(side="left")

        self.save_btn = ctk.CTkButton(self.footer_frame, text="結果を保存", command=self.save_to_file, state="disabled",
                                     font=self.font_norm, fg_color="transparent", border_width=1, border_color="#007AFF", text_color="#007AFF", hover_color="#F0F8FF")
        self.save_btn.pack(side="right")

        # Logic Logic
        self.transcriber = Transcriber()
        self.audio_path = None
        self.is_transcribing = False

    def drop_file(self, event):
        if self.is_transcribing:
            return
        
        file_path = event.data
        if file_path.startswith("{") and file_path.endswith("}"):
            file_path = file_path[1:-1]
        
        if self.validate_file(file_path):
            self.set_file(file_path)
        else:
            self.status_label.configure(text="対応していないファイル形式です", text_color="#FF3B30")

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("音声ファイル", "*.mp3 *.wav *.m4a *.mp4 *.flac")])
        if file_path:
            self.set_file(file_path)

    def validate_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        return ext in [".mp3", ".wav", ".m4a", ".mp4", ".flac"]

    def set_file(self, path):
        self.audio_path = path
        self.file_path_var.set(os.path.basename(path))
        self.transcribe_btn.configure(state="normal")
        self.status_label.configure(text="ファイルが選択されました", text_color="#007AFF")
        self.drop_frame.configure(border_color="#007AFF") # Highlight

    def update_progress_ui(self, progress):
        # Update progress bar and label from thread
        # callback is called from thread, so use after
        self.after(0, lambda p=progress: self._update_progress_safe(p))
    
    def _update_progress_safe(self, progress):
        self.progress_bar.set(progress)
        percentage = int(progress * 100)
        self.status_label.configure(text=f"処理中... {percentage}%", text_color="#007AFF")

    def start_transcription(self):
        if not self.audio_path:
            return
        
        if self.is_transcribing:
            return

        # Check for HF_TOKEN for Diarization
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            # Simple check to see if we should ask. 
            # If the user cancels, we proceed without diarization (token=None)
            dialog = ctk.CTkInputDialog(text="話者分離(Aさん/Bさん)を行うには\nHuggingFace Tokenが必要です。\n(入力しない場合は分離なしで実行します)", title="HF Token")
            hf_token = dialog.get_input()

        self.is_transcribing = True
        self.transcribe_btn.configure(state="disabled")
        self.select_file_btn.configure(state="disabled")
        self.model_combo.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        
        # Start indeterminate until duration calculation is done? 
        # Actually our transcriber calculates duration first.
        # But for model loading it takes time.
        self.progress_bar.set(0)
        
        self.status_label.configure(text="処理中... (モデルロード中)", text_color="#007AFF")
        self.textbox.delete("0.0", "end")

        model_name = self.model_var.get()
        
        # Pass callback
        threading.Thread(target=self.run_transcription, args=(self.audio_path, model_name, hf_token), daemon=True).start()

    def run_transcription(self, audio_path, model_name, hf_token=None):
        try:
            # Pass our update_progress_ui as callback
            result = self.transcriber.transcribe(audio_path, model_name, progress_callback=self.update_progress_ui, hf_token=hf_token)
            self.after(0, self.on_transcription_complete, result)
        except Exception as e:
            self.after(0, self.on_transcription_error, str(e))

    def on_transcription_complete(self, result):
        self.is_transcribing = False
        self.progress_bar.stop()
        self.progress_bar.configure(mode="determinate")
        self.progress_bar.set(1)
        
        self.select_file_btn.configure(state="normal")
        self.transcribe_btn.configure(state="normal")
        self.model_combo.configure(state="normal")
        self.save_btn.configure(state="normal")
        
        self.status_label.configure(text="完了しました (100%)", text_color="#34C759")
        self.textbox.insert("0.0", result["text"])

    def on_transcription_error(self, error_msg):
        self.is_transcribing = False
        self.progress_bar.stop()
        self.progress_bar.set(0)
        
        self.select_file_btn.configure(state="normal")
        self.transcribe_btn.configure(state="normal")
        self.model_combo.configure(state="normal")
        
        self.status_label.configure(text=f"エラーが発生しました", text_color="#FF3B30")
        messagebox.showerror("エラー", error_msg)

    def save_to_file(self):
        text = self.textbox.get("0.0", "end")
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("テキストファイル", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                messagebox.showinfo("保存完了", "ファイルを保存しました")
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました: {e}")
