
import PyInstaller.__main__
import os
import shutil
import customtkinter
from PyInstaller.utils.hooks import collect_all

def build():
    # 1. 基本引数の定義
    # PyInstallerに渡す設定を作成します



    args = [
        'main.py',             # 最初に実行されるファイル
        '--name=MojiOkoshi',   # 作成されるexeファイルの名前
        '--onefile',           # すべてを1つのファイルにまとめる（配布しやすくなります）
        '--windowed',          # 実行時に黒い画面（コンソール）を表示しない
        '--clean',             # キャッシュをクリアしてビルド
        '--noconfirm',         # 上書き確認などをしない
    ]

    # 2. CustomTkinterデータを追加
    # CustomTkinterのデザインテーマファイルなどをexeに含める必要があります
    # ctのパスをデータとして追加する必要がある
    ctk_path = os.path.dirname(customtkinter.__file__)
    args.append(f'--add-data={ctk_path}{os.pathsep}customtkinter')

    # 3. TkinterDnD2を追加
    # ドラッグ＆ドロップ機能のためのライブラリを含めます
    # tkinterdnd2のすべてを取得するためにcollect_allを使用
    # しかし、手動でのデータ追加のため、それを見つけることができる。
    # フックに処理させようとするが、失敗することがある。
    # 明示的なデータ追加の方が安全。
    try:
        import tkinterdnd2
        tkdnd_path = os.path.dirname(tkinterdnd2.__file__)
        args.append(f'--add-data={tkdnd_path}{os.pathsep}tkinterdnd2')
        print(f"Adding TkinterDnD2 from: {tkdnd_path}")
    except ImportError:
        print("Warning: tkinterdnd2 not found")

    # 4. ffmpegが見つかれば追加
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print(f"Found ffmpeg at: {ffmpeg_path}")
        # バイナリとして追加。onefileモードではsys._MEIPASSに解凍される
        # アプリがそこでそれを探すようにする必要がある。
        # しかし待てよ、whisperは通常PATHを探す。
        # バンドルする場合、実行時にアプリ内でos.environ["PATH"]に追加する必要がある。
        # 今のところ、とりあえずバンドルしておく。
        args.append(f'--add-binary={ffmpeg_path}{os.pathsep}.')
    else:
        print("Warning: ffmpeg not found on PATH. The executable might not work on machines without ffmpeg.")

    # 5. インポートの接続
    # Whisperは隠しインポートが必要かもしれない
    hidden_imports = [
        'whisper',
        'scipy', 
        'sklearn', # pyannoteで使用される場合（ダイアライゼーションは無効化されているがインポートされている？いや、条件付きインポートだ）
        'sklearn.utils._typedefs', # よくある欠落
        'sklearn.neighbors._partition_nodes',
        'openai',
        'google.generativeai',
        'json',
    ]

    for hidden in hidden_imports:
        args.append(f'--hidden-import={hidden}')

    # 6. Whisperのアセット(mel_filters.npz)を収集
    # 音声認識に必要なデータファイルを含めます
    import whisper
    whisper_path = os.path.dirname(whisper.__file__)
    args.append(f'--add-data={whisper_path}{os.pathsep}whisper')
    print(f"Adding Whisper assets from: {whisper_path}")

    # PyInstallerを実行
    print("Running PyInstaller with args:")
    print(args)
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build()
