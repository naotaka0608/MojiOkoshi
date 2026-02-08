import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinterdnd2 import TkinterDnD, DND_FILES
import threading
import os
import json
import time # sleep用

from .transcriber import Transcriber
from .summarizer import SimpleSummarizer
from .config_manager import ConfigManager
from .llm_summarizer import LocalLLMSummarizer
from .gemini_summarizer import GeminiSummarizer

# CTkをDnDサポートで拡張（変更なし）
class CTkDhD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        self.title("設定")
        self.geometry("500x500")
        self.resizable(False, False)
        
        # モーダルにする
        self.transient(parent)
        self.grab_set()
        
        self.layout()
        
    def layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # タイトル
        ctk.CTkLabel(self, text="設定", font=("Meiryo UI", 20, "bold")).pack(pady=10)
        
        # タブ
        tabview = ctk.CTkTabview(self)
        tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        tab_general = tabview.add("全般")
        tab_local = tabview.add("ローカルLLM")
        tab_gemini = tabview.add("Gemini")

        llm_config = self.config_manager.get("local_llm", {})
        
        # 内部的に保持するための変数（隠しフィールド的に使う）
        self.llm_url = llm_config.get("url", "http://localhost:11434/v1")
        self.llm_api_key = llm_config.get("api_key", "ollama")

        # モデル取得ボタン (再追加)
        ctk.CTkButton(tab_local, text="モデル一覧を更新", command=self.fetch_models, width=150, height=30, fg_color="#5E5CE6").pack(pady=(10, 5), anchor="w")
        
        ctk.CTkLabel(tab_local, text="モデルを選択:", font=("Meiryo UI", 12)).pack(pady=5, anchor="w")
        
        # コンボボックス
        current_model = llm_config.get("model", "llama3")
        self.llm_model_var = ctk.StringVar(value=current_model)
        
        # 保存されているモデルリストがあればそれを使う
        saved_models = llm_config.get("available_models", [])
        if not saved_models:
            saved_models = [current_model]
        
        # 現在のモデルがリストになければ追加
        if current_model not in saved_models:
            saved_models.append(current_model)
            
        self.llm_model_combo = ctk.CTkComboBox(tab_local, variable=self.llm_model_var, values=saved_models, width=300)
        self.llm_model_combo.pack(pady=2, anchor="w")

        # --- Gemini ---
        gemini_config = self.config_manager.get("gemini", {})
        
        ctk.CTkLabel(tab_gemini, text="APIキー:", font=("Meiryo UI", 12)).pack(pady=5, anchor="w")
        self.gemini_key_entry = ctk.CTkEntry(tab_gemini, width=300, show="*")
        self.gemini_key_entry.insert(0, gemini_config.get("api_key", ""))
        self.gemini_key_entry.pack(pady=2, anchor="w")
        
        ctk.CTkLabel(tab_gemini, text="モデル名:", font=("Meiryo UI", 12)).pack(pady=5, anchor="w")
        self.gemini_model_entry = ctk.CTkEntry(tab_gemini, width=300)
        self.gemini_model_entry.insert(0, gemini_config.get("model", "gemini-pro"))
        self.gemini_model_entry.pack(pady=2, anchor="w")

        # 保存ボタン
        ctk.CTkButton(self, text="保存して閉じる", command=self.save_settings, fg_color="#007AFF").pack(pady=20)

    def fetch_models(self):
        url = self.llm_url
        api_key = self.llm_api_key
        
        try:
            # 一時的にクライアントを作成してロード
            temp_llm = LocalLLMSummarizer(base_url=url, api_key=api_key)
            models = temp_llm.get_models()
            
            if models:
                self.llm_model_combo.configure(values=models)
                # モデルが見つかったら、現在選択中のモデルがその中にあるか確認
                current = self.llm_model_var.get()
                if current not in models:
                    self.llm_model_combo.set(models[0])
                messagebox.showinfo("成功", f"{len(models)}個のモデルを取得しました。")
            else:
                messagebox.showwarning("警告", "モデルが見つかりませんでした。")
        except Exception as e:
            messagebox.showerror("エラー", f"モデルの取得に失敗しました: {e}")

    def save_settings(self):
        # モデルリストも保存しておく（次回起動時のため）
        current_models = self.llm_model_combo._values
        
        self.config_manager.set("local_llm", {
            "enabled": True,
            "url": self.llm_url,     # 隠しフィールドから保存
            "model": self.llm_model_combo.get(),
            "api_key": self.llm_api_key, # 隠しフィールドから保存
            "available_models": current_models # リストを保存
        })
        
        self.config_manager.set("gemini", {
            "enabled": True,
            "api_key": self.gemini_key_entry.get(),
            "model": self.gemini_model_entry.get()
        })
        
        messagebox.showinfo("設定", "設定を保存しました。")
        self.destroy()


class App(CTkDhD):
    def __init__(self):
        super().__init__()

        # 設定管理
        self.config_manager = ConfigManager()

        # テーマ＆カラー設定
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")
        
        # ウィンドウ設定
        self.title("MojiOkoshi")
        self.geometry("1000x800") # 少し広げる
        self.configure(fg_color="#F5F5F7")

        # フォント
        self.font_title = ("Meiryo UI", 28, "bold")
        self.font_norm = ("Meiryo UI", 14)
        self.font_small = ("Meiryo UI", 12)

        # レイアウトグリッド
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- ヘッダー ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        
        self.logo_label = ctk.CTkLabel(self.header_frame, text="文字おこし AI", font=self.font_title, text_color="#1D1D1F")
        self.logo_label.pack(side="left")

        # 設定ボタン
        self.settings_btn = ctk.CTkButton(self.header_frame, text="設定", width=60, height=24, font=self.font_small,
                                         fg_color="#E5E5E5", text_color="#1D1D1F", hover_color="#D1D1D6",
                                         command=self.open_settings)
        self.settings_btn.pack(side="right", padx=(10, 0))

        self.model_var = ctk.StringVar(value="small (推奨)")
        self.model_combo = ctk.CTkOptionMenu(self.header_frame, variable=self.model_var, 
                                            values=["tiny (高速)", "base (標準)", "small (推奨)", "medium (中精度)", "large (最高精度)"],
                                            width=140, font=self.font_small,
                                            fg_color="#FFFFFF", text_color="#1D1D1F", button_color="#007AFF", button_hover_color="#005ecb")
        self.model_combo.pack(side="right")
        ctk.CTkLabel(self.header_frame, text="Whisperモデル:", font=self.font_small, text_color="#515154").pack(side="right", padx=5)

        # --- ドロップゾーン＆コントロール ---
        # (ここはあまり変えない)
        self.controls_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=15, border_width=1, border_color="#E5E5E5")
        self.controls_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=10)
        self.controls_frame.grid_columnconfigure(0, weight=1)

        # ドロップゾーン
        self.drop_frame = ctk.CTkFrame(self.controls_frame, fg_color="#F5F9FF", corner_radius=10, border_width=2, border_color="#D1E3FF")
        self.drop_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        self.drop_frame.grid_columnconfigure(0, weight=1)
        
        self.drop_target_register(DND_FILES)
        self.dnd_bind('<<Drop>>', self.drop_file)

        self.drop_label = ctk.CTkLabel(self.drop_frame, text="ここにファイルをドラッグ＆ドロップ\nまたは", 
                                      font=("Meiryo UI", 16), text_color="#6E6E73")
        self.drop_label.pack(pady=(20, 5))
        
        self.support_label = ctk.CTkLabel(self.drop_frame, text="対応形式: .mp3 .wav .m4a .mp4 .flac", 
                                      font=("Meiryo UI", 12), text_color="#8E8E93")
        self.support_label.pack(pady=(0, 10))

        self.select_file_btn = ctk.CTkButton(self.drop_frame, text="ファイルを選択", command=self.select_file, 
                                            font=self.font_norm, fg_color="#007AFF", hover_color="#005ecb", height=35)
        self.select_file_btn.pack(pady=(0, 20))

        # ファイル情報
        self.file_path_var = tk.StringVar(value="ファイルが選択されていません")
        self.file_label = ctk.CTkLabel(self.controls_frame, textvariable=self.file_path_var, font=self.font_small, text_color="#86868B", wraplength=600)
        self.file_label.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="w")

        self.transcribe_btn = ctk.CTkButton(self.controls_frame, text="文字起こし開始", command=self.start_transcription, state="disabled",
                                           font=("Meiryo UI", 15, "bold"), fg_color="#007AFF", hover_color="#005ecb", height=40, width=200, text_color="white")
        self.transcribe_btn.grid(row=1, column=1, padx=20, pady=(0, 20), sticky="e")

        # 進捗
        self.progress_bar = ctk.CTkProgressBar(self.controls_frame, height=10, progress_color="#007AFF", fg_color="#E5E5E5")
        self.progress_bar.grid(row=2, column=0, columnspan=2, padx=0, pady=0, sticky="ew")
        self.progress_bar.set(0)
        
        # --- 結果エリア (タブ化) ---
        self.result_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.result_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=(10, 20))
        self.result_frame.grid_rowconfigure(0, weight=1)
        self.result_frame.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self.result_frame, fg_color="transparent")
        self.tabview.grid(row=0, column=0, sticky="nsew")
        
        self.tabview.add("文字起こし")
        self.tabview.add("簡易要約")
        self.tabview.add("ローカルLLM")
        # self.tabview.add("Gemini") # Geminiは非表示（コードは残す）
        
        # 各タブのテキストボックス
        self.text_widgets = {}
        for tab_name in ["文字起こし", "簡易要約", "ローカルLLM"]: # Gemini除外
            textbox = ctk.CTkTextbox(self.tabview.tab(tab_name), font=self.font_norm, corner_radius=10, fg_color="#FFFFFF", text_color="#1D1D1F", border_width=1, border_color="#E5E5E5")
            textbox.pack(expand=True, fill="both")
            self.text_widgets[tab_name] = textbox
            
        # Gemini用のウィジェットは作成しないが、辞書には入れておく（保存ロジック等のため）
        # ただし、保存時にエラーにならないようにハンドリングが必要
        # ここではNoneを入れておくか、あるいは非表示のTabを作成するか。
        # CTkTabviewはaddしないとtab()が呼べない。
        # なので、保存ロジック側で "Gemini" キーがない場合を考慮するように修正する。
        
        # フッターアクション
        self.footer_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.footer_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(self.footer_frame, text="準備完了", font=self.font_small, text_color="#86868B")
        self.status_label.pack(side="left")

        self.save_btn = ctk.CTkButton(self.footer_frame, text="結果を保存", command=self.save_to_file, state="disabled",
                                     font=self.font_norm, fg_color="transparent", border_width=1, border_color="#007AFF", text_color="#007AFF", hover_color="#F0F8FF")
        self.save_btn.pack(side="right")
        
        # 要約生成ボタン（アクティブなタブによって挙動を変えるか、プルダウンにするか）
        # ここでは「現在開いている要約タブ」に対して生成を行う形にします
        self.summarize_btn = ctk.CTkButton(self.footer_frame, text="要約を作成", command=self.generate_summary, state="disabled",
                                     font=self.font_norm, fg_color="#34C759", hover_color="#2da84e", text_color="white", width=120)
        self.summarize_btn.pack(side="right", padx=10)

        # ロジック
        self.transcriber = Transcriber()
        self.simple_summarizer = SimpleSummarizer()
        
        # LLM系は都度初期化するか、キャッシュするか。
        # 設定が変わる可能性があるので、生成時にConfigから読み込んで初期化する方が安全
        self.audio_path = None
        self.is_transcribing = False

    def open_settings(self):
        SettingsDialog(self, self.config_manager)

    def drop_file(self, event):
        if self.is_transcribing: return
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
        self.drop_frame.configure(border_color="#007AFF")

    def update_progress_ui(self, progress):
        self.after(0, lambda p=progress: self._update_progress_safe(p))
    
    def _update_progress_safe(self, progress):
        self.progress_bar.set(progress)
        percentage = int(progress * 100)
        self.status_label.configure(text=f"処理中... {percentage}%", text_color="#007AFF")

    def update_text_ui(self, text):
        self.after(0, lambda t=text: self._append_text_safe(t))

    def _append_text_safe(self, text):
        self.text_widgets["文字起こし"].insert("end", text + "\n")
        self.text_widgets["文字起こし"].see("end")

    def start_transcription(self):
        if not self.audio_path or self.is_transcribing: return
        
        hf_token = None # 必要なら環境変数or設定から
        
        self.is_transcribing = True
        self.transcribe_btn.configure(state="disabled")
        self.select_file_btn.configure(state="disabled")
        self.model_combo.configure(state="disabled")
        self.save_btn.configure(state="disabled")
        self.summarize_btn.configure(state="disabled")
        
        self.progress_bar.set(0)
        self.status_label.configure(text="モデルロード中...", text_color="#007AFF")
        
        for k in self.text_widgets:
            self.text_widgets[k].delete("0.0", "end")
            
        model_name = self.model_var.get().split()[0]
        threading.Thread(target=self.run_transcription, args=(self.audio_path, model_name, hf_token), daemon=True).start()

    def run_transcription(self, audio_path, model_name, hf_token=None):
        try:
            result = self.transcriber.transcribe(
                audio_path, model_name, 
                progress_callback=self.update_progress_ui, 
                text_callback=self.update_text_ui,
                hf_token=hf_token
            )
            self.after(0, self.on_transcription_complete, result)
        except Exception as e:
            self.after(0, self.on_transcription_error, str(e))

    def on_transcription_complete(self, result):
        self.is_transcribing = False
        self.progress_bar.stop()
        self.progress_bar.set(1)
        self.select_file_btn.configure(state="normal")
        self.transcribe_btn.configure(state="normal")
        self.model_combo.configure(state="normal")
        self.save_btn.configure(state="normal")
        self.summarize_btn.configure(state="normal")
        self.status_label.configure(text="完了しました (100%)", text_color="#34C759")
        self.text_widgets["文字起こし"].delete("0.0", "end")
        self.text_widgets["文字起こし"].insert("0.0", result["text"])

    def on_transcription_error(self, error_msg):
        self.is_transcribing = False
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.select_file_btn.configure(state="normal")
        self.transcribe_btn.configure(state="normal")
        self.model_combo.configure(state="normal")
        self.status_label.configure(text=f"エラーが発生しました", text_color="#FF3B30")
        messagebox.showerror("エラー", error_msg)

    def generate_summary(self):
        # 現在のタブを確認
        original_text = self.text_widgets["文字起こし"].get("0.0", "end").strip()
        if not original_text:
            messagebox.showwarning("警告", "文字起こしテキストが空です")
            return
            
        current_tab = self.tabview.get()
        
        if current_tab == "文字起こし":
            messagebox.showinfo("案内", "要約を作成したいタブ（簡易要約、ローカルLLM）を選択してからボタンを押してください。")
            return

        self.status_label.configure(text=f"{current_tab}を作成中...", text_color="#007AFF")
        self.summarize_btn.configure(state="disabled")
        self.update_idletasks()
        
        target_widget = self.text_widgets[current_tab]
        target_widget.delete("0.0", "end")
        
        threading.Thread(target=self._run_summarization_thread, args=(current_tab, original_text), daemon=True).start()

    def _run_summarization_thread(self, mode, text):
        summary = ""
        try:
            if mode == "簡易要約":
                summary = self.simple_summarizer.summarize(text)
            elif mode == "ローカルLLM":
                config = self.config_manager.get("local_llm", {})
                llm = LocalLLMSummarizer(
                    base_url=config.get("url"),
                    api_key=config.get("api_key"),
                    model=config.get("model")
                )
                
                # ストリーミング用コールバック
                def stream_callback(chunk):
                    self.after(0, self._append_summary_chunk, mode, chunk)
                    
                summary = llm.summarize(text, stream_callback=stream_callback)
            elif mode == "Gemini":
                config = self.config_manager.get("gemini", {})
                gemini = GeminiSummarizer(
                    api_key=config.get("api_key"),
                    model=config.get("model")
                )
                summary = gemini.summarize(text)
                
            self.after(0, self._on_summary_complete, mode, summary)
            
        except Exception as e:
            self.after(0, self._on_summary_error, str(e))

    def _append_summary_chunk(self, mode, chunk):
        self.text_widgets[mode].insert("end", chunk)
        self.text_widgets[mode].see("end")

    def _on_summary_complete(self, mode, summary):
        self.summarize_btn.configure(state="normal")
        self.status_label.configure(text=f"{mode}が完了しました", text_color="#34C759")
        self.text_widgets[mode].insert("0.0", summary)

    def _on_summary_error(self, error_msg):
        self.summarize_btn.configure(state="normal")
        self.status_label.configure(text="要約に失敗しました", text_color="#FF3B30")
        messagebox.showerror("エラー", f"要約エラー: {error_msg}")

    def save_to_file(self):
        # ユーザー要望によりJSON形式のみとする
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSONファイル", "*.json")])
            
        if not file_path: return

        try:
            full_data = {
                "original": self.text_widgets["文字起こし"].get("0.0", "end"),
                "simple_summary": self.text_widgets["簡易要約"].get("0.0", "end"),
                "local_summary": self.text_widgets["ローカルLLM"].get("0.0", "end"),
                "gemini_summary": "" # 非表示のため空文字
            }
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(full_data, f, indent=4, ensure_ascii=False)
                    
            messagebox.showinfo("保存完了", "ファイルを保存しました")
        except Exception as e:
            messagebox.showerror("エラー", f"保存に失敗しました: {e}")
