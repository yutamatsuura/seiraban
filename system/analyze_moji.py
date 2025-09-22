#!/usr/bin/env python3
import json
import subprocess
import re

# Run puppeteer and get result for 山本太郎
result = subprocess.run(['node', 'puppeteer_bridge_final.js', 'seimei', '{"name": "山本 太郎"}'],
                       capture_output=True, text=True)

if result.returncode == 0:
    data = json.loads(result.stdout)
    raw_text = data['result']['raw_text']

    # Find the 文字による鑑定 section and print exactly what's there
    moji_section_match = re.search(r'文字による鑑定\s*(.+?)(?:陰陽による鑑定|五行による鑑定|$)', raw_text, re.DOTALL)
    if moji_section_match:
        moji_content = moji_section_match.group(1).strip()
        print('=== Raw 文字による鑑定 content ===')
        print(repr(moji_content))
        print()
        print('=== Formatted 文字による鑑定 content ===')
        print(moji_content)

        # Let's look for sentence boundaries more carefully
        sentences = re.split(r'[。]', moji_content)
        print(f'\n=== Split by 。: {len(sentences)} parts ===')
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                print(f'{i}: {repr(sentence.strip())}')