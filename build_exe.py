#!/usr/bin/env python3
"""
Build script to create Windows executable for PDF Text Extractor
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("PyInstaller already installed")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("Failed to install PyInstaller")
            return False

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pdf_text_extractor.py'],
    pathex=[],
    binaries=[],
    datas=[('table_parser.py', '.'), ('requirements.txt', '.')],
    hiddenimports=['PIL._tkinter_finder'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pdf-text-extractor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''

    with open('pdf_extractor.spec', 'w') as f:
        f.write(spec_content)
    print("Created PyInstaller spec file")

def build_executable():
    """Build the Windows executable"""
    print("Building Windows executable...")

    # Clean previous builds
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("Cleaned previous build directory")

    if os.path.exists('dist'):
        shutil.rmtree('dist')
        print("Cleaned previous dist directory")

    try:
        # Build using spec file
        subprocess.check_call([
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            'pdf_extractor.spec'
        ])

        if os.path.exists('dist/pdf-text-extractor.exe'):
            print("✅ Executable built successfully!")
            print(f"Location: {os.path.abspath('dist/pdf-text-extractor.exe')}")

            # Get file size
            size = os.path.getsize('dist/pdf-text-extractor.exe') / (1024 * 1024)
            print(f"Size: {size:.1f} MB")

            return True
        else:
            print("❌ Executable not found after build")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_portable_package():
    """Create a portable package with the executable"""
    if not os.path.exists('dist/pdf-text-extractor.exe'):
        print("Executable not found")
        return False

    # Create portable package directory
    package_dir = 'PDF-Text-Extractor-Portable'
    if os.path.exists(package_dir):
        shutil.rmtree(package_dir)

    os.makedirs(package_dir)

    # Copy executable
    shutil.copy2('dist/pdf-text-extractor.exe', package_dir)

    # Create README for Windows users
    readme_content = '''# PDF Text Extractor - Portable Windows Version

## Usage

1. Place your PDF files in the same folder as this executable
2. Open Command Prompt or PowerShell in this folder
3. Run commands:

### Extract table data to CSV:
```cmd
pdf-text-extractor.exe "your-invoice.pdf" --csv
```

### Analyze table structure:
```cmd
pdf-text-extractor.exe "your-invoice.pdf" --analyze
```

### Extract all text:
```cmd
pdf-text-extractor.exe "your-invoice.pdf" -o output.txt
```

## Requirements

- Windows 10 or later
- Tesseract OCR (for scanned PDFs)

## Install Tesseract OCR

1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to default location (C:\\Program Files\\Tesseract-OCR)
3. Or specify path: `pdf-text-extractor.exe --tesseract-cmd "C:\\path\\to\\tesseract.exe"`

## Output

- CSV files are created in the same folder
- Empty cells in CSV can be filled manually in Excel
- Raw text is preserved for verification

## Features

- Extracts table data from invoices, receipts, reports
- Handles OCR errors gracefully
- Works with any product type (not just Apple)
- Conservative extraction - no data guessing

Built with Python and packaged for Windows convenience.
'''

    with open(f'{package_dir}/README.txt', 'w', encoding='utf-8') as f:
        f.write(readme_content)

    # Create batch file for easy usage
    batch_content = '''@echo off
echo PDF Text Extractor - Windows Portable
echo =====================================
echo.
echo Usage examples:
echo   pdf-text-extractor.exe "invoice.pdf" --csv
echo   pdf-text-extractor.exe "invoice.pdf" --analyze
echo.
echo Place your PDF files in this folder, then run:
set /p filename="Enter PDF filename (or drag and drop): "
if "%filename%"=="" (
    echo No file specified
    pause
    exit /b
)

echo.
echo Choose operation:
echo 1. Extract table to CSV
echo 2. Analyze table structure
echo 3. Extract all text
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" (
    pdf-text-extractor.exe %filename% --csv
) else if "%choice%"=="2" (
    pdf-text-extractor.exe %filename% --analyze
) else if "%choice%"=="3" (
    pdf-text-extractor.exe %filename% -o output.txt
) else (
    echo Invalid choice
)

echo.
pause
'''

    with open(f'{package_dir}/run.bat', 'w') as f:
        f.write(batch_content)

    print(f"✅ Portable package created: {package_dir}/")
    return True

def main():
    """Main build process"""
    print("PDF Text Extractor - Windows Executable Builder")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists('pdf_text_extractor.py'):
        print("❌ pdf_text_extractor.py not found. Run this script from the project directory.")
        return False

    # Step 1: Install PyInstaller
    if not install_pyinstaller():
        return False

    # Step 2: Create spec file
    create_spec_file()

    # Step 3: Build executable
    if not build_executable():
        return False

    # Step 4: Create portable package
    if not create_portable_package():
        return False

    print("\n🎉 Build completed successfully!")
    print(f"Executable: dist/pdf-text-extractor.exe")
    print(f"Portable package: PDF-Text-Extractor-Portable/")
    print("\nYou can distribute the portable package to Windows users.")

    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)