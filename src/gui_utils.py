
import sys
import subprocess
import os

def patch_subprocess():
    """
    Windows上でコンソールウィンドウなしで実行されることを保証するためにsubprocess.Popenにパッチを適用する。
    これは、'whisper'のようなライブラリが単にsubprocess.run()を呼び出し、黒いウィンドウがポップアップしてしまうため必要である。
    """
    if sys.platform == "win32":
        # フローズンバンドル(PyInstaller)で実行しているか、通常のPythonで実行しているかを確認
        # 実際には、コンソールを抑制したい場合、両方で有用である。
        
        # 元のPopenを保存
        original_popen = subprocess.Popen

        class PopenNoWindow(original_popen):
            def __init__(self, args, **kwargs):
                # creationflagsが指定されていない場合、CREATE_NO_WINDOWに設定する
                # これにより、コマンド実行時に黒い画面が出ないようになります
                if "creationflags" not in kwargs:
                    # CREATE_NO_WINDOW = 0x08000000
                    kwargs["creationflags"] = 0x08000000
                super().__init__(args, **kwargs)

        # パッチを適用
        # これ以降、subprocess.Popen（およびそれを使う関数）はすべて上記のクラスを使います
        subprocess.Popen = PopenNoWindow
        print("Patched subprocess.Popen for no-window execution.")
