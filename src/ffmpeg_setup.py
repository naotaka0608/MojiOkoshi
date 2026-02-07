import os
import shutil
import sys
from pathlib import Path

def setup_ffmpeg():

    """
    ffmpegがPATHにあるか確認する。ない場合、可能性のある場所を探し、現在のプロセスのPATHに追加する。
    """
    # 0. バンドルされたffmpeg(PyInstaller)を確認
    if getattr(sys, 'frozen', False):
        # PyInstallerバンドル内
        bundle_dir = sys._MEIPASS
        # subprocessがffmpeg.exeを見つけられるようにバンドルディレクトリをPATHに追加
        # これにより、ユーザーがffmpegをインストールしていなくてもアプリが動作します
        os.environ["PATH"] += os.pathsep + bundle_dir
        
    # shutil.which はコマンドが実行可能かどうか（PATHにあるか）を確認します
    if shutil.which("ffmpeg"):
        return True

    print("FFmpeg not found in PATH. Searching known locations...")
    
    # Windowsの一般的な場所（特にWinget）
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if not local_app_data:
        return False
        
    winget_packages = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
    
    if not winget_packages.exists():
        return False

    # wingetパッケージ内のffmpeg.exeの単純な検索
    # "ffmpeg-*-full_build/bin"または同様のパターンを探す
    # WingetでインストールされたffmpegはPATHに追加されていないことがあるため、手動で探します
    try:
        found_ffmpeg = list(winget_packages.rglob("ffmpeg.exe"))
        if found_ffmpeg:
            ffmpeg_path = found_ffmpeg[0].parent
            print(f"Found FFmpeg at: {ffmpeg_path}")
            
            # PATHに追加
            # これでこのプログラム実行中のみ、ffmpegコマンドが使えるようになります
            os.environ["PATH"] += os.pathsep + str(ffmpeg_path)
            
            # 検証
            if shutil.which("ffmpeg"):
                print("FFmpeg successfully added to PATH.")
                return True
    except Exception as e:
        print(f"Error searching for FFmpeg: {e}")

    return False
