
import os
import sys
import tkinter as tk
import customtkinter as ctk
from src.app import App

def test_manual_launch():
    """
    の手動テスト用スクリプト
    アプリを起動し、以下の機能を確認するためのもの
    1. 設定画面が開くか (APIキー等の保存・読み込み)
    2. タブが4つあるか
    3. 各要約機能が動作するか（モックデータ等は使わず、実際のAPI/LocalLLMに接続を試みる）
    """
    print("Launching App for Manual Verification...")
    
    app = App()
    app.mainloop()

if __name__ == "__main__":
    test_manual_launch()
