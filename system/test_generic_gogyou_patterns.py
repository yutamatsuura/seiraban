#!/usr/bin/env python3
import re

# Test various name patterns to ensure our generic solution works
test_cases = [
    {
        "name": "松浦百花",
        "raw_text": """
五行による鑑定
人格：浦百
【水-水】中年期（28歳～50歳）までの運勢は大凶。人間関係で成したことがすべて流れてしまう。詐欺など人に騙された経験があり人が信用できない。人間関係の広がりがない。また、濃い関係になればなるほどトラブルが起こりやすく、苦労の人生となります。腎臓、肝臓に不調が出やすく、性病にかかりやすいです。

松浦 百花【五行のバランス(良)】
五行のバランスが良く、精神的にも肉体的にも健康的。人との関係性が良く、幸福感に満ちた人生を歩むでしょう。

陰陽による鑑定
"""
    },
    {
        "name": "田中花子",
        "raw_text": """
五行による鑑定
人格：中花
【火-木】中年期の運勢は吉。積極的な性格で人間関係も良好。仕事運に恵まれ、成功を収めやすい。健康面でも問題なく、充実した人生を送れます。

田中 花子【五行のバランス(中)】
五行のバランスは標準的で、安定した人生を歩むでしょう。大きな波乱はありませんが、堅実に歩んでいけます。

陰陽による鑑定
"""
    },
    {
        "name": "山田太郎",
        "raw_text": """
五行による鑑定
人格：田太
【土-金】晩年期の運勢は大吉。忍耐強い性格で、困難を乗り越える力があります。金運に恵まれ、財産を築きやすい。

山田 太郎【五行のバランス(悪)】
五行のバランスが悪く、波乱万丈な人生になりがち。しかし、困難を乗り越えることで大きな成長を遂げます。

陰陽による鑑定
"""
    }
]

def extract_gogyou_section(raw_text):
    """五行による鑑定のセクションを抽出"""
    gogyou_section_match = re.search(r'五行による鑑定\s*(.+?)(?:陰陽による鑑定|画数による鑑定|$)', raw_text, re.DOTALL)
    if gogyou_section_match:
        return gogyou_section_match.group(1).strip()
    return None

def parse_gogyou_items(gogyou_content):
    """五行による鑑定の内容を解析"""
    results = []
    lines = gogyou_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        # パターン1: 人格：XXX
        jinko_match = re.match(r'人格：([^\s]+)', line)
        if jinko_match:
            jinko_value = jinko_match.group(1).strip()

            # 次の行から詳細を探し、【】パターンから評価を抽出
            description_parts = []
            evaluation = jinko_value  # デフォルト
            j = i + 1

            while j < len(lines):
                next_line = lines[j].strip()

                # 新しいパターンが始まったら停止
                if (re.match(r'人格：', next_line) or
                    re.match(r'([一-龯]+)\s+([一-龯]+)【', next_line)):
                    break
                elif next_line:
                    # 【水-水】パターンから評価を抽出
                    bracket_match = re.search(r'【([^】]+)】', next_line)
                    if bracket_match:
                        evaluation = bracket_match.group(1)  # 【水-水】の部分
                        # 【】部分を除去してから詳細に追加
                        clean_line = re.sub(r'【[^】]+】', '', next_line).strip()
                        if clean_line:
                            description_parts.append(clean_line)
                    else:
                        description_parts.append(next_line)

                j += 1

            results.append({
                "タイプ": "人格",
                "対象": f"人格:{jinko_value}",
                "評価": evaluation,
                "詳細": "。".join(description_parts) + "。" if description_parts else ""
            })
            i = j
            continue

        # パターン2: 姓名 pattern (name with 【】)
        name_match = re.match(r'([一-龯]+)\s+([一-龯]+)【([^】]+)】', line)
        if name_match:
            sei = name_match.group(1)
            mei = name_match.group(2)
            label = name_match.group(3)

            # 次の行以降から詳細を収集
            description_parts = []
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()

                # 新しいパターンが始まったら停止
                if (re.match(r'人格：', next_line) or
                    re.match(r'([一-龯]+)\s+([一-龯]+)【', next_line)):
                    break

                if next_line:
                    description_parts.append(next_line)
                j += 1

            results.append({
                "タイプ": "五行のバランス",
                "対象": f"{sei} {mei}",
                "評価": label,
                "詳細": "。".join(description_parts) + "。" if description_parts else ""
            })
            i = j
            continue

        i += 1

    return results

print("Testing generic 五行による鑑定 parsing with multiple name patterns...")
print("=" * 70)

for test_case in test_cases:
    name = test_case["name"]
    raw_text = test_case["raw_text"]

    print(f"\n名前: {name}")
    print("-" * 40)

    # 五行セクションを抽出
    gogyou_content = extract_gogyou_section(raw_text)
    if not gogyou_content:
        print("❌ 五行による鑑定セクションが見つからない")
        continue

    # 解析実行
    results = parse_gogyou_items(gogyou_content)

    print(f"抽出されたアイテム数: {len(results)}")

    for i, item in enumerate(results):
        print(f"{i+1}. タイプ: {item['タイプ']}")
        print(f"   対象: {item['対象']}")
        print(f"   評価: {item['評価']}")
        print(f"   詳細: {item['詳細'][:50]}..." if len(item['詳細']) > 50 else f"   詳細: {item['詳細']}")
        print()

    # 検証
    jinko_items = [item for item in results if item['タイプ'] == '人格']
    balance_items = [item for item in results if item['タイプ'] == '五行のバランス']

    print("検証結果:")
    print(f"  人格アイテム: {len(jinko_items)}個 {'✅' if len(jinko_items) == 1 else '❌'}")
    print(f"  五行のバランスアイテム: {len(balance_items)}個 {'✅' if len(balance_items) == 1 else '❌'}")

    if jinko_items:
        jinko = jinko_items[0]
        # 評価が【】内の値として正しく抽出されているかチェック
        if jinko['評価'] in ['水-水', '火-木', '土-金']:
            print(f"  人格評価抽出: ✅ ({jinko['評価']})")
        else:
            print(f"  人格評価抽出: ❌ ({jinko['評価']})")

        # 詳細に【】が残っていないかチェック
        if '【' not in jinko['詳細']:
            print(f"  詳細クリーニング: ✅")
        else:
            print(f"  詳細クリーニング: ❌ (【】が残っている)")

    if balance_items:
        balance = balance_items[0]
        # 名前が正しく抽出されているかチェック
        if name.replace('', ' ') in balance['対象'] or name[:1] + ' ' + name[1:] in balance['対象']:
            print(f"  名前抽出: ✅ ({balance['対象']})")
        else:
            print(f"  名前抽出: ❌ ({balance['対象']})")

print("\n" + "=" * 70)
print("テスト完了: 異なる名前パターンでの汎用的な解析をテスト")
print("すべてのパターンで人格と五行のバランスの両方が正しく抽出されることを確認")