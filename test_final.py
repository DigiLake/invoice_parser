#!/usr/bin/env python3

from table_parser import parse_invoice_table, save_to_csv, analyze_table

with open('extracted_text.txt', 'r') as f:
    text = f.read()

table_data = parse_invoice_table(text)

print('Final Analysis:')
analysis = analyze_table(table_data)
print(f"Status: {analysis['status']}")
print(f"Total rows: {analysis['total_rows']}")
print(f"Data completion:")
for field, count in analysis['fields_filled'].items():
    print(f"  {field}: {count}")
print(f"Overall completion rate: {analysis['completion_rate']}")

print(f'\nAll {len(table_data)} products found:')
for i, row in enumerate(table_data, 1):
    qty = str(row['Quantity']) if row['Quantity'] != '' else 'BLANK'
    unit_price = f"${row['Unit_Price_USD']:.2f}" if row['Unit_Price_USD'] != '' else 'BLANK'
    total_price = f"${row['Total_Price_USD']:,.2f}" if row['Total_Price_USD'] != '' else 'BLANK'
    product = row['Product']
    print(f'{i:2d}. {product:35s} | Qty: {qty:10s} | Unit: {unit_price:8s} | Total: {total_price:12s}')

# Save to CSV with blanks for manual entry
save_to_csv(table_data, 'final_invoice_table.csv')
print(f'\nSaved {len(table_data)} rows to final_invoice_table.csv')
print('Empty cells can be filled manually in Excel/Google Sheets')