#!/usr/bin/env python3
import json
import subprocess
import re

# 改善した抽出ロジックをテストする名前リスト
test_names = [
    # 分析済み：文字による鑑定あり
    ("山本", "太郎"),    # 郎【分離名】+ 人格:本太
    ("山田", "花子"),    # 花 文字の由来・意味から...
    ("田中", "太郎"),    # 郎【分離名】
    ("佐藤", "花子"),    # 花 文字の由来・意味から...
    ("鈴木", "一郎"),    # 郎【分離名】
    ("織田", "信長"),    # 地行:信長
    ("武田", "信玄"),    # 地行:信玄
    ("龍", "馬"),       # 馬【地行が水行】

    # 新規テスト名前
    ("高橋", "美咲"),    # 新しいパターンをチェック
    ("伊藤", "翔太"),    # 新しいパターンをチェック
]

print("Testing improved universal extraction logic...")
print("=" * 60)

success_count = 0
fail_count = 0

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

            # バックエンドでの抽出結果をシミュレート（ローカルで同じロジックを実行）
            moji_section_match = re.search(r'文字による鑑定\s*(.+?)(?:陰陽による鑑定|五行による鑑定|$)', raw_text, re.DOTALL)
            if moji_section_match:
                moji_content = moji_section_match.group(1).strip()

                if moji_content and len(moji_content) > 10:
                    print(f"    ✓ Has 文字による鑑定 content ({len(moji_content)} chars)")
                    print(f"    Raw content: {repr(moji_content[:100])}...")

                    # 新しい抽出ロジックをテスト
                    extracted_items = []
                    sentences = re.split(r'[。]', moji_content)
                    sentences = [s.strip() for s in sentences if s.strip()]

                    i_local = 0
                    while i_local < len(sentences):
                        sentence = sentences[i_local]

                        # パターン1: 漢字【分類名】
                        bracket_match = re.search(r'([一-龯]+)\s*【([^】]+)】\s*(.*)', sentence)
                        if bracket_match:
                            char = bracket_match.group(1).strip()
                            category = bracket_match.group(2).strip()
                            detail_parts = [bracket_match.group(3).strip()] if bracket_match.group(3).strip() else []

                            # 続く文を結合
                            j = i_local + 1
                            while j < len(sentences):
                                next_sentence = sentences[j]
                                if not re.match(r'([一-龯]+)\s*【([^】]+)】', next_sentence) and \
                                   not re.match(r'(人格|地行):([^\s]+)', next_sentence) and \
                                   not re.match(r'([一-龯]+)\s+文字の', next_sentence):
                                    detail_parts.append(next_sentence)
                                    j += 1
                                else:
                                    break

                            extracted_items.append({
                                "文字": char,
                                "分類": category,
                                "詳細": "。".join(detail_parts) + "。" if detail_parts else ""
                            })
                            i_local = j
                            continue

                        # パターン2: 人格:文字
                        jinko_match = re.search(r'人格:([^\s]+)\s*(.*)', sentence)
                        if jinko_match:
                            char_combo = jinko_match.group(1).strip()
                            detail_parts = [jinko_match.group(2).strip()] if jinko_match.group(2).strip() else []

                            j = i_local + 1
                            while j < len(sentences):
                                next_sentence = sentences[j]
                                if not re.match(r'([一-龯]+)\s*【([^】]+)】', next_sentence) and \
                                   not re.match(r'(人格|地行):([^\s]+)', next_sentence) and \
                                   not re.match(r'([一-龯]+)\s+文字の', next_sentence):
                                    detail_parts.append(next_sentence)
                                    j += 1
                                else:
                                    break

                            extracted_items.append({
                                "文字": f"人格:{char_combo}",
                                "分類": "人格",
                                "詳細": "。".join(detail_parts) + "。" if detail_parts else ""
                            })
                            i_local = j
                            continue

                        # パターン3: 地行:文字
                        chiko_match = re.search(r'地行:([^\s]+)\s*(.*)', sentence)
                        if chiko_match:
                            char_combo = chiko_match.group(1).strip()
                            detail_parts = [chiko_match.group(2).strip()] if chiko_match.group(2).strip() else []

                            j = i_local + 1
                            while j < len(sentences):
                                next_sentence = sentences[j]
                                if not re.match(r'([一-龯]+)\s*【([^】]+)】', next_sentence) and \
                                   not re.match(r'(人格|地行):([^\s]+)', next_sentence) and \
                                   not re.match(r'([一-龯]+)\s+文字の', next_sentence):
                                    detail_parts.append(next_sentence)
                                    j += 1
                                else:
                                    break

                            extracted_items.append({
                                "文字": f"地行:{char_combo}",
                                "分類": "地行",
                                "詳細": "。".join(detail_parts) + "。" if detail_parts else ""
                            })
                            i_local = j
                            continue

                        # パターン4: 文字 文字の由来・意味から...
                        char_meaning_match = re.search(r'^([一-龯]+)\s+文字の', sentence)
                        if char_meaning_match:
                            char = char_meaning_match.group(1).strip()
                            detail_parts = [sentence]

                            j = i_local + 1
                            while j < len(sentences):
                                next_sentence = sentences[j]
                                if next_sentence.startswith(char + ' ') or \
                                   (not re.match(r'([一-龯]+)\s*【([^】]+)】', next_sentence) and \
                                    not re.match(r'(人格|地行):([^\s]+)', next_sentence) and \
                                    not re.match(r'([一-龯]+)\s+文字の', next_sentence)):
                                    detail_parts.append(next_sentence)
                                    j += 1
                                else:
                                    break

                            extracted_items.append({
                                "文字": char,
                                "分類": "文字",
                                "詳細": "。".join(detail_parts) + "。"
                            })
                            i_local = j
                            continue

                        # パターン5: その他の単一文字パターン
                        single_char_match = re.search(r'^([一-龯]+)\s+(.+)', sentence)
                        if single_char_match:
                            char = single_char_match.group(1).strip()
                            detail_parts = [sentence]

                            j = i_local + 1
                            while j < len(sentences):
                                next_sentence = sentences[j]
                                if not re.match(r'([一-龯]+)\s*【([^】]+)】', next_sentence) and \
                                   not re.match(r'(人格|地行):([^\s]+)', next_sentence) and \
                                   not re.match(r'([一-龯]+)\s+文字の', next_sentence) and \
                                   not re.match(r'^([一-龯]+)\s+(.+)', next_sentence):
                                    detail_parts.append(next_sentence)
                                    j += 1
                                else:
                                    break

                            extracted_items.append({
                                "文字": char,
                                "分類": "その他",
                                "詳細": "。".join(detail_parts) + "。"
                            })
                            i_local = j
                            continue

                        i_local += 1

                    # 結果を表示
                    if extracted_items:
                        print(f"    ✓ Successfully extracted {len(extracted_items)} items:")
                        for item in extracted_items:
                            print(f"      - {item['文字']} [{item['分類']}]: {item['詳細'][:50]}...")
                        success_count += 1
                    else:
                        print(f"    ✗ No items extracted despite having content")
                        fail_count += 1
                else:
                    print(f"    ✗ Empty or too short content")
                    fail_count += 1
            else:
                print(f"    ✗ No 文字による鑑定 section found")
                fail_count += 1

        else:
            print(f"    ERROR: {result.stderr}")
            fail_count += 1

    except Exception as e:
        print(f"    EXCEPTION: {e}")
        fail_count += 1

print(f"\n{'='*60}")
print(f"FINAL RESULTS")
print(f"{'='*60}")
print(f"Total tested: {len(test_names)}")
print(f"Success: {success_count}")
print(f"Failed: {fail_count}")
print(f"Success rate: {success_count/len(test_names)*100:.1f}%")