import PyInstaller.__main__
import os
import shutil

def build():
    print("Building Anki Composer executable for macOS...")
    
    # Clean previous builds if any
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
        
    PyInstaller.__main__.run([
        'main.py',
        '--name=Anki Composer',
        '--windowed',
        '--noconfirm',
        '--clean',
        '--hidden-import=ttkbootstrap',
        # Add pandas and dependencies explicitly if needed, but PyInstaller usually finds them
    ])
    
    print("\nBuild complete! Check the 'dist' folder for 'Anki Composer.app'.")

if __name__ == "__main__":
    build()
