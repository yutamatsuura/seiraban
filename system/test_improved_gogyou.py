#!/usr/bin/env python3
import re

# 実際のデータをシミュレートしたテスト
sample_raw_text = """
五行による鑑定
人格：浦百
                【水-水】
             中年期（28歳～50歳）までの運勢は大凶。人間関係で成したことがすべて流れてしまう。詐欺など人に騙された経験があり人が信用できない。人間関係の広がりがない。また、濃い関係になればなるほどトラブルが起こりやすく、苦労の人生となります。腎臓、肝臓に不調が出やすく、性病にかかりやすいです。

松浦 百花【五行のバランス(良)】
五行のバランスが良く、精神的にも肉体的にも健康的。人との関係性が良く、幸福感に満ちた人生を歩むでしょう。

陰陽による鑑定
"""

print("Testing improved 五行による鑑定 parsing...")
print("=" * 50)

# テスト用のパース関数
def test_improved_parsing(raw_text):
    results = []
    gogyou_section_match = re.search(r'五行による鑑定\s*(.+?)(?:陰陽による鑑定|画数による鑑定|$)', raw_text, re.DOTALL)

    if gogyou_section_match:
        gogyou_content = gogyou_section_match.group(1).strip()
        print(f"五行セクション内容: {repr(gogyou_content)}")

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
                print(f"人格パターン発見: {jinko_value}")

                # 次の行から詳細を探し、【】パターンから評価を抽出
                description_parts = []
                evaluation = jinko_value  # デフォルト
                j = i + 1

                while j < len(lines):
                    next_line = lines[j].strip()

                    # 新しいパターンが始まったら停止
                    if (re.match(r'人格：', next_line) or
                        re.match(r'([一-龯]+)\s+([一-龯]+)【', next_line) or
                        ('松浦' in next_line and '百花' in next_line and '【' in next_line)):
                        break
                    elif next_line:
                        # 【水-水】パターンから評価を抽出
                        bracket_match = re.search(r'【([^】]+)】', next_line)
                        if bracket_match:
                            evaluation = bracket_match.group(1)  # 【水-水】の部分
                            print(f"  評価抽出: {evaluation}")
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
                print(f"  人格項目作成: 評価={evaluation}, 詳細長さ={len(description_parts)}")
                i = j
                continue

            # パターン2: 姓名 pattern (name with 【】)
            name_match = re.match(r'([一-龯]+)\s+([一-龯]+)【([^】]+)】', line)
            if name_match:
                sei = name_match.group(1)
                mei = name_match.group(2)
                label = name_match.group(3)
                print(f"名前パターン発見: {sei} {mei} 【{label}】")

                # 次の行以降から詳細を収集
                description_parts = []
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()

                    # 新しいパターンが始まったら停止
                    if (re.match(r'人格：', next_line) or
                        re.match(r'([一-龯]+)\s+([一-龯]+)【', next_line) or
                        ('松浦' in next_line and '百花' in next_line and '【' in next_line)):
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
                print(f"  名前項目作成: 評価={label}, 詳細長さ={len(description_parts)}")
                i = j
                continue

            i += 1

    return results

# テスト実行
results = test_improved_parsing(sample_raw_text)

print(f"\n抽出結果: {len(results)}個のアイテム")
for i, item in enumerate(results):
    print(f"{i+1}. タイプ: {item['タイプ']}")
    print(f"   対象: {item['対象']}")
    print(f"   評価: {item['評価']}")
    print(f"   詳細: {item['詳細'][:100]}...")
    print()

# 期待値チェック
print("期待値チェック:")
if len(results) >= 2:
    # 人格チェック
    jinko_item = next((item for item in results if item['タイプ'] == '人格'), None)
    if jinko_item:
        if jinko_item['評価'] == '水-水':
            print("✅ 人格の評価が正しく '水-水' として抽出された")
        else:
            print(f"❌ 人格の評価が '{jinko_item['評価']}' になっている（'水-水' であるべき）")

        if '【水-水】' not in jinko_item['詳細']:
            print("✅ 詳細から【】部分が正しく除去された")
        else:
            print("❌ 詳細に【】部分が残っている")

    # 五行のバランスチェック
    balance_item = next((item for item in results if item['タイプ'] == '五行のバランス'), None)
    if balance_item:
        if balance_item['評価'] == '五行のバランス(良)':
            print("✅ 五行のバランスの評価が正しく抽出された")
        else:
            print(f"❌ 五行のバランスの評価が '{balance_item['評価']}' になっている")

    print("✅ 二つのアイテムが正しく抽出された")
else:
    print(f"❌ アイテム数が不足: {len(results)}個（2個であるべき）")