#!/usr/bin/env python3

import re

# Read the file and check what's happening
with open('extracted_text.txt', 'r') as f:
    lines = f.readlines()

print("Debugging parser:")
print("=" * 50)

count = 0
for i, line in enumerate(lines, 1):
    line = line.strip()
    if not line:
        continue

    # Check if line contains product info
    if 'HSO CHINA' in line.upper() or 'CHINA' in line.upper():
        print(f"Line {i}: {line}")

        # Try simple pattern first
        simple_pattern = r'(\d+(?:\.\d+)?)\s+([\d,.:]+)$'
        match = re.search(simple_pattern, line)
        if match:
            print(f"  -> Found pattern: {match.groups()}")
            count += 1
        else:
            print(f"  -> No pattern match")
        print()

print(f"Total lines with patterns: {count}")