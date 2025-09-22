#!/usr/bin/env python3
import re

# 様々な文字種での文字種対応テスト
test_cases = [
    {
        "name": "漢字のみ",
        "input": "田中花子",
        "expected": "✅対応済み"
    },
    {
        "name": "ひらがなのみ",
        "input": "たなか はなこ",
        "expected": "✅対応済み"
    },
    {
        "name": "カタカナのみ",
        "input": "タナカ ハナコ",
        "expected": "✅対応済み"
    },
    {
        "name": "漢字+ひらがな混合",
        "input": "田中 はなこ",
        "expected": "✅対応済み"
    },
    {
        "name": "漢字+カタカナ混合",
        "input": "田中 ハナコ",
        "expected": "✅対応済み"
    },
    {
        "name": "ひらがな+カタカナ混合",
        "input": "たなか ハナコ",
        "expected": "✅対応済み"
    },
    {
        "name": "アルファベット",
        "input": "John Smith",
        "expected": "❌非対応"
    },
    {
        "name": "数字",
        "input": "田中 123",
        "expected": "❌非対応"
    },
    {
        "name": "記号",
        "input": "田中 花@子",
        "expected": "❌非対応"
    },
    {
        "name": "全角アルファベット",
        "input": "Ｊｏｈｎ Ｓｍｉｔｈ",
        "expected": "❌非対応"
    },
    {
        "name": "漢字+アルファベット混合",
        "input": "田中 Mary",
        "expected": "❌非対応"
    }
]

# 現在の正規表現パターン
current_pattern = r'([一-龯あ-ゖア-ヶ]+)\s+([一-龯あ-ゖア-ヶ]+)\s*\n?\s*【([^】]+)】'

print("📊 現在のシステム文字種対応状況")
print("=" * 60)
print(f"使用中の正規表現: {current_pattern}")
print()

print("📝 文字種別対応範囲:")
print("✅ [一-龯] : 漢字（CJK統合漢字）")
print("✅ [あ-ゖ] : ひらがな")
print("✅ [ア-ヶ] : カタカナ")
print("❌ [a-zA-Z] : 半角アルファベット")
print("❌ [０-９] : 全角数字")
print("❌ [0-9] : 半角数字")
print("❌ その他記号・特殊文字")
print()

print("🧪 テストケース結果:")
print("-" * 60)

for test_case in test_cases:
    name = test_case["name"]
    input_text = test_case["input"]
    expected = test_case["expected"]

    # 姓名を分離
    name_parts = input_text.split(' ')
    if len(name_parts) == 2:
        sei, mei = name_parts

        # 正規表現でマッチするかテスト
        test_text = f"{sei} {mei}【テスト評価】"
        match = re.search(current_pattern, test_text)

        if match:
            actual = "✅対応"
            sei_matched = match.group(1)
            mei_matched = match.group(2)
            evaluation = match.group(3)
            detail = f"抽出: 姓='{sei_matched}', 名='{mei_matched}', 評価='{evaluation}'"
        else:
            actual = "❌非対応"
            detail = "正規表現にマッチしません"

        status = "✅" if expected == actual else "⚠️"

        print(f"{status} {name:15} | 入力: '{input_text:12}' | 予想: {expected:6} | 結果: {actual:6}")
        print(f"    {detail}")
        print()
    else:
        print(f"❌ {name:15} | 入力: '{input_text:12}' | エラー: スペース区切り必須")
        print()

print("=" * 60)
print("📊 対応状況サマリー:")
print("✅ 完全対応: 日本語（漢字・ひらがな・カタカナ）")
print("❌ 未対応: アルファベット・数字・記号・その他")
print()
print("🔧 拡張案:")
print("- アルファベット対応: [a-zA-Z] を追加")
print("- 全角文字対応: [Ａ-Ｚａ-ｚ０-９] を追加")
print("- ただし姓名判断システムが外部文字に対応している必要あり")