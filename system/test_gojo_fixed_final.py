#!/usr/bin/env python3
import re

# テストケース：五条 めざるの五行解析（最終修正版）
test_text = """
五行による鑑定
人格:条め
【火-水】
中年期（28歳～50歳）までの運勢は大凶。上司や親、従業員と折り合い悪くなりやすいです。熱しやすく、冷めやすい。人生の変化が激しく、物事が壊れやすい。（自分自身で物事を壊しやすい）苦労の人生となります。腎臓 心臓、精神に不調が出やすいです。冷え性になりやすい。五条 めざる 【五行のバランス(良)】 バランス感覚が良く、判断力に優れています。縁のつかみ方、人間関係作りが上手です。周りの違う考えを受け入れることができます。
五条 めざる
【五行のバランス(良)】
バランス感覚が良く、判断力に優れています。縁のつかみ方、人間関係作りが上手です。周りの違う考えを受け入れることができます。

陰陽による鑑定
"""

expected_results = [
    {
        "タイプ": "人格",
        "対象": "人格:条め",
        "評価": "火-水",
        "詳細": "中年期（28歳～50歳）までの運勢は大凶。上司や親、従業員と折り合い悪くなりやすいです。熱しやすく、冷めやすい。人生の変化が激しく、物事が壊れやすい。（自分自身で物事を壊しやすい）苦労の人生となります。腎臓 心臓、精神に不調が出やすいです。冷え性になりやすい。"
    },
    {
        "タイプ": "五行のバランス",
        "対象": "五条 めざる",
        "評価": "五行のバランス(良)",
        "詳細": "バランス感覚が良く、判断力に優れています。縁のつかみ方、人間関係作りが上手です。周りの違う考えを受け入れることができます。"
    }
]

def parse_gogyou_kantei_final_fixed(raw_text):
    """五行による鑑定の最終修正版解析 - コロンの違いを修正"""
    results = []

    # 五行セクションを抽出
    gogyou_section_match = re.search(r'五行による鑑定\s*(.+?)(?:\s*陰陽による鑑定|\s*画数による鑑定|$)', raw_text, re.DOTALL)
    if not gogyou_section_match:
        return results

    gogyou_content = gogyou_section_match.group(1).strip()

    if not gogyou_content or len(gogyou_content) <= 10:
        return results

    print(f"原文:\n{gogyou_content}\n")

    # パターン1: 人格の抽出 - 半角コロンに修正
    jinko_pattern = r'人格:([^\s\n]+)\s*\n?\s*【([^】]+)】\s*(.*?)(?=(?:[\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+\s+[\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+\s*\n?\s*【)|$)'
    jinko_match = re.search(jinko_pattern, gogyou_content, re.DOTALL)
    if jinko_match:
        jinko_value = jinko_match.group(1)
        evaluation = jinko_match.group(2)
        content = jinko_match.group(3).strip()

        # 文中に名前パターンが混入している場合は除去
        content_lines = content.split('\n')
        clean_lines = []
        for line in content_lines:
            line = line.strip()
            # 日本語名前パターンを含む行をスキップ
            if re.search(r'[\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+\s+[\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+\s*【', line):
                break
            if line:
                clean_lines.append(line)

        clean_content = ' '.join(clean_lines).strip()

        print(f"人格詳細（最終版）: '{clean_content}'")

        results.append({
            "タイプ": "人格",
            "対象": f"人格:{jinko_value}",
            "評価": evaluation,
            "詳細": clean_content
        })

    # パターン2: 五行のバランス - 最初に現れる名前パターンを取得
    name_pattern = r'([\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+)\s+([\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+)\s*\n?\s*【([^】]+)】\s*(.*?)(?=(?:([\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+)\s+([\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+)\s*\n?\s*【)|$)'
    name_match = re.search(name_pattern, gogyou_content, re.DOTALL)
    if name_match:
        sei = name_match.group(1)
        mei = name_match.group(2)
        name_evaluation = name_match.group(3)
        content = name_match.group(4).strip()

        # 次の同名パターンが現れる前まで取得し、不要な重複を除去
        content_lines = content.split('\n')
        clean_lines = []
        skip_rest = False
        for line in content_lines:
            line = line.strip()
            # 同じ名前が再度現れた場合は以降をスキップ
            if f"{sei} {mei}" in line and "【" in line and not skip_rest:
                skip_rest = True
                continue
            if not skip_rest and line:
                clean_lines.append(line)

        clean_content = ' '.join(clean_lines).strip()

        print(f"五行のバランス詳細（最終版）: '{clean_content}'")

        results.append({
            "タイプ": "五行のバランス",
            "対象": f"{sei} {mei}",
            "評価": name_evaluation,
            "詳細": clean_content
        })

    return results

print("五条 めざるの五行による鑑定の分離テスト（最終修正版）")
print("=" * 70)

# 解析実行
results = parse_gogyou_kantei_final_fixed(test_text)
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

print(f"\n{'='*70}")
print(f"🎯 テスト結果: {'✅ 成功' if all_tests_passed else '❌ 失敗'}")
print(f"{'='*70}")

if all_tests_passed:
    print("✅ 五条 めざるケースの五行による鑑定の項目分離が正常に動作しています")
else:
    print("❌ 修正が必要です")