#!/usr/bin/env python3
import re

# テストケース1: 総格のみ（上原 はま）
uehara_hama_text = """
画数による鑑定
総格:上原 はま
【画数17】
権威。剛直、豪気、強情。善悪をハッキリし、物事の白黒をつけることに性急、ここに短気のもとが生じる。人の反対を押して自己の意志を貫徹し、ついには成功する。ジックリと努力すれば幸福となろう。色恋の情が強いので注意。

陰陽による鑑定
"""

# テストケース2: 総格と人格（渡井 ぽん）
watai_pon_text = """
画数による鑑定
総格:渡井 ぽん
【画数23】
頭領。知あって一躍大成功する。大志大望を抱いてそれを実現する大吉数、努力家は多い。女性は自己主張を除いて、やさしく生きることが幸福の条件。手八丁口八丁の器用もの。大吉人生だ。
人格:井 ぽ
【画数9】
孤独滅亡。何事に対しても苦境に陥る。努力は報われず、孤独滅亡。身体に障害を得やすく、肉親に縁薄い。しかし忍耐は人一倍強く、それがかえって孤独を強める。妥協を許さず、衝突は多い。

陰陽による鑑定
"""

# テストケース3: 総格と地格（五条 めざる）
gojo_mezaru_text = """
画数による鑑定
総格:五条 めざる
【画数24】
忍耐。正名の人は人を統率し、苦労するも大成功を収める。無から有を生じる吉数。俗に「嫁にもらうと倉が建つ」という。凶名の人は、財産、人生など、ことごとく無とする数である。
地格:めざる
【画数9】
孤独滅亡。何事に対しても苦境に陥る。努力は報われず、孤独滅亡。身体に障害を得やすく、肉親に縁薄い。しかし忍耐は人一倍強く、それがかえって孤独を強める。妥協を許さず、衝突は多い。

陰陽による鑑定
"""

def parse_kakusu_kantei_enhanced(raw_text):
    """画数による鑑定の包括的解析"""
    results = []

    # 画数セクションを抽出
    kakusu_section_match = re.search(r'画数による鑑定\s*(.+?)(?:\s*陰陽による鑑定|$)', raw_text, re.DOTALL)
    if not kakusu_section_match:
        return results

    kakusu_content = kakusu_section_match.group(1).strip()

    if not kakusu_content or len(kakusu_content) <= 10:
        return results

    # パターン1: 総格の抽出
    # 総格:上原 はま【画数17】権威。剛直...
    sou_pattern = r'総格:\s*([^【\n]+)\s*【画数(\d+)】\s*(.*?)(?=人格:|$)'
    sou_match = re.search(sou_pattern, kakusu_content, re.DOTALL)

    if sou_match:
        name_part = sou_match.group(1).strip()
        kakusu = sou_match.group(2)
        content = sou_match.group(3).strip()

        results.append({
            "タイプ": "総格",
            "対象": name_part,
            "画数": f"{kakusu}画",
            "詳細": content
        })

    # パターン2: 人格の抽出
    # 人格:井 ぽ【画数9】孤独滅亡...
    jin_pattern = r'人格:\s*([^【\n]+)\s*【画数(\d+)】\s*(.*?)(?=総格:|地格:|陰陽による鑑定|$)'
    jin_match = re.search(jin_pattern, kakusu_content, re.DOTALL)

    if jin_match:
        name_part = jin_match.group(1).strip()
        kakusu = jin_match.group(2)
        content = jin_match.group(3).strip()

        results.append({
            "タイプ": "人格",
            "対象": name_part,
            "画数": f"{kakusu}画",
            "詳細": content
        })

    # パターン3: 地格の抽出
    # 地格:めざる【画数9】孤独滅亡...
    chi_pattern = r'地格:\s*([^【\n]+)\s*【画数(\d+)】\s*(.*?)(?=総格:|人格:|陰陽による鑑定|$)'
    chi_match = re.search(chi_pattern, kakusu_content, re.DOTALL)

    if chi_match:
        name_part = chi_match.group(1).strip()
        kakusu = chi_match.group(2)
        content = chi_match.group(3).strip()

        results.append({
            "タイプ": "地格",
            "対象": name_part,
            "画数": f"{kakusu}画",
            "詳細": content
        })

    return results

print("画数による鑑定の包括的テスト")
print("=" * 60)

# テストケース1: 総格のみ
print("\n📝 テストケース1: 総格のみ（上原 はま）")
print("-" * 40)
results1 = parse_kakusu_kantei_enhanced(uehara_hama_text)

print(f"抽出されたアイテム数: {len(results1)}")
for i, item in enumerate(results1):
    print(f"{i+1}. タイプ: {item['タイプ']}")
    print(f"   対象: {item['対象']}")
    print(f"   画数: {item['画数']}")
    print(f"   詳細: {item['詳細'][:60]}...")
    print()

# 検証
sou_items1 = [item for item in results1 if item['タイプ'] == '総格']
jin_items1 = [item for item in results1 if item['タイプ'] == '人格']

print("📊 検証結果:")
print(f"  総格アイテム: {len(sou_items1)}個 {'✅' if len(sou_items1) == 1 else '❌'}")
print(f"  人格アイテム: {len(jin_items1)}個 {'✅' if len(jin_items1) == 0 else '❌'}")

if sou_items1:
    sou = sou_items1[0]
    print(f"  総格対象: '{sou['対象']}' {'✅' if '上原 はま' in sou['対象'] else '❌'}")
    print(f"  総格画数: {sou['画数']} {'✅' if sou['画数'] == '17画' else '❌'}")

print("\n" + "=" * 60)

# テストケース2: 総格と人格
print("\n📝 テストケース2: 総格と人格（渡井 ぽん）")
print("-" * 40)
results2 = parse_kakusu_kantei_enhanced(watai_pon_text)

print(f"抽出されたアイテム数: {len(results2)}")
for i, item in enumerate(results2):
    print(f"{i+1}. タイプ: {item['タイプ']}")
    print(f"   対象: {item['対象']}")
    print(f"   画数: {item['画数']}")
    print(f"   詳細: {item['詳細'][:60]}...")
    print()

# 検証
sou_items2 = [item for item in results2 if item['タイプ'] == '総格']
jin_items2 = [item for item in results2 if item['タイプ'] == '人格']

print("📊 検証結果:")
print(f"  総格アイテム: {len(sou_items2)}個 {'✅' if len(sou_items2) == 1 else '❌'}")
print(f"  人格アイテム: {len(jin_items2)}個 {'✅' if len(jin_items2) == 1 else '❌'}")

if sou_items2:
    sou = sou_items2[0]
    print(f"  総格対象: '{sou['対象']}' {'✅' if '渡井 ぽん' in sou['対象'] else '❌'}")
    print(f"  総格画数: {sou['画数']} {'✅' if sou['画数'] == '23画' else '❌'}")

if jin_items2:
    jin = jin_items2[0]
    print(f"  人格対象: '{jin['対象']}' {'✅' if '井 ぽ' in jin['対象'] else '❌'}")
    print(f"  人格画数: {jin['画数']} {'✅' if jin['画数'] == '9画' else '❌'}")

print("\n" + "=" * 60)

# テストケース3: 総格と地格
print("\n📝 テストケース3: 総格と地格（五条 めざる）")
print("-" * 40)
results3 = parse_kakusu_kantei_enhanced(gojo_mezaru_text)

print(f"抽出されたアイテム数: {len(results3)}")
for i, item in enumerate(results3):
    print(f"{i+1}. タイプ: {item['タイプ']}")
    print(f"   対象: {item['対象']}")
    print(f"   画数: {item['画数']}")
    print(f"   詳細: {item['詳細'][:60]}...")
    print()

# 検証
sou_items3 = [item for item in results3 if item['タイプ'] == '総格']
jin_items3 = [item for item in results3 if item['タイプ'] == '人格']
chi_items3 = [item for item in results3 if item['タイプ'] == '地格']

print("📊 検証結果:")
print(f"  総格アイテム: {len(sou_items3)}個 {'✅' if len(sou_items3) == 1 else '❌'}")
print(f"  人格アイテム: {len(jin_items3)}個 {'✅' if len(jin_items3) == 0 else '❌'}")
print(f"  地格アイテム: {len(chi_items3)}個 {'✅' if len(chi_items3) == 1 else '❌'}")

if sou_items3:
    sou = sou_items3[0]
    print(f"  総格対象: '{sou['対象']}' {'✅' if '五条 めざる' in sou['対象'] else '❌'}")
    print(f"  総格画数: {sou['画数']} {'✅' if sou['画数'] == '24画' else '❌'}")

if chi_items3:
    chi = chi_items3[0]
    print(f"  地格対象: '{chi['対象']}' {'✅' if 'めざる' in chi['対象'] else '❌'}")
    print(f"  地格画数: {chi['画数']} {'✅' if chi['画数'] == '9画' else '❌'}")

total_success = (len(sou_items1) == 1 and len(jin_items1) == 0 and
                 len(sou_items2) == 1 and len(jin_items2) == 1 and
                 len(sou_items3) == 1 and len(jin_items3) == 0 and len(chi_items3) == 1)

print(f"\n🎯 総合テスト結果: {'✅ 成功' if total_success else '❌ 失敗'}")
print("\n目標:")
print("- ケース1: 総格のみ正しく抽出")
print("- ケース2: 総格と人格の両方を正しく抽出")
print("- ケース3: 総格と地格の両方を正しく抽出")
print("- 各アイテムの対象、画数、詳細が正確に分離されている")