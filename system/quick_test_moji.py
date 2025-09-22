#!/usr/bin/env python3
import json
import subprocess
import re

# まず少数の名前で詳細分析
test_names = [
    ("山本", "太郎"),  # 既知で文字による鑑定あり
    ("山田", "花子"),  # 既知で文字による鑑定なし
    ("田中", "太郎"),  # 一般的な名前
    ("佐藤", "花子"),  # 一般的な名前
    ("鈴木", "一郎"),  # 一般的な名前
    ("織田", "信長"),  # 歴史上の人物
    ("豊臣", "秀吉"),  # 歴史上の人物
    ("徳川", "家康"),  # 歴史上の人物
    ("武田", "信玄"),  # 歴史上の人物
    ("龍", "馬"),     # 特殊漢字
]

print("Testing name patterns for 文字による鑑定...")

for i, (sei, mei) in enumerate(test_names, 1):
    try:
        print(f"\n{i:2d}. Testing: {sei} {mei}")

        # Puppeteerでテスト実行
        result = subprocess.run(
            ['node', 'puppeteer_bridge_final.js', 'seimei', f'{{"name": "{sei} {mei}"}}'],
            capture_output=True, text=True, timeout=15
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            raw_text = data['result']['raw_text']
            score = data['result']['score']

            print(f"    Score: {score}")

            # 文字による鑑定セクションをチェック
            if '文字による鑑定' in raw_text:
                print("    ✓ Contains '文字による鑑定' keyword")

                # セクション全体を抽出
                moji_section_match = re.search(r'文字による鑑定\s*(.+?)(?:陰陽による鑑定|五行による鑑定|$)', raw_text, re.DOTALL)
                if moji_section_match:
                    moji_content = moji_section_match.group(1).strip()
                    print(f"    Section content length: {len(moji_content)}")

                    if moji_content and len(moji_content) > 10:
                        print("    ✓ Has substantial content")
                        print(f"    Content preview: {repr(moji_content[:100])}...")

                        # パターン分析
                        print("    Pattern analysis:")

                        # 【】パターン
                        brackets = re.findall(r'【([^】]+)】', moji_content)
                        if brackets:
                            print(f"      Brackets found: {brackets}")

                        # 人格パターン
                        jinko_matches = re.findall(r'人格:([^\s]+)', moji_content)
                        if jinko_matches:
                            print(f"      人格 patterns: {jinko_matches}")

                        # 文字名パターン（漢字＋【】）
                        char_patterns = re.findall(r'([一-龯]+)\s*【([^】]+)】', moji_content)
                        if char_patterns:
                            print(f"      Character patterns: {char_patterns}")

                        # 文の区切り
                        sentences = re.split(r'[。]', moji_content)
                        print(f"      Sentences count: {len([s for s in sentences if s.strip()])}")
                        for j, sentence in enumerate(sentences[:3]):
                            if sentence.strip():
                                print(f"        {j+1}: {repr(sentence.strip()[:50])}...")

                    else:
                        print("    ✗ Empty or too short content")
                else:
                    print("    ✗ Could not extract section content")
            else:
                print("    ✗ No '文字による鑑定' keyword found")

                # 他のセクションを確認
                if '陰陽による鑑定' in raw_text:
                    print("    (Has 陰陽による鑑定)")
                if '五行による鑑定' in raw_text:
                    print("    (Has 五行による鑑定)")
                if '画数による鑑定' in raw_text:
                    print("    (Has 画数による鑑定)")

        else:
            print(f"    ERROR: {result.stderr}")

    except Exception as e:
        print(f"    EXCEPTION: {e}")

print("\nTest completed!")