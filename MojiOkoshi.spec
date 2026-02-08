# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('C:\\Users\\elast\\AppData\\Local\\Microsoft\\WinGet\\Links\\ffmpeg.EXE', '.')],
    datas=[('C:\\Users\\elast\\Documents\\workspace\\01_program\\python\\claude\\MojiOkoshi\\.venv\\Lib\\site-packages\\customtkinter', 'customtkinter'), ('C:\\Users\\elast\\Documents\\workspace\\01_program\\python\\claude\\MojiOkoshi\\.venv\\Lib\\site-packages\\tkinterdnd2', 'tkinterdnd2'), ('C:\\Users\\elast\\Documents\\workspace\\01_program\\python\\claude\\MojiOkoshi\\.venv\\Lib\\site-packages\\whisper', 'whisper')],
    hiddenimports=['whisper', 'scipy', 'sklearn', 'sklearn.utils._typedefs', 'sklearn.neighbors._partition_nodes', 'openai', 'google.generativeai', 'json'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MojiOkoshi',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
