#!/usr/bin/env python3
import re

# Test case for complete 3-item extraction including 地格
uehara_hama_text = """
五行による鑑定
地格：はま
【水-水】
生まれてから27歳までの運勢は凶命。
自分個人でやったことが全部流れてしまう。体が弱く、精神的にも不安定になりがち、真面目で人は良く、悪い人に騙され染まりやすい。寂しい。頭は良いが、不正、盗みをしがち。経済苦に陥りやすく、苦労の人生となります。腎臓、肝臓に不調が出やすく、性病にかかりやすいです。
人格：原は
【木-水】
中年期（28歳～50歳）までの運勢。
活発で社交的で判断力、理解力に優れています。
上原 はま
【五行のバランス(良)】
バランス感覚が良く、判断力に優れています。縁のつかみ方、人間関係作りが上手です。周りの違う考えを受け入れることができます。

陰陽による鑑定
"""

def parse_gogyou_enhanced(raw_text):
    """Enhanced parsing logic to extract all 3 items including 地格"""
    results = []

    # 五行セクションを抽出
    gogyou_section_match = re.search(r'五行による鑑定\s*(.+?)(?:\s*陰陽による鑑定|\s*画数による鑑定|$)', raw_text, re.DOTALL)
    if not gogyou_section_match:
        return results

    gogyou_content = gogyou_section_match.group(1).strip()

    if not gogyou_content or len(gogyou_content) <= 10:
        return results

    # まず名前パターンを検索して姓を動的に検出
    name_pattern = r'([一-龯あ-ゖア-ヶ]+)\s+([一-龯あ-ゖア-ヶ]+)\s*\n?\s*【([^】]+)】'
    name_match = re.search(name_pattern, gogyou_content)

    if name_match:
        sei = name_match.group(1)
        mei = name_match.group(2)
        name_evaluation = name_match.group(3)

        # パターン1: 地格 - 新たに追加
        chikaku_pattern = r'地格：([^\s]+)\s*\n?\s*【([^】]+)】\s*(.*?)(?=人格：|(?=' + re.escape(sei) + r'))'
        chikaku_match = re.search(chikaku_pattern, gogyou_content, re.DOTALL)
        if chikaku_match:
            chikaku_value = chikaku_match.group(1)
            evaluation = chikaku_match.group(2)
            content = chikaku_match.group(3).strip()

            results.append({
                "タイプ": "地格",
                "対象": f"地格:{chikaku_value}",
                "評価": evaluation,
                "詳細": content
            })

        # パターン2: 人格 - 動的に検出された姓を使用
        jinko_pattern = rf'人格：([^\s]+)\s*\n?\s*【([^】]+)】\s*(.*?)(?={re.escape(sei)})'
        jinko_match = re.search(jinko_pattern, gogyou_content, re.DOTALL)
        if jinko_match:
            jinko_value = jinko_match.group(1)
            evaluation = jinko_match.group(2)
            content = jinko_match.group(3).strip()

            results.append({
                "タイプ": "人格",
                "対象": f"人格:{jinko_value}",
                "評価": evaluation,
                "詳細": content
            })

        # パターン3: 五行のバランス - 名前の詳細を取得
        name_detail_pattern = rf'{re.escape(sei)}\s+{re.escape(mei)}\s*\n?\s*【[^】]+】\s*(.*?)(?=陰陽による鑑定|画数による鑑定|$)'
        name_detail_match = re.search(name_detail_pattern, gogyou_content, re.DOTALL)
        if name_detail_match:
            content = name_detail_match.group(1).strip()
        else:
            content = ""

        results.append({
            "タイプ": "五行のバランス",
            "対象": f"{sei} {mei}",
            "評価": name_evaluation,
            "詳細": content
        })

    return results

print("Enhanced 3-Item Extraction Test")
print("=" * 60)

results = parse_gogyou_enhanced(uehara_hama_text)

print(f"抽出されたアイテム数: {len(results)}")
print()

for i, item in enumerate(results):
    print(f"{i+1}. タイプ: {item['タイプ']}")
    print(f"   対象: {item['対象']}")
    print(f"   評価: {item['評価']}")
    print(f"   詳細: {item['詳細'][:80]}...")
    print()

# 検証
chikaku_items = [item for item in results if item['タイプ'] == '地格']
jinko_items = [item for item in results if item['タイプ'] == '人格']
balance_items = [item for item in results if item['タイプ'] == '五行のバランス']

print("📊 検証結果:")
print(f"  地格アイテム: {len(chikaku_items)}個 {'✅' if len(chikaku_items) == 1 else '❌'}")
print(f"  人格アイテム: {len(jinko_items)}個 {'✅' if len(jinko_items) == 1 else '❌'}")
print(f"  五行のバランスアイテム: {len(balance_items)}個 {'✅' if len(balance_items) == 1 else '❌'}")

total_success = len(chikaku_items) == 1 and len(jinko_items) == 1 and len(balance_items) == 1
print(f"  総合: {'✅ 成功' if total_success else '❌ 失敗'}")

if chikaku_items:
    chikaku = chikaku_items[0]
    print(f"  地格評価: {chikaku['評価']} {'✅' if chikaku['評価'] == '水-水' else '❌'}")

if jinko_items:
    jinko = jinko_items[0]
    print(f"  人格評価: {jinko['評価']} {'✅' if jinko['評価'] == '木-水' else '❌'}")

if balance_items:
    balance = balance_items[0]
    print(f"  五行のバランス評価: {balance['評価']} {'✅' if '五行のバランス' in balance['評価'] else '❌'}")

print(f"\n{'=' * 60}")
print("目標: 地格・人格・五行のバランスの3つのアイテムを正確に抽出")