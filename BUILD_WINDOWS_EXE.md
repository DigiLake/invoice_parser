# Building Windows Executable

This guide shows how to create a standalone Windows executable (.exe) for the PDF Text Extractor.

## Prerequisites

- **Windows 10 or later**
- **Python 3.8+** installed from [python.org](https://python.org)
- **Git** (optional, for cloning the repository)

## Quick Build (Automated)

### Method 1: Using Batch Script

1. **Open Command Prompt** in the project directory
2. **Run the build script:**
   ```cmd
   build_windows.bat
   ```
3. **Wait for completion** - takes 2-5 minutes
4. **Find your executable** in `dist/pdf-text-extractor.exe`

### Method 2: Using Python Script

```cmd
python build_exe.py
```

## Manual Build Steps

### 1. Install Build Dependencies

```cmd
pip install -r requirements-exe.txt
```

### 2. Build Executable

```cmd
python -m PyInstaller --clean --onefile --console pdf_text_extractor.py --name pdf-text-extractor --add-data "table_parser.py;." --add-data "requirements.txt;."
```

### 3. Test Executable

```cmd
dist\pdf-text-extractor.exe --help
```

## Output

After successful build, you'll have:

- **`dist/pdf-text-extractor.exe`** - The standalone executable (~50MB)
- **`PDF-Text-Extractor-Portable/`** - Ready-to-distribute package with:
  - `pdf-text-extractor.exe` - Main executable
  - `run.bat` - User-friendly batch script
  - `README.txt` - Instructions for end users

## Usage of Executable

### Command Line

```cmd
# Extract table to CSV
pdf-text-extractor.exe "invoice.pdf" --csv

# Analyze table structure
pdf-text-extractor.exe "invoice.pdf" --analyze

# Extract all text
pdf-text-extractor.exe "invoice.pdf" -o output.txt
```

### Using the Batch File

1. Double-click `run.bat`
2. Follow the interactive prompts
3. Drag and drop PDF files when prompted

## Distribution

The portable package (`PDF-Text-Extractor-Portable/`) can be:

- **Zipped and shared** - Users just extract and run
- **Copied to USB drives** - Runs without installation
- **Deployed in corporate environments** - No admin rights needed

## Requirements for End Users

- **Windows 10 or later**
- **Tesseract OCR** (for scanned PDFs):
  - Download from: https://github.com/UB-Mannheim/tesseract/wiki
  - Install to default location: `C:\Program Files\Tesseract-OCR\`
  - Or specify custom path: `--tesseract-cmd "C:\path\to\tesseract.exe"`

## Troubleshooting

### Build Issues

**Error: "PyInstaller not found"**
```cmd
pip install pyinstaller
```

**Error: "Module not found"**
```cmd
pip install -r requirements-exe.txt
```

**Error: "Permission denied"**
- Run Command Prompt as Administrator
- Or build in a folder you have write access to

### Runtime Issues

**Error: "Tesseract not found"**
- Install Tesseract OCR for Windows
- Or use: `--tesseract-cmd "C:\path\to\tesseract.exe"`

**Error: "No module named..."**
- The executable should be self-contained
- Try rebuilding with `--clean` flag

### Performance Notes

- **First run** may be slower (Windows Defender scan)
- **File size** is ~50MB (includes Python + all dependencies)
- **Memory usage** is ~100-200MB during processing
- **OCR processing** takes 2-10 seconds per page

## Advanced Options

### Custom Icon

Add to build script:
```python
exe = EXE(..., icon='icon.ico')
```

### Hidden Console

Change in spec file:
```python
exe = EXE(..., console=False, ...)
```

### Version Information

Add version info to spec file:
```python
exe = EXE(..., version='version.txt', ...)
```

## Security

The executable is built from open source code and includes:
- **No network access** - Works completely offline
- **No registry changes** - Portable application
- **No system modifications** - Safe to run

Some antivirus software may flag PyInstaller executables as suspicious. This is a false positive common with Python-based executables.