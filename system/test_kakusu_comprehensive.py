#!/usr/bin/env python3
import re

# 包括的テストケース
test_cases = [
    {
        "name": "総格のみ (上原 はま)",
        "text": """
画数による鑑定
総格:上原 はま
【画数17】
権威。剛直、豪気、強情。善悪をハッキリし、物事の白黒をつけることに性急、ここに短気のもとが生じる。人の反対を押して自己の意志を貫徹し、ついには成功する。ジックリと努力すれば幸福となろう。色恋の情が強いので注意。

陰陽による鑑定
""",
        "expected": [
            {"タイプ": "総格", "対象": "上原 はま", "画数": "17画"}
        ]
    },
    {
        "name": "総格と人格 (渡井 ぽん)",
        "text": """
画数による鑑定
総格:渡井 ぽん
【画数23】
頭領。知あって一躍大成功する。大志大望を抱いてそれを実現する大吉数、努力家は多い。女性は自己主張を除いて、やさしく生きることが幸福の条件。手八丁口八丁の器用もの。大吉人生だ。
人格:井 ぽ
【画数9】
孤独滅亡。何事に対しても苦境に陥る。努力は報われず、孤独滅亡。身体に障害を得やすく、肉親に縁薄い。しかし忍耐は人一倍強く、それがかえって孤独を強める。妥協を許さず、衝突は多い。

陰陽による鑑定
""",
        "expected": [
            {"タイプ": "総格", "対象": "渡井 ぽん", "画数": "23画"},
            {"タイプ": "人格", "対象": "井 ぽ", "画数": "9画"}
        ]
    },
    {
        "name": "総格と地格 (五条 めざる)",
        "text": """
画数による鑑定
総格:五条 めざる
【画数24】
忍耐。正名の人は人を統率し、苦労するも大成功を収める。無から有を生じる吉数。俗に「嫁にもらうと倉が建つ」という。凶名の人は、財産、人生など、ことごとく無とする数である。
地格:めざる
【画数9】
孤独滅亡。何事に対しても苦境に陥る。努力は報われず、孤独滅亡。身体に障害を得やすく、肉親に縁薄い。しかし忍耐は人一倍強く、それがかえって孤独を強める。妥協を許さず、衝突は多い。

陰陽による鑑定
""",
        "expected": [
            {"タイプ": "総格", "対象": "五条 めざる", "画数": "24画"},
            {"タイプ": "地格", "対象": "めざる", "画数": "9画"}
        ]
    },
    {
        "name": "問題ケース (京極 初め) - 混在テキスト",
        "text": """
画数による鑑定
総格:京極 初め
【画数30】
自力発展。積極的に努力し建設の才あり。あらゆるものに工夫を加えて物事を進める。正名の場合は幸福を得る数である。選名に吉。晩年は孤独になりやすいので、精神的に豊かな生活を心がけること。凶名は努力が報われず失意の人生となる。地格:初め
【画数9】
孤独滅亡。何事に対しても苦境に陥る。努力は報われず、孤独滅亡。身体に障害を得やすく、肉親に縁薄い。しかし忍耐は人一倍強く、それがかえって孤独を強める。妥協を許さず、衝突は多い。

陰陽による鑑定
""",
        "expected": [
            {"タイプ": "総格", "対象": "京極 初め", "画数": "30画"},
            {"タイプ": "地格", "対象": "初め", "画数": "9画"}
        ]
    }
]

def parse_kakusu_kantei_enhanced(raw_text):
    """画数による鑑定の修正版解析 - 項目分離を改善"""
    results = []

    # 画数セクションを抽出
    kakusu_section_match = re.search(r'画数による鑑定\s*(.+?)(?:\s*陰陽による鑑定|$)', raw_text, re.DOTALL)
    if not kakusu_section_match:
        return results

    kakusu_content = kakusu_section_match.group(1).strip()

    if not kakusu_content or len(kakusu_content) <= 10:
        return results

    # 全てのパターン（総格、人格、地格）を順序で検索
    patterns = [
        (r'総格:\s*([^【\n]+)\s*【画数(\d+)】\s*(.*?)(?=(?:人格:|地格:)|$)', "総格"),
        (r'人格:\s*([^【\n]+)\s*【画数(\d+)】\s*(.*?)(?=(?:総格:|地格:)|$)', "人格"),
        (r'地格:\s*([^【\n]+)\s*【画数(\d+)】\s*(.*?)(?=(?:総格:|人格:)|$)', "地格")
    ]

    for pattern, type_name in patterns:
        matches = re.finditer(pattern, kakusu_content, re.DOTALL)
        for match in matches:
            name_part = match.group(1).strip()
            kakusu = match.group(2)
            content = match.group(3).strip()

            # 次のパターンが混入している場合は除去
            # 例: 地格:初め が総格の詳細に含まれている場合
            next_pattern_match = re.search(r'(総格:|人格:|地格:)', content)
            if next_pattern_match:
                # 次のパターンが見つかった位置で切り取る
                cut_position = next_pattern_match.start()
                content = content[:cut_position].strip()

            results.append({
                "タイプ": type_name,
                "対象": name_part,
                "画数": f"{kakusu}画",
                "詳細": content
            })

    return results

print("画数による鑑定の包括的テスト（修正版）")
print("=" * 70)

all_tests_passed = True

for i, test_case in enumerate(test_cases):
    print(f"\n📝 テストケース{i+1}: {test_case['name']}")
    print("-" * 50)

    # 解析実行
    results = parse_kakusu_kantei_enhanced(test_case['text'])
    expected = test_case['expected']

    print(f"抽出されたアイテム数: {len(results)} (期待値: {len(expected)})")

    # 基本チェック
    items_count_ok = len(results) == len(expected)
    print(f"  アイテム数: {'✅' if items_count_ok else '❌'}")

    if not items_count_ok:
        all_tests_passed = False

    # 各アイテムの詳細チェック
    for j, expected_item in enumerate(expected):
        if j < len(results):
            actual_item = results[j]

            type_ok = actual_item['タイプ'] == expected_item['タイプ']
            target_ok = actual_item['対象'] == expected_item['対象']
            kakusu_ok = actual_item['画数'] == expected_item['画数']

            # 詳細に他の項目が混入していないかチェック
            content_clean = True
            for check_type in ['総格:', '人格:', '地格:']:
                if check_type != f"{expected_item['タイプ']}:" and check_type in actual_item['詳細']:
                    content_clean = False
                    break

            print(f"  {j+1}. {expected_item['タイプ']}: "
                  f"タイプ{'✅' if type_ok else '❌'} "
                  f"対象{'✅' if target_ok else '❌'} "
                  f"画数{'✅' if kakusu_ok else '❌'} "
                  f"内容クリーン{'✅' if content_clean else '❌'}")

            if not (type_ok and target_ok and kakusu_ok and content_clean):
                all_tests_passed = False
                if not type_ok:
                    print(f"    タイプ不一致: 期待値='{expected_item['タイプ']}', 実際='{actual_item['タイプ']}'")
                if not target_ok:
                    print(f"    対象不一致: 期待値='{expected_item['対象']}', 実際='{actual_item['対象']}'")
                if not kakusu_ok:
                    print(f"    画数不一致: 期待値='{expected_item['画数']}', 実際='{actual_item['画数']}'")
                if not content_clean:
                    print(f"    詳細に他項目混入: '{actual_item['詳細'][:50]}...'")
        else:
            print(f"  {j+1}. {expected_item['タイプ']}: ❌ (項目が見つからない)")
            all_tests_passed = False

    # 詳細表示
    print("\n  抽出された項目:")
    for j, item in enumerate(results):
        print(f"    {j+1}. {item['タイプ']} - {item['対象']} - {item['画数']}")
        print(f"       詳細: {item['詳細'][:50]}{'...' if len(item['詳細']) > 50 else ''}")

print(f"\n{'='*70}")
print(f"🎯 総合テスト結果: {'✅ 全テスト成功' if all_tests_passed else '❌ 一部テスト失敗'}")
print(f"{'='*70}")

if all_tests_passed:
    print("✅ 修正版画数による鑑定解析が正常に動作しています")
    print("✅ 項目分離が正しく行われています")
    print("✅ 全パターン（総格、人格、地格）に対応しています")
else:
    print("❌ 修正が必要です")