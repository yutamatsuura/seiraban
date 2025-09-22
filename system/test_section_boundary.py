#!/usr/bin/env python3
import re

# Test the updated section boundary regex
sample_raw_text = """
姓名判断結果

文字による鑑定
松  文字の由来・意味から名前には使用しないほうがいい文字です。松  名前には使用できない文字です。

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

print("Testing updated section boundary regex...")
print("=" * 50)

# Test original boundary (which was failing)
old_match = re.search(r'五行による鑑定\s*(.+?)(?:画数による鑑定|$)', sample_raw_text, re.DOTALL)
if old_match:
    old_content = old_match.group(1).strip()
    print("Original boundary regex captured:")
    print(repr(old_content))
    print(f"Length: {len(old_content)}")
    if "松浦 百花【五行のバランス(良)】" in old_content:
        print("✅ Contains second item")
    else:
        print("❌ Missing second item")
    print()

# Test new boundary (should include both items)
new_match = re.search(r'五行による鑑定\s*(.+?)(?:陰陽による鑑定|画数による鑑定|$)', sample_raw_text, re.DOTALL)
if new_match:
    new_content = new_match.group(1).strip()
    print("New boundary regex captured:")
    print(repr(new_content))
    print(f"Length: {len(new_content)}")
    if "松浦 百花【五行のバランス(良)】" in new_content:
        print("✅ Contains second item")
    else:
        print("❌ Missing second item")

    # Check for both items
    lines = new_content.split('\n')
    jinko_found = any("人格：" in line for line in lines)
    balance_found = any("【五行のバランス(良)】" in line for line in lines)

    print(f"人格 pattern found: {'✅' if jinko_found else '❌'}")
    print(f"五行のバランス pattern found: {'✅' if balance_found else '❌'}")

print("\nTest completed!")