# PDF Text Extractor

A Python utility to extract text from PDF files, including scanned PDFs using OCR.

## Features

- Extract text from regular (text-based) PDFs
- OCR support for scanned PDFs using Tesseract
- **Conservative table data extraction to CSV format**
- **Handles OCR errors gracefully - leaves blank cells for manual entry**
- **Works with any product type, not just Apple products**
- **Table structure analysis with completion statistics**
- **Preserves original raw text for verification**
- Batch processing for multiple PDFs
- Command-line interface
- Save output to files or print to console

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

## Usage

### Command Line Interface

Extract text from a single PDF:
```bash
python pdf_text_extractor.py path/to/document.pdf
```

Save extracted text to a file:
```bash
python pdf_text_extractor.py path/to/document.pdf -o output.txt
```

Process all PDFs in a directory:
```bash
python pdf_text_extractor.py path/to/pdf_directory --batch -o output_directory
```

Disable OCR (text-based PDFs only):
```bash
python pdf_text_extractor.py path/to/document.pdf --no-ocr
```

Extract table data to CSV (auto-names as document.csv):
```bash
python pdf_text_extractor.py path/to/document.pdf --csv
```

Or specify custom output name:
```bash
python pdf_text_extractor.py path/to/document.pdf --csv -o custom_name.csv
```

Analyze table structure:
```bash
python pdf_text_extractor.py path/to/document.pdf --analyze
```

### Python API

```python
from pdf_text_extractor import PDFTextExtractor

# Initialize extractor
extractor = PDFTextExtractor()

# Extract text from a PDF
text = extractor.extract_text_from_pdf('document.pdf')
print(text)

# Save to file
extractor.extract_to_file('document.pdf', 'output.txt')

# Batch process
processed = extractor.batch_extract('pdf_folder', 'output_folder')

# Extract table data to CSV (auto-names as invoice.csv)
extractor.extract_tables_to_csv('invoice.pdf', 'invoice.csv')

# Analyze table structure
analysis = extractor.analyze_table_structure('invoice.pdf')
print(f"Found {analysis['total_rows']} table rows")
```

## Options

- `-o, --output`: Output file or directory path
- `--csv`: Extract table data to CSV format
- `--analyze`: Analyze table structure
- `--no-ocr`: Disable OCR for scanned pages
- `--batch`: Process all PDFs in directory
- `--tesseract-cmd`: Path to tesseract executable
- `-v, --verbose`: Enable verbose logging

## Requirements

- Python 3.6+
- PyMuPDF (fitz)
- pytesseract
- Pillow (PIL)
- Tesseract OCR engine# invoice_parser
