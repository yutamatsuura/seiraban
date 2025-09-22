#!/usr/bin/env python3
import re

# Test sample text that mimics the structure we see in the logs
test_text = """花  文字の由来・意味から名前には使用しないほうがいい文字です。花  名前には使用できない文字です。人生に実り少なく早く枯れてしまう。または変化に翻弄され苦労の連続となりがちです。"""

print("Testing parsing logic with sample text:")
print(f"Raw text: {repr(test_text)}")
print()

# Split into sentences like the backend does
sentences = re.split(r'[。]', test_text)
sentences = [s.strip() for s in sentences if s.strip()]

print(f"Sentences after split:")
for i, sentence in enumerate(sentences):
    print(f"  {i}: {repr(sentence)}")

print()

# Simulate the backend logic
extracted_items = []
i = 0
while i < len(sentences):
    sentence = sentences[i]
    print(f"Processing sentence {i}: {repr(sentence)}")

    # Pattern 5: 文字単体での鑑定（例: 花 文字の由来・意味から...）
    char_meaning_match = re.search(r'^([一-龯]+)\s+文字の', sentence)
    if char_meaning_match:
        char = char_meaning_match.group(1).strip()
        detail_parts = [sentence]
        print(f"  ✓ Pattern 5 matched - char: {char}")

        # 続きの文を結合（新しい文字パターンが始まったら停止）
        j = i + 1
        while j < len(sentences):
            next_sentence = sentences[j]
            print(f"    Checking next sentence {j}: {repr(next_sentence)}")

            # 新しいパターンが始まったら停止
            bracket_match = re.match(r'([一-龯]+)\s*【([^】]+)】', next_sentence)
            special_match = re.match(r'(人格|地行|地格):([^\s]+)', next_sentence)
            char_meaning_match2 = re.match(r'([一-龯]+)\s+文字の', next_sentence)
            single_char_match = re.match(r'^([一-龯]+)\s+(.+)', next_sentence)

            if bracket_match:
                print(f"      → Bracket pattern found, breaking")
                break
            elif special_match:
                print(f"      → Special pattern found, breaking")
                break
            elif char_meaning_match2:
                print(f"      → Char meaning pattern found, breaking")
                break
            elif single_char_match:
                print(f"      → Single char pattern found, breaking")
                break
            else:
                print(f"      → No pattern found, continuing")
                detail_parts.append(next_sentence)
                j += 1

        extracted_items.append({
            "文字": char,
            "分類": "文字",
            "詳細": "。".join(detail_parts) + "。"
        })
        i = j
        continue

    # Pattern 6: その他の形式（単一文字で始まる場合）
    single_char_match = re.search(r'^([一-龯]+)\s+(.+)', sentence)
    if single_char_match:
        char = single_char_match.group(1).strip()
        detail_parts = [single_char_match.group(2).strip()]
        print(f"  ✓ Pattern 6 matched - char: {char}, detail: {detail_parts[0]}")

        # 関連する続きの文を結合（新しい文字パターンは除外）
        j = i + 1
        while j < len(sentences):
            next_sentence = sentences[j]
            print(f"    Checking next sentence {j}: {repr(next_sentence)}")

            # 新しいパターンが始まったら停止
            if re.match(r'([一-龯]+)\s*【([^】]+)】', next_sentence) or \
               re.match(r'(人格|地行|地格):([^\s]+)', next_sentence) or \
               re.match(r'([一-龯]+)\s+文字の', next_sentence) or \
               re.match(r'^([一-龯]+)\s+(.+)', next_sentence):
                print(f"      → Pattern found, breaking")
                break
            else:
                print(f"      → No pattern found, continuing")
                detail_parts.append(next_sentence)
                j += 1

        extracted_items.append({
            "文字": char,
            "分類": "その他",
            "詳細": "。".join(detail_parts) + "。"
        })
        i = j
        continue

    print(f"  ✗ No pattern matched")
    i += 1

print()
print("Final extracted items:")
for i, item in enumerate(extracted_items):
    print(f"{i+1}. 文字: {item['文字']}")
    print(f"   分類: {item['分類']}")
    print(f"   詳細: {item['詳細']}")
    print()