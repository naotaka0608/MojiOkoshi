from src.app import App
import customtkinter as ctk
from src.ffmpeg_setup import setup_ffmpeg

import sys
from tkinter import messagebox

if __name__ == "__main__":
    ffmpeg_found = setup_ffmpeg()
    
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    
    if not ffmpeg_found:
        # Schedule warning after main loop starts
        app.after(1000, lambda: messagebox.showwarning("警告", "FFmpegが見つかりませんでした。\nWinget等でインストールされているか確認してください。\n文字起こしが機能しない可能性があります。"))

    app.mainloop()
