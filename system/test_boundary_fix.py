#!/usr/bin/env python3
import re

# 実際のユーザーデータのパターンをテスト
actual_data = """
中年期（28歳～50歳）までの運勢は大凶。
人間関係で成したことがすべて流れてしまう。詐欺など人に騙された経験があり人が信用できない。人間関係の広がりがない。また、濃い関係になればなるほどトラブルが起こりやすく、苦労の人生となります。腎臓、肝臓に不調が出やすく、性病にかかりやすいです。
松浦 百花
【五行のバランス(良)】
バランス感覚が良く、判断力に優れています。縁のつかみ方、人間関係作りが上手です。周りの違う考えを受け入れることができます。

陰陽による鑑定
"""

test_with_spaces = f"""
五行による鑑定
人格：浦百
【水-水】{actual_data}
"""

print("テスト: セクション境界の修正")
print("=" * 50)

# 修正前の正規表現
old_pattern = r'五行による鑑定\s*(.+?)(?:陰陽による鑑定|画数による鑑定|$)'
old_match = re.search(old_pattern, test_with_spaces, re.DOTALL)

# 修正後の正規表現
new_pattern = r'五行による鑑定\s*(.+?)(?:\s*陰陽による鑑定|\s*画数による鑑定|$)'
new_match = re.search(new_pattern, test_with_spaces, re.DOTALL)

print("修正前の正規表現で抽出:")
if old_match:
    old_content = old_match.group(1).strip()
    print(f"長さ: {len(old_content)}")
    print(f"内容の最後50文字: ...{old_content[-50:]}")
    if "松浦 百花" in old_content:
        print("✅ 2つ目のアイテムが含まれている")
    else:
        print("❌ 2つ目のアイテムが欠けている")
else:
    print("❌ マッチなし")

print("\n修正後の正規表現で抽出:")
if new_match:
    new_content = new_match.group(1).strip()
    print(f"長さ: {len(new_content)}")
    print(f"内容の最後50文字: ...{new_content[-50:]}")
    if "松浦 百花" in new_content:
        print("✅ 2つ目のアイテムが含まれている")
    else:
        print("❌ 2つ目のアイテムが欠けている")

    # 【五行のバランス(良)】パターンもチェック
    if "【五行のバランス(良)】" in new_content:
        print("✅ 五行のバランス評価も含まれている")
    else:
        print("❌ 五行のバランス評価が欠けている")

    # 完全な詳細もチェック
    if "縁のつかみ方、人間関係作りが上手です" in new_content:
        print("✅ 完全な詳細が含まれている")
    else:
        print("❌ 詳細が不完全")
else:
    print("❌ マッチなし")

print("\n結論:")
if new_match and "松浦 百花" in new_match.group(1) and "【五行のバランス(良)】" in new_match.group(1):
    print("✅ セクション境界の修正により、2つ目のアイテムが正しく抽出できるようになりました")
else:
    print("❌ まだ問題が残っています")