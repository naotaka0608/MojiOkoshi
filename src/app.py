import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
from .transcriber import Transcriber

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("文字起こし - OpenAI Whisper")
        self.geometry("800x600")

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # Text area expands

        # Title
        self.title_label = ctk.CTkLabel(self, text="文字起こし (Whisper)", font=("Meiryo", 24))
        self.title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        # Controls Frame
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.controls_frame.grid_columnconfigure(1, weight=1)

        # File Selection
        self.file_path_var = tk.StringVar()
        self.select_file_btn = ctk.CTkButton(self.controls_frame, text="ファイルを選択", command=self.select_file)
        self.select_file_btn.grid(row=0, column=0, padx=10, pady=10)
        
        self.file_label = ctk.CTkLabel(self.controls_frame, textvariable=self.file_path_var, wraplength=400)
        self.file_label.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Model Selection
        self.model_var = ctk.StringVar(value="base")
        self.model_option = ctk.CTkOptionMenu(self.controls_frame, variable=self.model_var, 
                                              values=["tiny", "base", "small", "medium", "large"])
        self.model_option.grid(row=0, column=2, padx=10, pady=10)

        # Action Buttons
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        self.action_frame.grid_columnconfigure(0, weight=1)

        self.transcribe_btn = ctk.CTkButton(self.action_frame, text="文字起こし開始", command=self.start_transcription, state="disabled")
        self.transcribe_btn.grid(row=0, column=0, padx=10, pady=10)

        self.save_btn = ctk.CTkButton(self.action_frame, text="保存", command=self.save_to_file, state="disabled")
        self.save_btn.grid(row=0, column=1, padx=10, pady=10)

        # Progress / Status
        self.status_label = ctk.CTkLabel(self.action_frame, text="準備完了", text_color="gray")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=5)

        self.progress_bar = ctk.CTkProgressBar(self.action_frame)
        self.progress_bar.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="ew")
        self.progress_bar.set(0)

        # Text Area
        self.textbox = ctk.CTkTextbox(self, font=("Meiryo", 14))
        self.textbox.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")

        # Transcriber instance
        self.transcriber = Transcriber()
        self.audio_path = None
        self.is_transcribing = False

    def select_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("音声ファイル", "*.mp3 *.wav *.m4a *.mp4 *.flac")])
        if file_path:
            self.audio_path = file_path
            self.file_path_var.set(os.path.basename(file_path))
            self.transcribe_btn.configure(state="normal")
            self.status_label.configure(text="ファイルが選択されました。開始できます。", text_color="white")

    def start_transcription(self):
        if not self.audio_path:
            return
        
        if self.is_transcribing:
            return

        self.is_transcribing = True
        self.transcribe_btn.configure(state="disabled")
        self.select_file_btn.configure(state="disabled")
        self.model_option.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.progress_bar.start()
        self.status_label.configure(text="モデルを読み込み中 & 文字起こし中...", text_color="yellow")
        self.textbox.delete("0.0", "end")

        model_name = self.model_var.get()
        
        # Run in thread
        threading.Thread(target=self.run_transcription, args=(self.audio_path, model_name), daemon=True).start()

    def run_transcription(self, audio_path, model_name):
        try:
            result = self.transcriber.transcribe(audio_path, model_name)
            self.after(0, self.on_transcription_complete, result)
        except Exception as e:
            self.after(0, self.on_transcription_error, str(e))

    def on_transcription_complete(self, result):
        self.is_transcribing = False
        self.progress_bar.stop()
        self.progress_bar.set(1)
        self.select_file_btn.configure(state="normal")
        self.transcribe_btn.configure(state="normal")
        self.model_option.configure(state="normal")
        self.save_btn.configure(state="normal")
        
        self.status_label.configure(text="完了しました！", text_color="green")
        self.textbox.insert("0.0", result["text"])

    def on_transcription_error(self, error_msg):
        self.is_transcribing = False
        self.progress_bar.stop()
        self.select_file_btn.configure(state="normal")
        self.transcribe_btn.configure(state="normal")
        self.model_option.configure(state="normal")
        
        self.status_label.configure(text=f"エラー: {error_msg}", text_color="red")
        messagebox.showerror("エラー", error_msg)

    def save_to_file(self):
        text = self.textbox.get("0.0", "end")
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("テキストファイル", "*.txt")])
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(text)
                messagebox.showinfo("成功", "保存しました！")
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました: {e}")

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
