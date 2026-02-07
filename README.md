# 文字起こしアプリ (MojiOkoshi)

OpenAIのWhisperモデルを使用して、音声ファイルを自動的にテキスト化するデスクトップアプリケーションです。
PythonとCustomTkinterで構築された、シンプルでモダンなGUIを備えています。

## 特徴

- **シンプルなUI**:
    - ファイルをドラッグ＆ドロップ、またはボタンから選択するだけの簡単操作。
    - 対応形式: `.mp3`, `.wav`, `.m4a`, `.mp4`, `.flac`
- **選べるモデル**: 精度と速度のバランスに応じてモデルサイズを選択可能。
    - `tiny (高速)`
    - `base (標準)`
    - `small (推奨)` - バランスが良い
    - `medium (中精度)`
    - `large (最高精度)`
- **リアルタイム表示**: 文字起こしの進行に合わせてテキストが順次表示されます。
- **自動整形**: 句読点がない場合でも読みやすいように適宜改行を挿入します。
- **ポータブル**: `ffmpeg` を内包した単体実行ファイル (`.exe`) として動作します（Python環境不要）。

## 動作環境

- Windows 10/11 (推奨)
- **インターネット接続**: 初回起動時にAIモデルのダウンロードが必要です。

## 使い方（実行ファイル版）

1. `dist/MojiOkoshi.exe` をダブルクリックして起動します。
    - ※初回は起動に少し時間がかかる場合があります。
    - ※ウィルス対策ソフト等で警告が出る場合がありますが、署名がないためです。
2. 音声ファイルを画面中央のエリアにドラッグ＆ドロップします。
3. 右上のプルダウンからモデルを選択します（最初は `small (推奨)` になっています）。
4. **「文字起こし開始」** をクリックします。
    - 初回利用時はモデルのダウンロードが行われるため、完了まで時間がかかります。
5. 完了するとテキストが表示されます。 **「結果を保存」** ボタンでテキストファイルとして保存できます。

---

## 開発者向け情報

ソースコードから実行する場合の手順です。

### 前提条件

- Python 3.12+
- `uv` (パッケージマネージャー)
- **FFmpeg**: 音声処理に必須です。
    - インストール推奨: `winget install Gyan.FFmpeg`
    - アプリ起動時に自動検出されますが、検出されない場合はPATHへの追加が必要です。

### インストール

```bash
# プロジェクトのクローン
git clone https://github.com/yourusername/MojiOkoshi.git
cd MojiOkoshi

# 依存関係のインストール
uv sync
```

### 実行

```powershell
uv run main.py
```

### ビルド（exe化）

`pyinstaller` を使用して単体実行ファイルを作成します。

```powershell
uv run build_exe.py
```
`dist/` フォルダに実行ファイルが生成されます。

## 技術スタック

- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - UIフレームワーク
- [OpenAI Whisper](https://github.com/openai/whisper) - 音声認識エンジン
- [TkinterDnD2](https://github.com/pmgagne/tkinterdnd2) - ドラッグ＆ドロップ対応
- uv - パッケージ管理
- PyInstaller - 実行ファイル化

## ライセンス

MIT License
