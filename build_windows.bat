@echo off
REM Windows Executable Builder for PDF Text Extractor
REM ================================================

echo PDF Text Extractor - Windows Build Script
echo ==========================================
echo.

REM Check if Python is available
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

REM Install build requirements
echo Installing build requirements...
pip install -r requirements-exe.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install build requirements
    pause
    exit /b 1
)
echo.

REM Run the build script
echo Running build script...
python build_exe.py
if %errorlevel% neq 0 (
    echo Error: Build failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
echo.
echo Executable location: dist\pdf-text-extractor.exe
echo Portable package: PDF-Text-Extractor-Portable\
echo.
echo You can now distribute the portable package to other Windows computers.
echo.

REM Test the executable
set /p test="Do you want to test the executable? (y/N): "
if /i "%test%"=="y" (
    echo.
    echo Testing executable...
    dist\pdf-text-extractor.exe --help
    if %errorlevel% equ 0 (
        echo.
        echo ✅ Executable test passed!
    ) else (
        echo.
        echo ❌ Executable test failed!
    )
)

echo.
pause