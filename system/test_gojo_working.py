#!/usr/bin/env python3
import re

# テストケース：五条 めざるの五行解析（動作確認版）
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

def parse_gogyou_kantei_working(raw_text):
    """五行による鑑定の動作確認版解析"""
    results = []

    # 五行セクションを抽出
    gogyou_section_match = re.search(r'五行による鑑定\s*(.+?)(?:\s*陰陽による鑑定|\s*画数による鑑定|$)', raw_text, re.DOTALL)
    if not gogyou_section_match:
        return results

    gogyou_content = gogyou_section_match.group(1).strip()

    if not gogyou_content or len(gogyou_content) <= 10:
        return results

    print(f"原文:\n{gogyou_content}\n")

    # 各パターンの詳細チェック
    print("=== パターン検索デバッグ ===")

    # パターン1: 人格
    jinko_pattern = r'人格:([^\s\n]+)\s*\n?\s*【([^】]+)】'
    jinko_matches = re.findall(jinko_pattern, gogyou_content)
    print(f"人格パターンマッチ数: {len(jinko_matches)}")
    for i, match in enumerate(jinko_matches):
        print(f"  人格{i+1}: '{match[0]}' - '{match[1]}'")

    # パターン2: 名前パターン
    name_pattern = r'([一-龯あ-ゖア-ヶ]+)\s+([一-龯あ-ゖア-ヶ]+)\s*\n?\s*【([^】]+)】'
    name_matches = re.findall(name_pattern, gogyou_content)
    print(f"名前パターンマッチ数: {len(name_matches)}")
    for i, match in enumerate(name_matches):
        print(f"  名前{i+1}: '{match[0]}' '{match[1]}' - '{match[2]}'")

    print("=== 実際の解析開始 ===")

    # 人格の処理
    jinko_pattern_full = r'人格:([^\s\n]+)\s*\n?\s*【([^】]+)】\s*(.*?)(?=(?:[一-龯あ-ゖア-ヶ]+\s+[一-龯あ-ゖア-ヶ]+\s*\n?\s*【)|$)'
    jinko_match = re.search(jinko_pattern_full, gogyou_content, re.DOTALL)
    if jinko_match:
        jinko_value = jinko_match.group(1)
        evaluation = jinko_match.group(2)
        content = jinko_match.group(3).strip()

        # 混入した名前情報を除去
        content_lines = content.split('\n')
        clean_lines = []
        for line in content_lines:
            line = line.strip()
            # 名前パターンが含まれていたら停止
            if re.search(r'[一-龯あ-ゖア-ヶ]+\s+[一-龯あ-ゖア-ヶ]+\s*【', line):
                break
            if line:
                clean_lines.append(line)

        clean_content = ' '.join(clean_lines).strip()

        print(f"人格詳細（動作確認版）: '{clean_content}'")

        results.append({
            "タイプ": "人格",
            "対象": f"人格:{jinko_value}",
            "評価": evaluation,
            "詳細": clean_content
        })

    # 五行のバランスの処理（最初に現れる名前）
    name_pattern_full = r'([一-龯あ-ゖア-ヶ]+)\s+([一-龯あ-ゖア-ヶ]+)\s*\n?\s*【([^】]+)】\s*(.*?)(?=\n[一-龯あ-ゖア-ヶ]+\s+[一-龯あ-ゖア-ヶ]+\s*\n?\s*【|$)'
    name_match = re.search(name_pattern_full, gogyou_content, re.DOTALL)
    if name_match:
        sei = name_match.group(1)
        mei = name_match.group(2)
        name_evaluation = name_match.group(3)
        content = name_match.group(4).strip()

        print(f"五行のバランス詳細（RAW）: '{content}'")

        # 改行で分割して最初の文章まで取得
        lines = content.split('\n')
        clean_lines = []
        for line in lines:
            line = line.strip()
            if line and not re.search(r'[一-龯あ-ゖア-ヶ]+\s+[一-龯あ-ゖア-ヶ]+\s*【', line):
                clean_lines.append(line)
            elif re.search(r'[一-龯あ-ゖア-ヶ]+\s+[一-龯あ-ゖア-ヶ]+\s*【', line):
                break

        clean_content = ' '.join(clean_lines).strip()

        print(f"五行のバランス詳細（動作確認版）: '{clean_content}'")

        results.append({
            "タイプ": "五行のバランス",
            "対象": f"{sei} {mei}",
            "評価": name_evaluation,
            "詳細": clean_content
        })

    return results

print("五条 めざるの五行による鑑定の分離テスト（動作確認版）")
print("=" * 70)

results = parse_gogyou_kantei_working(test_text)

print(f"\n抽出されたアイテム数: {len(results)}")

for j, item in enumerate(results):
    print(f"  {j+1}. {item['タイプ']} - {item['対象']} - {item['評価']}")
    print(f"     詳細: {item['詳細']}")

print(f"\n{'='*70}")
expected_jinko = "中年期（28歳～50歳）までの運勢は大凶。上司や親、従業員と折り合い悪くなりやすいです。熱しやすく、冷めやすい。人生の変化が激しく、物事が壊れやすい。（自分自身で物事を壊しやすい）苦労の人生となります。腎臓 心臓、精神に不調が出やすいです。冷え性になりやすい。"
expected_gogyou = "バランス感覚が良く、判断力に優れています。縁のつかみ方、人間関係作りが上手です。周りの違う考えを受け入れることができます。"

success = len(results) == 2
if len(results) >= 1:
    success = success and results[0]['タイプ'] == '人格' and results[0]['詳細'] == expected_jinko
if len(results) >= 2:
    success = success and results[1]['タイプ'] == '五行のバランス' and results[1]['詳細'] == expected_gogyou

print(f"🎯 テスト結果: {'✅ 成功' if success else '❌ 失敗'}")
print(f"{'='*70}")