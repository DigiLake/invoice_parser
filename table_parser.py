#!/usr/bin/env python3
"""
Conservative table parser for PDF text extraction - extracts what it can, leaves blanks for manual entry
"""

import re
import csv
from typing import List, Dict, Any, Optional


def parse_invoice_table(text: str) -> List[Dict[str, Any]]:
    """
    Parse invoice table from extracted text - conservative approach.
    Extracts what it can reliably identify, leaves empty fields for manual entry.

    Args:
        text: Extracted text from PDF

    Returns:
        List of dictionaries representing table rows
    """
    lines = text.strip().split('\n')
    table_data = []

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        # Look for lines that contain product information
        if 'HSO CHINA' not in line.upper() and 'CHINA' not in line.upper():
            continue

        # Initialize row with empty values
        row = {
            'Product': '',
            'Quantity': '',
            'Unit_Price_USD': '',
            'Total_Price_USD': '',
            'Source_Line': line_num,
            'Raw_Text': line
        }

        # Extract product name (everything before HSO CHINA)
        product_match = re.search(r'^(.+?)(?=HSO\s+CHINA)', line, re.IGNORECASE)
        if product_match:
            product_name = product_match.group(1).strip()
            # Clean up product name - remove long product codes but keep meaningful text
            product_clean = re.sub(r'\d{8,}', '', product_name).strip()
            product_clean = re.sub(r'\s+', ' ', product_clean).strip()
            row['Product'] = product_clean

        # Try to extract numbers from the end of the line
        # Look for patterns like: [quantity] [unit_price] [total_price]
        # But be conservative - only extract what we're confident about

        # Pattern 1: Clean numbers at end: QTY UNIT_PRICE TOTAL_PRICE
        clean_pattern = r'(\d+)\s+(\d+(?:\.\d+)?)\s+([\d,]+\.?\d*)$'
        match = re.search(clean_pattern, line)
        if match:
            row['Quantity'] = int(match.group(1))
            row['Unit_Price_USD'] = float(match.group(2))
            row['Total_Price_USD'] = float(match.group(3).replace(',', ''))
        else:
            # Pattern 2: Numbers with colon: QTY UNIT_PRICE : TOTAL_PRICE
            colon_pattern = r'(\d+)\s+(\d+(?:\.\d+)?)\s*:\s*([\d,]+\.?\d*)$'
            match = re.search(colon_pattern, line)
            if match:
                row['Quantity'] = int(match.group(1))
                row['Unit_Price_USD'] = float(match.group(2))
                row['Total_Price_USD'] = float(match.group(3).replace(',', ''))
            else:
                # Pattern 3: Just extract unit and total price (leave quantity blank)
                price_pattern = r'(\d+(?:\.\d+)?)\s+([\d,]+\.?\d*)$'
                match = re.search(price_pattern, line)
                if match:
                    row['Unit_Price_USD'] = float(match.group(1))
                    row['Total_Price_USD'] = float(match.group(2).replace(',', ''))
                    # Leave quantity empty for manual entry

        # Special handling for corrupted quantities
        # If we found prices but quantity has issues, try to extract clean numbers only
        if row['Unit_Price_USD'] and row['Total_Price_USD'] and not row['Quantity']:
            # Look for a clean number before the unit price
            qty_pattern = r'(\d+)(?:\s+|\s*\.\s*)' + re.escape(str(row['Unit_Price_USD']))
            qty_match = re.search(qty_pattern, line)
            if qty_match:
                try:
                    row['Quantity'] = int(qty_match.group(1))
                except ValueError:
                    pass  # Leave empty for manual entry

        # Only add row if we extracted at least the product name
        if row['Product'] and len(row['Product']) > 2:
            table_data.append(row)

    return table_data


def save_to_csv(table_data: List[Dict[str, Any]], csv_path: str) -> None:
    """
    Save table data to CSV file with proper formatting.

    Args:
        table_data: List of dictionaries representing table rows
        csv_path: Path to save CSV file
    """
    if not table_data:
        return

    # Define the column order we want
    fieldnames = ['Product', 'Quantity', 'Unit_Price_USD', 'Total_Price_USD', 'Source_Line', 'Raw_Text']

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        for row in table_data:
            # Format each field properly for CSV
            csv_row = {}

            # Product name - clean and trim
            csv_row['Product'] = str(row.get('Product', '')).strip()

            # Quantity - format as integer or empty
            qty = row.get('Quantity', '')
            if qty != '' and qty is not None:
                try:
                    csv_row['Quantity'] = int(qty)
                except (ValueError, TypeError):
                    csv_row['Quantity'] = ''
            else:
                csv_row['Quantity'] = ''

            # Unit Price - format to 2 decimal places or empty
            unit_price = row.get('Unit_Price_USD', '')
            if unit_price != '' and unit_price is not None:
                try:
                    csv_row['Unit_Price_USD'] = f"{float(unit_price):.2f}"
                except (ValueError, TypeError):
                    csv_row['Unit_Price_USD'] = ''
            else:
                csv_row['Unit_Price_USD'] = ''

            # Total Price - format to 2 decimal places or empty
            total_price = row.get('Total_Price_USD', '')
            if total_price != '' and total_price is not None:
                try:
                    csv_row['Total_Price_USD'] = f"{float(total_price):.2f}"
                except (ValueError, TypeError):
                    csv_row['Total_Price_USD'] = ''
            else:
                csv_row['Total_Price_USD'] = ''

            # Source line - as number
            csv_row['Source_Line'] = row.get('Source_Line', '')

            # Raw text - clean but preserve original
            csv_row['Raw_Text'] = str(row.get('Raw_Text', '')).strip()

            writer.writerow(csv_row)


def analyze_table(table_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze table structure and return summary.

    Args:
        table_data: List of dictionaries representing table rows

    Returns:
        Dictionary with analysis results
    """
    if not table_data:
        return {'status': 'No table data found'}

    # Count non-empty fields
    total_rows = len(table_data)
    products_filled = sum(1 for row in table_data if row.get('Product'))
    quantities_filled = sum(1 for row in table_data if row.get('Quantity') != '')
    unit_prices_filled = sum(1 for row in table_data if row.get('Unit_Price_USD') != '')
    total_prices_filled = sum(1 for row in table_data if row.get('Total_Price_USD') != '')

    # Calculate totals for filled values only
    total_quantity = sum(row.get('Quantity', 0) for row in table_data if isinstance(row.get('Quantity'), (int, float)))
    total_value = sum(row.get('Total_Price_USD', 0) for row in table_data if isinstance(row.get('Total_Price_USD'), (int, float)))

    analysis = {
        'status': 'Table data found',
        'total_rows': total_rows,
        'fields_filled': {
            'products': f"{products_filled}/{total_rows}",
            'quantities': f"{quantities_filled}/{total_rows}",
            'unit_prices': f"{unit_prices_filled}/{total_rows}",
            'total_prices': f"{total_prices_filled}/{total_rows}"
        },
        'calculated_totals': {
            'total_quantity': total_quantity,
            'total_value': total_value
        },
        'completion_rate': f"{((quantities_filled + unit_prices_filled + total_prices_filled) / (total_rows * 3) * 100):.1f}%"
    }

    return analysis


# Keep backward compatibility
def parse_apple_invoice_table(text: str) -> List[Dict[str, Any]]:
    """Backward compatibility wrapper"""
    return parse_invoice_table(text)


if __name__ == "__main__":
    # Test with sample text including problematic lines
    test_text = """
APPLEIPHONE 12  256GB HSO CHINA 851713004 4 233.00 932.00
APPLE IPHONE 12 PRO 128GB HSO CHINA 9517130011 270.00 : 2,970.00
APPLE IPHONE 13 PRO 256GB HSO CHINA 85171300 14. 400.00 5,600.00
APPLE IPHONE 13 PRO MAX 512GBHSO CHINA 85171300 i 490.00 5,390.00
APPLE IPHONE SE3 256GB HSO CHINA 85171300 tos 200.00 rae 200.00
    """

    result = parse_invoice_table(test_text)
    print("Parsed table:")
    for row in result:
        print(f"Product: {row['Product']}")
        print(f"Quantity: {row['Quantity']}")
        print(f"Unit Price: {row['Unit_Price_USD']}")
        print(f"Total Price: {row['Total_Price_USD']}")
        print(f"Raw: {row['Raw_Text']}")
        print("-" * 50)