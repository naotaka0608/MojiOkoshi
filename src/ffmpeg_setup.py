import os
import shutil
import sys
from pathlib import Path

def setup_ffmpeg():
    """
    Checks if ffmpeg is in PATH. If not, tries to find it in likely locations
    and adds it to PATH for the current process.
    """
    if shutil.which("ffmpeg"):
        return True

    print("FFmpeg not found in PATH. Searching known locations...")
    
    # Common locations on Windows (especially Winget)
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if not local_app_data:
        return False
        
    winget_packages = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
    
    if not winget_packages.exists():
        return False

    # Naive search for ffmpeg.exe in winget packages
    # We look for "ffmpeg-*-full_build/bin" or similar pattern
    try:
        found_ffmpeg = list(winget_packages.rglob("ffmpeg.exe"))
        if found_ffmpeg:
            ffmpeg_path = found_ffmpeg[0].parent
            print(f"Found FFmpeg at: {ffmpeg_path}")
            
            # Add to PATH
            os.environ["PATH"] += os.pathsep + str(ffmpeg_path)
            
            # Verify
            if shutil.which("ffmpeg"):
                print("FFmpeg successfully added to PATH.")
                return True
    except Exception as e:
        print(f"Error searching for FFmpeg: {e}")

    return False
