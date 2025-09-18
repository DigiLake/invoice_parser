@echo off
REM PDF Text Extractor Setup Script for Windows
REM ============================================

echo PDF Text Extractor - Windows Setup
echo ===================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies
    pause
    exit /b 1
)
echo Python dependencies installed successfully!
echo.

REM Check for Tesseract
echo Checking for Tesseract OCR...
python -c "import pytesseract; pytesseract.get_tesseract_version(); print('Tesseract OCR found!')" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo WARNING: Tesseract OCR is not installed or not in PATH
    echo.
    echo Please install Tesseract OCR from:
    echo https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo After installation, add Tesseract to your PATH or use:
    echo python pdf_text_extractor.py --tesseract-cmd "C:\Program Files\Tesseract-OCR\tesseract.exe"
    echo.
) else (
    echo Tesseract OCR found and working!
)

echo.
echo Setup complete!
echo.
echo Usage examples:
echo   python pdf_text_extractor.py document.pdf
echo   python pdf_text_extractor.py document.pdf -o output.txt
echo   python pdf_text_extractor.py pdf_folder --batch -o output_folder
echo.
pause