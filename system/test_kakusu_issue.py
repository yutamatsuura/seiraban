#!/usr/bin/env python3
import re

# 実際の問題となっているケース
kyogoku_hajime_text = """
画数による鑑定
総格:京極 初め
【画数30】
自力発展。積極的に努力し建設の才あり。あらゆるものに工夫を加えて物事を進める。正名の場合は幸福を得る数である。選名に吉。晩年は孤独になりやすいので、精神的に豊かな生活を心がけること。凶名は努力が報われず失意の人生となる。地格:初め
【画数9】
孤独滅亡。何事に対しても苦境に陥る。努力は報われず、孤独滅亡。身体に障害を得やすく、肉親に縁薄い。しかし忍耐は人一倍強く、それがかえって孤独を強める。妥協を許さず、衝突は多い。

陰陽による鑑定
"""

def parse_kakusu_kantei_fixed(raw_text):
    """画数による鑑定の修正版解析"""
    results = []

    # 画数セクションを抽出
    kakusu_section_match = re.search(r'画数による鑑定\s*(.+?)(?:\s*陰陽による鑑定|$)', raw_text, re.DOTALL)
    if not kakusu_section_match:
        return results

    kakusu_content = kakusu_section_match.group(1).strip()

    if not kakusu_content or len(kakusu_content) <= 10:
        return results

    print(f"DEBUG: 画数セクション内容:\n{kakusu_content}\n")

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

            print(f"DEBUG: {type_name}マッチ:")
            print(f"  name_part: '{name_part}'")
            print(f"  kakusu: '{kakusu}'")
            print(f"  content: '{content[:100]}...'")
            print()

            # 次のパターンが混入している場合は除去
            # 例: 地格:初め が総格の詳細に含まれている場合
            next_pattern_match = re.search(r'(総格:|人格:|地格:)', content)
            if next_pattern_match:
                # 次のパターンが見つかった位置で切り取る
                cut_position = next_pattern_match.start()
                content = content[:cut_position].strip()
                print(f"DEBUG: {type_name}の詳細を切り取り: '{content[:50]}...'")

            results.append({
                "タイプ": type_name,
                "対象": name_part,
                "画数": f"{kakusu}画",
                "詳細": content
            })

    return results

print("画数による鑑定の問題ケーステスト")
print("=" * 60)

print("🔍 現在の問題ケース: 京極 初め")
print("-" * 40)

# 現在の問題ケースをテスト
results = parse_kakusu_kantei_fixed(kyogoku_hajime_text)

print(f"抽出されたアイテム数: {len(results)}")
for i, item in enumerate(results):
    print(f"{i+1}. タイプ: {item['タイプ']}")
    print(f"   対象: {item['対象']}")
    print(f"   画数: {item['画数']}")
    print(f"   詳細: {item['詳細']}")
    print()

# 期待される結果と比較
expected_results = [
    {
        "タイプ": "総格",
        "対象": "京極 初め",
        "画数": "30画",
        "詳細": "自力発展。積極的に努力し建設の才あり。あらゆるものに工夫を加えて物事を進める。正名の場合は幸福を得る数である。選名に吉。晩年は孤独になりやすいので、精神的に豊かな生活を心がけること。凶名は努力が報われず失意の人生となる。"
    },
    {
        "タイプ": "地格",
        "対象": "初め",
        "画数": "9画",
        "詳細": "孤独滅亡。何事に対しても苦境に陥る。努力は報われず、孤独滅亡。身体に障害を得やすく、肉親に縁薄い。しかし忍耐は人一倍強く、それがかえって孤独を強める。妥協を許さず、衝突は多い。"
    }
]

print("📊 検証結果:")
print(f"  抽出アイテム数: {len(results)}個 {'✅' if len(results) == 2 else '❌'}")

if len(results) >= 1:
    actual_sou = results[0]
    expected_sou = expected_results[0]
    print(f"  総格対象: '{actual_sou['対象']}' {'✅' if actual_sou['対象'] == expected_sou['対象'] else '❌'}")
    print(f"  総格画数: {actual_sou['画数']} {'✅' if actual_sou['画数'] == expected_sou['画数'] else '❌'}")

    # 詳細内容に地格の情報が混入していないかチェック
    sou_clean = "地格:" not in actual_sou['詳細']
    print(f"  総格詳細クリーン: {'✅' if sou_clean else '❌'} (地格情報が混入していない)")

if len(results) >= 2:
    actual_chi = results[1]
    expected_chi = expected_results[1]
    print(f"  地格対象: '{actual_chi['対象']}' {'✅' if actual_chi['対象'] == expected_chi['対象'] else '❌'}")
    print(f"  地格画数: {actual_chi['画数']} {'✅' if actual_chi['画数'] == expected_chi['画数'] else '❌'}")

success = (
    len(results) == 2 and
    results[0]['対象'] == expected_results[0]['対象'] and
    results[0]['画数'] == expected_results[0]['画数'] and
    "地格:" not in results[0]['詳細'] and
    results[1]['対象'] == expected_results[1]['対象'] and
    results[1]['画数'] == expected_results[1]['画数']
)

print(f"\n🎯 修正テスト結果: {'✅ 成功' if success else '❌ 失敗'}")