#!/usr/bin/env python3

from table_parser import parse_invoice_table, save_to_csv, analyze_table

with open('extracted_text.txt', 'r') as f:
    text = f.read()

table_data = parse_invoice_table(text)

print('Analysis:')
analysis = analyze_table(table_data)
for key, value in analysis.items():
    if key != 'products':
        print(f'{key}: {value}')

print(f'\nAll {len(table_data)} products found:')
for i, row in enumerate(table_data, 1):
    qty = row['Quantity']
    unit_price = row['Unit_Price_USD']
    total_price = row['Total_Price_USD']
    product = row['Product']
    print(f'{i:2d}. {product:30s} | Qty: {qty:4d} | Price: ${unit_price:6.2f} | Total: ${total_price:9,.2f}')

# Save to CSV
save_to_csv(table_data, 'complete_invoice_table.csv')
print(f'\nSaved {len(table_data)} rows to complete_invoice_table.csv')