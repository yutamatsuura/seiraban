#!/usr/bin/env python3
import re

# 文字による鑑定で「め【地行が水行】」が抽出されない原因を調査

test_text = """
文字による鑑定 め
【地行が水行】
水性はご自身がやってきたことを水に流し、努力が報われず、体を壊します。苦労の連続となりやすいです。地格:めざる  地格に9画の文字は使ってはいけません。喧嘩と衝突、事故死が多くなります。
"""

print("文字による鑑定の抽出テスト")
print("=" * 50)

# 現在のパターン（漢字のみ）
current_pattern = r'([一-龯]+)\s*【([^】]+)】\s*(.*)'
current_match = re.search(current_pattern, test_text)
print(f"現在のパターン（漢字のみ）: {current_pattern}")
print(f"マッチ結果: {current_match}")

# 修正パターン（ひらがな・カタカナも含む）
fixed_pattern = r'([\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+)\s*【([^】]+)】\s*(.*)'
fixed_match = re.search(fixed_pattern, test_text)
print(f"\n修正パターン（日本語文字）: {fixed_pattern}")
print(f"マッチ結果: {fixed_match}")

if fixed_match:
    print(f"文字: '{fixed_match.group(1)}'")
    print(f"分類: '{fixed_match.group(2)}'")
    print(f"詳細: '{fixed_match.group(3)}'")

print("\n文字種別テスト:")
print(f"'め' の文字コード: {ord('め'):04x}")
print(f"'め' が漢字範囲[一-龯]にマッチ: {bool(re.match(r'[一-龯]', 'め'))}")
print(f"'め' がひらがな範囲[\u3042-\u3096]にマッチ: {bool(re.match(r'[\u3042-\u3096]', 'め'))}")
print(f"'め' が日本語範囲[\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]にマッチ: {bool(re.match(r'[\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]', 'め'))}")