# 文字起こしアプリ (MojiOkoshi)

OpenAIのWhisperモデルを使用して、音声ファイルを自動的にテキスト化するデスクトップアプリケーションです。
PythonとCustomTkinterで構築された、シンプルでモダンなGUIを備えています。

## 特徴
- **シンプルなUI**: ファイルを選んでボタンを押すだけの簡単操作
- **選べるモデル**: 精度と速度のバランスに応じてモデルサイズ (tiny, base, small, medium, large) を選択可能
- **自動環境設定**: 初回起動時にFFmpegのパスを自動的に検出・設定 (Winget等でインストール済みの場合)
- **進捗表示**: 文字起こしの進行状況をバーで表示

## 前提条件
- Windows (推奨)
- **FFmpeg**: 音声処理に必須です。
    - インストール推奨: `winget install Gyan.FFmpeg`
    - アプリ起動時に自動検出されますが、検出されない場合はPATHへの追加が必要です。

## インストール
このプロジェクトは `uv` を使用して依存関係を管理しています。

```bash
# プロジェクトのクローン
git clone https://github.com/yourusername/MojiOkoshi.git
cd MojiOkoshi

# 依存関係のインストール
uv sync
```

## 使い方
1. アプリを起動します。
   ```powershell
   uv run main.py
   ```
2. **「ファイルを選択」** ボタンで音声ファイル (mp3, wav, m4aなど) を開きます。
3. モデルサイズを選択します (通常は `base` で十分ですが、精度が必要な場合は `small` や `medium` を選んでください)。
4. **「文字起こし開始」** をクリックします。
   - 初回はモデルのダウンロードが行われます。
5. 完了するとテキストが表示されます。 **「保存」** ボタンでテキストファイルとして保存できます。

## 技術スタック
- Python 3.12+
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - UIフレームワーク
- [OpenAI Whisper](https://github.com/openai/whisper) - 音声認識エンジン
- uv - パッケージ管理

## ライセンス
MIT License
