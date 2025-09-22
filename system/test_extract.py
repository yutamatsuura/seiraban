#!/usr/bin/env python3
import json
import sys
import subprocess

# Run puppeteer and get result
result = subprocess.run(['node', 'puppeteer_bridge_final.js', 'seimei', '{"name": "田中 太郎"}'],
                       capture_output=True, text=True)

if result.returncode == 0:
    data = json.loads(result.stdout)
    raw_text = data['result']['raw_text']
    print('Score found:', data['result']['score'])
    print('=== 総評 search ===')
    if '総評' in raw_text:
        start = raw_text.find('総評')
        section = raw_text[start:start+400] if start != -1 else 'Not found'
        print('総評 section found:', repr(section))

        # Look for the message pattern
        import re
        sohyo_pattern = r'総評\s*\n\s*(\d+)点\s*\n\s*/100\s*\n\s*(.+?)(?:文字による鑑定|陰陽による鑑定|五行による鑑定|\n\n)'
        sohyo_match = re.search(sohyo_pattern, raw_text, re.DOTALL)
        if sohyo_match:
            message = sohyo_match.group(2).strip()
            print('Message extracted:', repr(message))
        else:
            print('Message pattern not matched')
    else:
        print('総評 not found in raw text')
else:
    print('Error running puppeteer:', result.stderr)