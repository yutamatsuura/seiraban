#!/usr/bin/env python3
import re
import json

# Sample raw text for 松浦百花 that contains 五行による鑑定 section
sample_raw_text = """
姓名判断結果

文字による鑑定
松  文字の由来・意味から名前には使用しないほうがいい文字です。松  名前には使用できない文字です。

浦  文字の由来・意味から名前には使用しないほうがいい文字です。浦  名前には使用できない文字です。

百  文字の由来・意味から名前には使用しないほうがいい文字です。百  名前には使用できない文字です。

花  文字の由来・意味から名前には使用しないほうがいい文字です。花  名前には使用できない文字です。人生に実り少なく早く枯れてしまう。または変化に翻弄され苦労の連続となりがちです。

五行による鑑定
人格：浦百
五行のバランスは浦百(水-水)の持つ性質により、何事も溜め込みやすい性格です。ガンをはじめとする病気で長生きが出やすく、性病にかかりやすいです。

松浦 百花【五行のバランス(良)】
五行のバランスが良く、精神的にも肉体的にも健康的。人との関係性が良く、幸福感に満ちた人生を歩むでしょう。

陰陽による鑑定
松浦 百花【黒の方寄り】
名前の陰陽バランスは黒の方に寄っています。陰陽のバランスが悪く、性格的に内向的になりがちです。

画数による鑑定
総格: 25画
"""

print("Testing 五行による鑑定 parsing...")
print("=" * 50)

# Extract 五行による鑑定 section
gogyou_section_match = re.search(r'五行による鑑定\s*(.+?)(?:画数による鑑定|$)', sample_raw_text, re.DOTALL)
if gogyou_section_match:
    gogyou_content = gogyou_section_match.group(1).strip()
    print(f"Raw 五行 section extracted:")
    print(repr(gogyou_content))
    print()

    lines = gogyou_content.split('\n')
    print(f"Lines in 五行 section: {len(lines)}")
    for i, line in enumerate(lines):
        print(f"  {i}: {repr(line.strip())}")
    print()

    # Parse using updated backend logic
    gogyou_items = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        print(f"Processing line {i}: {repr(line)}")

        if not line:
            print("  → Empty line, skipping")
            i += 1
            continue

        # Pattern 1: 人格：XXX
        jinko_match = re.match(r'人格：([^\s]+)', line)
        if jinko_match:
            jinko_value = jinko_match.group(1).strip()
            print(f"  ✓ Found 人格 pattern: {jinko_value}")

            # 次の行から詳細を探し、(水-水)パターンから評価を抽出
            description_parts = []
            evaluation = jinko_value  # デフォルト
            j = i + 1

            while j < len(lines):
                next_line = lines[j].strip()
                print(f"    Checking next line {j}: {repr(next_line)}")

                # 新しいパターンが始まったら停止
                if re.match(r'人格：', next_line) or re.match(r'([一-龯]+)\s+([一-龯]+)【', next_line):
                    print(f"    → Found new pattern, breaking")
                    break
                elif next_line:
                    # (水-水)パターンから評価を抽出
                    gogyou_match = re.search(r'([一-龯]+)\(([^)]+)\)', next_line)
                    if gogyou_match:
                        evaluation = gogyou_match.group(2)  # (水-水)の部分
                        print(f"    → Found gogyou evaluation: {evaluation}")
                    description_parts.append(next_line)
                    print(f"    → Added to description: {next_line}")

                j += 1

            gogyou_items.append({
                "分類": "人格",
                "ラベル": evaluation,
                "詳細": "。".join(description_parts) + "。" if description_parts else ""
            })
            i = j
            continue

        # Pattern 2: 姓名 pattern (name with 【】)
        name_match = re.match(r'([一-龯]+)\s+([一-龯]+)【([^】]+)】', line)
        if name_match:
            sei = name_match.group(1)
            mei = name_match.group(2)
            label = name_match.group(3)
            print(f"  ✓ Found name pattern: {sei} {mei} 【{label}】")

            # Get description from next lines
            description_parts = []
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                print(f"    Checking next line {j}: {repr(next_line)}")

                # Stop if we hit another pattern
                if re.match(r'人格：', next_line) or re.match(r'([一-龯]+)\s+([一-龯]+)【', next_line):
                    print(f"    → Found new pattern, breaking")
                    break
                else:
                    if next_line:
                        description_parts.append(next_line)
                        print(f"    → Added to description: {next_line}")
                    j += 1

            gogyou_items.append({
                "分類": "五行のバランス",
                "ラベル": label,
                "詳細": "。".join(description_parts) + "。" if description_parts else ""
            })
            i = j
            continue

        print(f"  ✗ No pattern matched for line: {repr(line)}")
        i += 1

    print()
    print("Final 五行による鑑定 items:")
    for i, item in enumerate(gogyou_items):
        print(f"{i+1}. 分類: {item['分類']}")
        print(f"   ラベル: {item['ラベル']}")
        print(f"   詳細: {item['詳細']}")
        print()

    print(f"Total items extracted: {len(gogyou_items)}")

    # Test if we're getting both expected items
    jinko_items = [item for item in gogyou_items if item['分類'] == '人格']
    balance_items = [item for item in gogyou_items if item['分類'] == '五行のバランス']

    print(f"人格 items: {len(jinko_items)}")
    print(f"五行のバランス items: {len(balance_items)}")

    if jinko_items:
        print(f"人格 content: {jinko_items[0]['詳細']}")
        if "松浦。" in jinko_items[0]['詳細']:
            print("❌ PROBLEM: Content is still truncated at '松浦。'")
        else:
            print("✅ 人格 content looks complete")
        print(f"人格 evaluation: {jinko_items[0]['ラベル']}")
        if jinko_items[0]['ラベル'] == "水-水":
            print("✅ 人格 evaluation correctly extracted as '水-水'")
        else:
            print(f"❌ 人格 evaluation should be '水-水', got '{jinko_items[0]['ラベル']}'")

    if balance_items:
        print(f"五行のバランス content: {balance_items[0]['詳細']}")

else:
    print("❌ Could not extract 五行による鑑定 section")