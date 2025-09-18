# PDF Text Extractor Makefile
# Cross-platform support for Linux/macOS/Windows

# Detect operating system
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
    PYTHON := python
    PIP := pip
    RM := del /Q
    MKDIR := mkdir
    TESSERACT_INSTALL := @echo "Please install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki"
else
    DETECTED_OS := $(shell uname -s)
    PYTHON := python3
    PIP := pip3
    RM := rm -f
    MKDIR := mkdir -p
    ifeq ($(DETECTED_OS),Darwin)
        TESSERACT_INSTALL := brew install tesseract
    else ifeq ($(DETECTED_OS),Linux)
        TESSERACT_INSTALL := sudo apt-get update && sudo apt-get install -y tesseract-ocr
    else
        TESSERACT_INSTALL := @echo "Please install Tesseract OCR for your system"
    endif
endif

# Default target
.PHONY: all
all: setup

# Help target
.PHONY: help
help:
	@echo "PDF Text Extractor - Makefile Help"
	@echo "=================================="
	@echo ""
	@echo "Available targets:"
	@echo "  help           - Show this help message"
	@echo "  setup          - Complete setup (install dependencies + tesseract)"
	@echo "  install        - Install Python dependencies"
	@echo "  install-tesseract - Install Tesseract OCR"
	@echo "  test           - Test the utility"
	@echo "  demo           - Run demo with help command"
	@echo "  clean          - Clean temporary files"
	@echo "  check-deps     - Check if dependencies are installed"
	@echo "  extract-csv    - Extract table data to CSV"
	@echo "  analyze        - Analyze table structure"
	@echo "  build-exe      - Build Windows executable (Windows only)"
	@echo ""
	@echo "Usage examples:"
	@echo "  make setup                    - Setup everything"
	@echo "  make extract FILE=doc.pdf     - Extract text from specific file"
	@echo "  make extract-csv FILE=doc.pdf - Extract table to doc.csv"
	@echo "  make analyze FILE=doc.pdf     - Analyze table structure"
	@echo "  make batch DIR=pdf_folder     - Process all PDFs in directory"
	@echo ""
	@echo "Detected OS: $(DETECTED_OS)"

# Complete setup
.PHONY: setup
setup: install install-tesseract check-deps
	@echo "Setup complete! You can now use the PDF text extractor."

# Install Python dependencies
.PHONY: install
install:
	@echo "Installing Python dependencies..."
	$(PIP) install -r requirements.txt

# Install Tesseract OCR
.PHONY: install-tesseract
install-tesseract:
	@echo "Installing Tesseract OCR for $(DETECTED_OS)..."
	$(TESSERACT_INSTALL)

# Check if dependencies are installed
.PHONY: check-deps
check-deps:
	@echo "Checking dependencies..."
	@$(PYTHON) -c "import fitz; print('✓ PyMuPDF installed')" || echo "✗ PyMuPDF missing"
	@$(PYTHON) -c "import pytesseract; print('✓ pytesseract installed')" || echo "✗ pytesseract missing"
	@$(PYTHON) -c "import PIL; print('✓ Pillow installed')" || echo "✗ Pillow missing"
	@$(PYTHON) -c "import pytesseract; pytesseract.get_tesseract_version(); print('✓ Tesseract OCR available')" || echo "✗ Tesseract OCR missing or not in PATH"

# Test the utility
.PHONY: test
test:
	@echo "Testing PDF text extractor..."
	$(PYTHON) pdf_text_extractor.py --help

# Demo - show help
.PHONY: demo
demo:
	@echo "PDF Text Extractor Demo"
	@echo "======================"
	$(PYTHON) pdf_text_extractor.py --help

# Extract text from a specific file
.PHONY: extract
extract:
ifndef FILE
	@echo "Usage: make extract FILE=path/to/document.pdf [OUTPUT=output.txt]"
	@exit 1
endif
ifdef OUTPUT
	$(PYTHON) pdf_text_extractor.py "$(FILE)" -o "$(OUTPUT)"
else
	$(PYTHON) pdf_text_extractor.py "$(FILE)"
endif

# Batch process PDFs in a directory
.PHONY: batch
batch:
ifndef DIR
	@echo "Usage: make batch DIR=path/to/pdf_directory [OUTPUT=output_directory]"
	@exit 1
endif
ifdef OUTPUT
	$(PYTHON) pdf_text_extractor.py "$(DIR)" --batch -o "$(OUTPUT)"
else
	$(PYTHON) pdf_text_extractor.py "$(DIR)" --batch
endif

# Extract without OCR
.PHONY: extract-no-ocr
extract-no-ocr:
ifndef FILE
	@echo "Usage: make extract-no-ocr FILE=path/to/document.pdf [OUTPUT=output.txt]"
	@exit 1
endif
ifdef OUTPUT
	$(PYTHON) pdf_text_extractor.py "$(FILE)" --no-ocr -o "$(OUTPUT)"
else
	$(PYTHON) pdf_text_extractor.py "$(FILE)" --no-ocr
endif

# Extract table data to CSV
.PHONY: extract-csv
extract-csv:
ifndef FILE
	@echo "Usage: make extract-csv FILE=path/to/document.pdf"
	@echo "       Automatically creates filename.csv from input PDF"
	@exit 1
endif
ifdef OUTPUT
	$(PYTHON) pdf_text_extractor.py "$(FILE)" --csv -o "$(OUTPUT)"
else
	$(PYTHON) pdf_text_extractor.py "$(FILE)" --csv
endif

# Analyze table structure
.PHONY: analyze
analyze:
ifndef FILE
	@echo "Usage: make analyze FILE=path/to/document.pdf"
	@exit 1
endif
	$(PYTHON) pdf_text_extractor.py "$(FILE)" --analyze

# Clean temporary files
.PHONY: clean
clean:
	@echo "Cleaning temporary files..."
ifeq ($(DETECTED_OS),Windows)
	-$(RM) *.pyc 2>nul
	-$(RM) __pycache__ 2>nul
	-$(RM) *.log 2>nul
else
	-$(RM) *.pyc
	-$(RM) -rf __pycache__
	-$(RM) *.log
endif

# Create sample directory structure
.PHONY: create-dirs
create-dirs:
	$(MKDIR) input_pdfs
	$(MKDIR) output_text
	@echo "Created directories: input_pdfs/ and output_text/"

# Upgrade dependencies
.PHONY: upgrade
upgrade:
	@echo "Upgrading dependencies..."
	$(PIP) install --upgrade -r requirements.txt

# Install development dependencies
.PHONY: install-dev
install-dev: install
	$(PIP) install pytest black flake8

# Run code formatting
.PHONY: format
format:
	@echo "Formatting code..."
	black pdf_text_extractor.py

# Run linting
.PHONY: lint
lint:
	@echo "Running linting..."
	flake8 pdf_text_extractor.py

# Build Windows executable
.PHONY: build-exe
build-exe:
ifeq ($(DETECTED_OS),Windows)
	@echo "Building Windows executable..."
	$(PYTHON) build_simple.py
else
	@echo "Windows executable build is only available on Windows"
	@echo "Current OS: $(DETECTED_OS)"
endif

# Show system info
.PHONY: info
info:
	@echo "System Information"
	@echo "=================="
	@echo "OS: $(DETECTED_OS)"
	@echo "Python: $(PYTHON)"
	@echo "Pip: $(PIP)"
	@$(PYTHON) --version
	@$(PIP) --version