#!/usr/bin/env python3
"""
Simple build script for Windows executable
"""

import subprocess
import sys
import os

def build_simple_exe():
    """Build a simple executable"""
    print("Building Windows executable (simplified)...")

    try:
        # Install PyInstaller if needed
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

        # Simple build command
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--console",
            "--name", "pdf-text-extractor",
            "pdf_text_extractor.py"
        ]

        print(f"Running: {' '.join(cmd)}")
        subprocess.check_call(cmd)

        if os.path.exists("dist/pdf-text-extractor.exe") or os.path.exists("dist/pdf-text-extractor"):
            print("✅ Build completed successfully!")
            print("📁 Check the 'dist' folder for your executable")
            return True
        else:
            print("❌ Build failed - executable not found")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

if __name__ == "__main__":
    build_simple_exe()