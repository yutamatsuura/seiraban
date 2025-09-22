#!/usr/bin/env python3
import re

# テストケース：井花 浄光寺の五行解析
test_text = """
五行による鑑定
井花 浄光寺
【五行のバランス(悪)】
五行のバランスが良くないです。名前に五行が3つ以上が望ましいです。
人格：花浄
【木-金】
中年期（28歳～50歳）までの運勢。明朗で行動力があり、人をまとめる力があります。

陰陽による鑑定
"""

expected_results = [
    {
        "タイプ": "五行のバランス",
        "対象": "井花 浄光寺",
        "評価": "五行のバランス(悪)",
        "詳細": "五行のバランスが良くないです。名前に五行が3つ以上が望ましいです。"
    },
    {
        "タイプ": "人格",
        "対象": "人格:花浄",
        "評価": "木-金",
        "詳細": "中年期（28歳～50歳）までの運勢。明朗で行動力があり、人をまとめる力があります。"
    }
]

def parse_gogyou_kantei_enhanced(raw_text):
    """五行による鑑定の修正版解析 - 項目分離を改善"""
    results = []

    # 五行セクションを抽出
    gogyou_section_match = re.search(r'五行による鑑定\s*(.+?)(?:\s*陰陽による鑑定|\s*画数による鑑定|$)', raw_text, re.DOTALL)
    if not gogyou_section_match:
        return results

    gogyou_content = gogyou_section_match.group(1).strip()

    if not gogyou_content or len(gogyou_content) <= 10:
        return results

    print(f"五行コンテンツ:\n{gogyou_content}\n")

    # まず名前パターンを検索して姓を動的に検出
    name_pattern = r'([一-龯あ-ゖア-ヶ]+)\s+([一-龯あ-ゖア-ヶ]+)\s*\n?\s*【([^】]+)】'
    name_match = re.search(name_pattern, gogyou_content)

    if name_match:
        sei = name_match.group(1)
        mei = name_match.group(2)
        name_evaluation = name_match.group(3)

        print(f"検出された名前: {sei} {mei}, 評価: {name_evaluation}")

        # パターン1: 五行のバランス - 名前の詳細を取得（人格より前まで）
        name_detail_pattern = rf'{re.escape(sei)}\s+{re.escape(mei)}\s*\n?\s*【[^】]+】\s*(.*?)(?=人格：|$)'
        name_detail_match = re.search(name_detail_pattern, gogyou_content, re.DOTALL)
        if name_detail_match:
            content = name_detail_match.group(1).strip()
            print(f"五行のバランス詳細（修正版）: '{content}'")

            results.append({
                "タイプ": "五行のバランス",
                "対象": f"{sei} {mei}",
                "評価": name_evaluation,
                "詳細": content
            })

        # パターン2: 人格 - 陰陽による鑑定より前まで
        jinko_pattern = r'人格：([^\s]+)\s*\n?\s*【([^】]+)】\s*(.*?)(?=陰陽による鑑定|画数による鑑定|$)'
        jinko_match = re.search(jinko_pattern, gogyou_content, re.DOTALL)
        if jinko_match:
            jinko_value = jinko_match.group(1)
            evaluation = jinko_match.group(2)
            content = jinko_match.group(3).strip()

            print(f"人格詳細（修正版）: '{content}'")

            results.append({
                "タイプ": "人格",
                "対象": f"人格:{jinko_value}",
                "評価": evaluation,
                "詳細": content
            })

    return results

print("五行による鑑定の分離テスト")
print("=" * 60)

# 解析実行
results = parse_gogyou_kantei_enhanced(test_text)
expected = expected_results

print(f"抽出されたアイテム数: {len(results)} (期待値: {len(expected)})")

# 基本チェック
items_count_ok = len(results) == len(expected)
print(f"アイテム数: {'✅' if items_count_ok else '❌'}")

all_tests_passed = items_count_ok

# 各アイテムの詳細チェック
for j, expected_item in enumerate(expected):
    if j < len(results):
        actual_item = results[j]

        type_ok = actual_item['タイプ'] == expected_item['タイプ']
        target_ok = actual_item['対象'] == expected_item['対象']
        eval_ok = actual_item['評価'] == expected_item['評価']
        detail_ok = actual_item['詳細'] == expected_item['詳細']

        print(f"{j+1}. {expected_item['タイプ']}: "
              f"タイプ{'✅' if type_ok else '❌'} "
              f"対象{'✅' if target_ok else '❌'} "
              f"評価{'✅' if eval_ok else '❌'} "
              f"詳細{'✅' if detail_ok else '❌'}")

        if not (type_ok and target_ok and eval_ok and detail_ok):
            all_tests_passed = False
            if not type_ok:
                print(f"    タイプ不一致: 期待値='{expected_item['タイプ']}', 実際='{actual_item['タイプ']}'")
            if not target_ok:
                print(f"    対象不一致: 期待値='{expected_item['対象']}', 実際='{actual_item['対象']}'")
            if not eval_ok:
                print(f"    評価不一致: 期待値='{expected_item['評価']}', 実際='{actual_item['評価']}'")
            if not detail_ok:
                print(f"    詳細不一致:")
                print(f"      期待値: '{expected_item['詳細']}'")
                print(f"      実際  : '{actual_item['詳細']}'")
    else:
        print(f"{j+1}. {expected_item['タイプ']}: ❌ (項目が見つからない)")
        all_tests_passed = False

# 詳細表示
print("\n抽出された項目:")
for j, item in enumerate(results):
    print(f"  {j+1}. {item['タイプ']} - {item['対象']} - {item['評価']}")
    print(f"     詳細: {item['詳細']}")

print(f"\n{'='*60}")
print(f"🎯 テスト結果: {'✅ 成功' if all_tests_passed else '❌ 失敗'}")
print(f"{'='*60}")

if all_tests_passed:
    print("✅ 五行による鑑定の項目分離が正常に動作しています")
else:
    print("❌ 修正が必要です")