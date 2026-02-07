from src.app import App
import customtkinter as ctk

from src.ffmpeg_setup import setup_ffmpeg
from src.gui_utils import patch_subprocess

import sys
from tkinter import messagebox

if __name__ == "__main__":
    # Windowsで黒い画面（コンソール）が出ないようにするためのパッチを適用します
    patch_subprocess()
    
    # FFmpegが使えるか確認し、パスを通します
    # FFmpegは音声ファイルの変換に必要なツールです
    ffmpeg_found = setup_ffmpeg()
    
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = App()
    
    if not ffmpeg_found:
        # メインループ開始後に警告をスケジュール
        app.after(1000, lambda: messagebox.showwarning("警告", "FFmpegが見つかりませんでした。\nWinget等でインストールされているか確認してください。\n文字起こしが機能しない可能性があります。"))

    # アプリのメインループを開始します
    # これによりウィンドウが表示され、ユーザーの操作を受け付ける状態になります
    app.mainloop()
