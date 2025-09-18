#!/usr/bin/env python3
"""
PDF Text Extraction Utility with OCR Support

This utility extracts text from PDF files, including scanned PDFs using OCR.
It supports both text-based PDFs and image-based (scanned) PDFs.
"""

import argparse
import csv
import logging
import re
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    import fitz  # PyMuPDF
    import pytesseract
    from PIL import Image
    import io
    import pandas as pd
    from table_parser import parse_apple_invoice_table
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install dependencies: pip install PyMuPDF pytesseract Pillow pandas")
    sys.exit(1)


class PDFTextExtractor:
    """Extract text from PDF files with OCR fallback for scanned documents."""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize the PDF text extractor.

        Args:
            tesseract_cmd: Path to tesseract executable (optional)
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def extract_text_from_pdf(self, pdf_path: str, use_ocr: bool = True) -> str:
        """
        Extract text from a PDF file.

        Args:
            pdf_path: Path to the PDF file
            use_ocr: Whether to use OCR for scanned pages

        Returns:
            Extracted text as string
        """
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        self.logger.info(f"Processing PDF: {pdf_path}")

        try:
            doc = fitz.open(pdf_path)
            extracted_text = []

            for page_num in range(len(doc)):
                page = doc[page_num]

                # Try to extract text directly first
                text = page.get_text()

                if text.strip():
                    self.logger.info(f"Page {page_num + 1}: Extracted text directly")
                    extracted_text.append(text)
                elif use_ocr:
                    # If no text found, use OCR on the page image
                    self.logger.info(f"Page {page_num + 1}: Using OCR")
                    ocr_text = self._extract_text_with_ocr(page)
                    extracted_text.append(ocr_text)
                else:
                    self.logger.warning(f"Page {page_num + 1}: No text found and OCR disabled")

            doc.close()
            return '\n\n'.join(extracted_text)

        except Exception as e:
            self.logger.error(f"Error processing PDF: {e}")
            raise

    def _extract_text_with_ocr(self, page) -> str:
        """
        Extract text from a PDF page using OCR.

        Args:
            page: PyMuPDF page object

        Returns:
            Extracted text using OCR
        """
        try:
            # Convert PDF page to image
            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0))  # 2x scaling for better OCR
            img_data = pix.tobytes("png")

            # Convert to PIL Image
            img = Image.open(io.BytesIO(img_data))

            # Use Tesseract OCR
            text = pytesseract.image_to_string(img, lang='eng')

            return text

        except Exception as e:
            self.logger.error(f"OCR extraction failed: {e}")
            return ""

    def extract_to_file(self, pdf_path: str, output_path: str, use_ocr: bool = True) -> None:
        """
        Extract text from PDF and save to file.

        Args:
            pdf_path: Path to the PDF file
            output_path: Path to save extracted text
            use_ocr: Whether to use OCR for scanned pages
        """
        text = self.extract_text_from_pdf(pdf_path, use_ocr)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

        self.logger.info(f"Text saved to: {output_path}")

    def batch_extract(self, pdf_directory: str, output_directory: str, use_ocr: bool = True) -> List[str]:
        """
        Extract text from multiple PDF files in a directory.

        Args:
            pdf_directory: Directory containing PDF files
            output_directory: Directory to save extracted text files
            use_ocr: Whether to use OCR for scanned pages

        Returns:
            List of processed file names
        """
        pdf_dir = Path(pdf_directory)
        output_dir = Path(output_directory)

        if not pdf_dir.exists():
            raise FileNotFoundError(f"PDF directory not found: {pdf_directory}")

        output_dir.mkdir(parents=True, exist_ok=True)

        pdf_files = list(pdf_dir.glob("*.pdf"))
        processed_files = []

        for pdf_file in pdf_files:
            try:
                output_file = output_dir / f"{pdf_file.stem}.txt"
                self.extract_to_file(str(pdf_file), str(output_file), use_ocr)
                processed_files.append(pdf_file.name)
            except Exception as e:
                self.logger.error(f"Failed to process {pdf_file.name}: {e}")

        return processed_files

    def extract_tables_to_csv(self, pdf_path: str, csv_path: str, use_ocr: bool = True) -> None:
        """
        Extract table data from PDF and save to CSV.

        Args:
            pdf_path: Path to the PDF file
            csv_path: Path to save CSV file
            use_ocr: Whether to use OCR for scanned pages
        """
        text = self.extract_text_from_pdf(pdf_path, use_ocr)
        table_data = parse_apple_invoice_table(text)

        if table_data:
            from table_parser import save_to_csv
            save_to_csv(table_data, csv_path)
            self.logger.info(f"Table data saved to CSV: {csv_path}")
        else:
            self.logger.warning("No table data found in PDF")

    def _parse_table_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Parse table data from extracted text.

        Args:
            text: Extracted text from PDF

        Returns:
            List of dictionaries representing table rows
        """
        lines = text.strip().split('\n')
        table_data = []

        # Enhanced patterns for different invoice formats
        patterns = [
            # Apple iPhone pattern (current invoice)
            r'APPLE\s+IPHONE\s+([\w\s]+?)\s+(\d+GB)\s+HSO\s+CHINA\s+(\d+)\s+(\d+(?:\.\d+)?)\s+([\d,]+\.\d+)',
            # Generic product pattern
            r'([A-Z][\w\s]+?)\s+(\d+)\s+(\d+(?:\.\d+)?)\s+([\d,]+\.\d+)',
            # Pattern with quantities and prices
            r'([A-Z][\w\s]+?)\s+HSO\s+CHINA\s+(\d+)\s+(\d+(?:\.\d+)?)\s+([\d,]+\.\d+)'
        ]

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try Apple iPhone specific pattern first
            apple_match = re.search(patterns[0], line)
            if apple_match:
                model = apple_match.group(1).strip()
                storage = apple_match.group(2)
                quantity = int(apple_match.group(3))
                unit_price = float(apple_match.group(4))
                total_price = float(apple_match.group(5).replace(',', ''))

                table_data.append({
                    'Product': f"Apple iPhone {model} {storage}",
                    'Model': model,
                    'Storage': storage,
                    'Origin': 'HSO CHINA',
                    'Quantity': quantity,
                    'Unit_Price_USD': unit_price,
                    'Total_Price_USD': total_price
                })
                continue

            # Try other patterns for different invoice types
            for pattern in patterns[1:]:
                match = re.search(pattern, line)
                if match:
                    if len(match.groups()) == 4:
                        product, quantity, unit_price, total_price = match.groups()
                        table_data.append({
                            'Product': product.strip(),
                            'Quantity': int(quantity),
                            'Unit_Price_USD': float(unit_price),
                            'Total_Price_USD': float(total_price.replace(',', ''))
                        })
                    break

        return table_data

    def _save_to_csv(self, table_data: List[Dict[str, Any]], csv_path: str) -> None:
        """
        Save table data to CSV file.

        Args:
            table_data: List of dictionaries representing table rows
            csv_path: Path to save CSV file
        """
        if not table_data:
            return

        fieldnames = table_data[0].keys()

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(table_data)

    def analyze_table_structure(self, pdf_path: str, use_ocr: bool = True) -> Dict[str, Any]:
        """
        Analyze table structure in PDF and return summary.

        Args:
            pdf_path: Path to the PDF file
            use_ocr: Whether to use OCR for scanned pages

        Returns:
            Dictionary with table analysis
        """
        text = self.extract_text_from_pdf(pdf_path, use_ocr)
        table_data = parse_apple_invoice_table(text)

        if not table_data:
            return {'status': 'No table data found'}

        from table_parser import analyze_table
        analysis = analyze_table(table_data)

        return analysis


def main():
    """Command-line interface for the PDF text extractor."""
    parser = argparse.ArgumentParser(description="Extract text from PDF files with OCR support")
    parser.add_argument("pdf_path", help="Path to PDF file or directory")
    parser.add_argument("-o", "--output", help="Output file or directory path")
    parser.add_argument("--csv", action="store_true", help="Extract table data to CSV format")
    parser.add_argument("--analyze", action="store_true", help="Analyze table structure")
    parser.add_argument("--no-ocr", action="store_true", help="Disable OCR for scanned pages")
    parser.add_argument("--batch", action="store_true", help="Process all PDFs in directory")
    parser.add_argument("--tesseract-cmd", help="Path to tesseract executable")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    extractor = PDFTextExtractor(tesseract_cmd=args.tesseract_cmd)

    try:
        if args.analyze:
            # Analyze table structure
            analysis = extractor.analyze_table_structure(args.pdf_path, use_ocr=not args.no_ocr)
            print("Table Analysis:")
            print(f"Status: {analysis['status']}")
            if 'total_rows' in analysis:
                print(f"Total rows: {analysis['total_rows']}")
                if 'fields_filled' in analysis:
                    print("Data completion:")
                    for field, count in analysis['fields_filled'].items():
                        print(f"  {field}: {count}")
                    print(f"Overall completion rate: {analysis['completion_rate']}")
                    if 'calculated_totals' in analysis:
                        totals = analysis['calculated_totals']
                        print(f"Calculated totals (from filled fields only):")
                        print(f"  Total quantity: {totals['total_quantity']:,}")
                        print(f"  Total value: ${totals['total_value']:,.2f}")
                else:
                    # Old format fallback
                    if 'columns' in analysis:
                        print(f"Columns: {', '.join(analysis['columns'])}")
                    if 'total_quantity' in analysis:
                        print(f"Total quantity: {analysis['total_quantity']}")
                    if 'total_value' in analysis:
                        print(f"Total value: ${analysis['total_value']:,.2f}")
                    if 'products' in analysis:
                        print(f"Products found: {len(analysis['products'])}")
        elif args.csv:
            # Extract to CSV
            if args.output:
                csv_path = args.output
            else:
                # Auto-generate CSV filename from PDF name
                pdf_stem = Path(args.pdf_path).stem
                csv_path = f"{pdf_stem}.csv"

            extractor.extract_tables_to_csv(args.pdf_path, csv_path, use_ocr=not args.no_ocr)
            print(f"Table data extracted to CSV: {csv_path}")
        elif args.batch:
            # Batch processing
            output_dir = args.output or f"{args.pdf_path}_extracted"
            processed = extractor.batch_extract(args.pdf_path, output_dir, use_ocr=not args.no_ocr)
            print(f"Processed {len(processed)} files:")
            for file in processed:
                print(f"  - {file}")
        else:
            # Single file processing
            if args.output:
                extractor.extract_to_file(args.pdf_path, args.output, use_ocr=not args.no_ocr)
                print(f"Text extracted to: {args.output}")
            else:
                text = extractor.extract_text_from_pdf(args.pdf_path, use_ocr=not args.no_ocr)
                print(text)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()