#!/usr/bin/env python3
import re

# 上原はまの実際のデータをテスト
uehara_hama_raw_text = """
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

print("Testing 上原はま pattern analysis...")
print("=" * 50)

# 五行セクションを抽出
gogyou_section_match = re.search(r'五行による鑑定\s*(.+?)(?:\s*陰陽による鑑定|\s*画数による鑑定|$)', uehara_hama_raw_text, re.DOTALL)
if gogyou_section_match:
    gogyou_content = gogyou_section_match.group(1).strip()
    print(f"五行セクション内容:\n{repr(gogyou_content)}")
    print("\n" + "-" * 50)

    # 現在の問題のあるパターン（松浦ハードコード）
    print("❌ 現在の問題のあるパターン:")
    jinko_pattern_bad = r'人格：([^\s]+)\s*\n?\s*【([^】]+)】\s*([^松]*?)(?=松浦|$)'
    jinko_match_bad = re.search(jinko_pattern_bad, gogyou_content, re.DOTALL)
    print(f"  パターン: {jinko_pattern_bad}")
    print(f"  マッチ結果: {jinko_match_bad}")

    print("\n✅ 新しい汎用的なパターン:")
    # 改良案1: 名前パターンを先に見つけて、それをルックアヘッドに使用
    # まず名前パターンを検索
    name_pattern = r'([一-龯あ-ゖ]+)\s+([一-龯あ-ゖ]+)\s*\n?\s*【([^】]+)】'
    name_match = re.search(name_pattern, gogyou_content)
    if name_match:
        sei = name_match.group(1)
        print(f"  検出された姓: {sei}")

        # 姓を使って人格パターンを動的に構築
        jinko_pattern_good = rf'人格：([^\s]+)\s*\n?\s*【([^】]+)】\s*(.*?)(?={re.escape(sei)})'
        jinko_match_good = re.search(jinko_pattern_good, gogyou_content, re.DOTALL)
        print(f"  パターン: {jinko_pattern_good}")
        print(f"  マッチ結果: {jinko_match_good.groups() if jinko_match_good else None}")

        if jinko_match_good:
            jinko_value = jinko_match_good.group(1)
            evaluation = jinko_match_good.group(2)
            content = jinko_match_good.group(3).strip()

            print(f"  人格値: {jinko_value}")
            print(f"  評価: {evaluation}")
            print(f"  詳細: {content[:100]}...")

    print("\n✅ 名前パターンの解析:")
    if name_match:
        sei = name_match.group(1)
        mei = name_match.group(2)
        label = name_match.group(3)
        print(f"  姓: {sei}")
        print(f"  名: {mei}")
        print(f"  評価: {label}")

        # 名前の詳細を取得（陰陽による鑑定まで）
        name_detail_pattern = rf'{re.escape(sei)}\s+{re.escape(mei)}\s*\n?\s*【[^】]+】\s*(.*?)(?=陰陽による鑑定|$)'
        name_detail_match = re.search(name_detail_pattern, gogyou_content, re.DOTALL)
        if name_detail_match:
            detail = name_detail_match.group(1).strip()
            print(f"  詳細: {detail}")

print("\n" + "=" * 50)
print("結論: 松浦ハードコードを除去し、動的に姓を検出して使用する必要がある")