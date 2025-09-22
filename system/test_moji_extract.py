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
    print('Score found:', data['result']['score'])
    print('=== 文字による鑑定 section ===')

    # Test extraction patterns
    details = {}
    details["文字による鑑定"] = []

    # 文字による鑑定セクションを抽出
    moji_section_match = re.search(r'文字による鑑定\s*(.+?)(?:陰陽による鑑定|五行による鑑定|$)', raw_text, re.DOTALL)
    if moji_section_match:
        moji_content = moji_section_match.group(1).strip()
        print('文字による鑑定 content found:', repr(moji_content[:200]))

        # 個別の文字鑑定（例：郎【分離名】...）
        char_evaluations = re.findall(r'([^\s]+)\s*【([^】]+)】\s*([^。]+。)', moji_content, re.DOTALL)
        print(f'Found {len(char_evaluations)} character evaluations:')
        for char, category, description in char_evaluations:
            evaluation = {
                "文字": char.strip(),
                "分類": category.strip(),
                "詳細": description.strip()
            }
            details["文字による鑑定"].append(evaluation)
            print(f'  {evaluation}')

        # 人格鑑定（例：人格:本太 人格に9画の...）
        jinko_match = re.search(r'人格:([^\s]+)\s+(.+?)(?:[。\s]|$)', moji_content, re.DOTALL)
        if jinko_match:
            evaluation = {
                "文字": f"人格:{jinko_match.group(1).strip()}",
                "分類": "人格",
                "詳細": jinko_match.group(2).strip()
            }
            details["文字による鑑定"].append(evaluation)
            print(f'  人格: {evaluation}')
        else:
            print('  No 人格 pattern found')
    else:
        print('No 文字による鑑定 section found')

    print('\n=== Final result ===')
    print(json.dumps(details["文字による鑑定"], ensure_ascii=False, indent=2))
else:
    print('Error running puppeteer:', result.stderr)