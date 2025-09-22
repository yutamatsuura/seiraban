#!/usr/bin/env python3
import json
import subprocess
import re
import time

# 包括的なテスト用の名前リスト（様々なパターンを含む）
test_names = [
    # 既知パターン
    ("山本", "太郎"),    # 郎【分離名】+ 人格:本太
    ("山田", "花子"),    # 花 文字の由来・意味から...
    ("織田", "信長"),    # 地行:信長
    ("龍", "馬"),       # 馬【地行が水行】

    # 問題のケース
    ("村木", "隆志"),    # 地格:隆志 (新パターン)

    # 追加テストケース
    ("田中", "一郎"),    # 郎【分離名】
    ("佐藤", "次郎"),    # 郎【分離名】
    ("鈴木", "三郎"),    # 郎【分離名】
    ("高橋", "四郎"),    # 郎【分離名】
    ("渡辺", "五郎"),    # 郎【分離名】

    ("伊藤", "花子"),    # 花 パターン
    ("加藤", "桜子"),    # 桜の可能性
    ("斎藤", "梅子"),    # 梅の可能性
    ("近藤", "菊子"),    # 菊の可能性
    ("武藤", "蘭子"),    # 蘭の可能性

    # 歴史上の人物
    ("豊臣", "秀吉"),    # 吉パターン
    ("徳川", "家康"),    # 康パターン
    ("武田", "信玄"),    # 地行:信玄
    ("上杉", "謙信"),    # 信パターン
    ("毛利", "元就"),    # 就パターン

    # 特殊漢字
    ("神", "風"),       # 風パターン
    ("鬼", "塚"),       # 塚パターン
    ("虎", "之介"),     # 之介パターン
    ("鳳", "凰"),       # 凰パターン
    ("麒", "麟"),       # 麟パターン

    # 画数の多い漢字
    ("黒田", "官兵衛"),  # 複雑な漢字
    ("細川", "忠興"),    # 興パターン
    ("小早川", "隆景"),  # 三文字姓+景パターン
    ("立花", "宗茂"),    # 茂パターン
    ("宇喜多", "秀家"),  # 三文字姓+家パターン

    # 現代的な名前
    ("田中", "美咲"),    # 美パターン
    ("佐藤", "翔太"),    # 翔パターン
    ("鈴木", "愛美"),    # 愛パターン
    ("高橋", "大輔"),    # 大パターン
    ("伊藤", "智子"),    # 智パターン

    # 一文字名前
    ("林", "蓮"),       # 蓮パターン
    ("森", "樹"),       # 樹パターン
    ("池", "泉"),       # 泉パターン
    ("石", "岩"),       # 岩パターン
    ("金", "銀"),       # 銀パターン
]

print(f"Comprehensive pattern testing - {len(test_names)} names")
print("=" * 70)

# 発見されたパターンを分類して保存
found_patterns = {
    '漢字【分類】': [],
    '人格:文字': [],
    '地行:文字': [],
    '地格:文字': [],  # 新発見
    '文字の意味': [],
    'その他': []
}

success_count = 0
total_extractions = 0

for i, (sei, mei) in enumerate(test_names, 1):
    try:
        print(f"\n{i:2d}. Testing: {sei} {mei}")

        result = subprocess.run(
            ['node', 'puppeteer_bridge_final.js', 'seimei', f'{{"name": "{sei} {mei}"}}'],
            capture_output=True, text=True, timeout=15
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            raw_text = data['result']['raw_text']
            score = data['result']['score']

            print(f"    Score: {score}")

            # 文字による鑑定セクションをチェック
            moji_section_match = re.search(r'文字による鑑定\s*(.+?)(?:陰陽による鑑定|五行による鑑定|$)', raw_text, re.DOTALL)
            if moji_section_match:
                moji_content = moji_section_match.group(1).strip()

                if moji_content and len(moji_content) > 5:
                    print(f"    ✓ Has 文字による鑑定 ({len(moji_content)} chars)")
                    print(f"    Content: {repr(moji_content[:80])}...")

                    # パターン分析
                    sentences = re.split(r'[。]', moji_content)
                    sentences = [s.strip() for s in sentences if s.strip()]

                    extractions_this_name = 0
                    for sentence in sentences:
                        # パターン1: 漢字【分類】
                        bracket_match = re.search(r'([一-龯]+)\s*【([^】]+)】', sentence)
                        if bracket_match:
                            char = bracket_match.group(1).strip()
                            category = bracket_match.group(2).strip()
                            found_patterns['漢字【分類】'].append(f"{char}【{category}】 from {sei}{mei}")
                            extractions_this_name += 1
                            continue

                        # パターン2: 人格:文字
                        jinko_match = re.search(r'人格:([^\s]+)', sentence)
                        if jinko_match:
                            char_combo = jinko_match.group(1).strip()
                            found_patterns['人格:文字'].append(f"人格:{char_combo} from {sei}{mei}")
                            extractions_this_name += 1
                            continue

                        # パターン3: 地行:文字
                        chiko_match = re.search(r'地行:([^\s]+)', sentence)
                        if chiko_match:
                            char_combo = chiko_match.group(1).strip()
                            found_patterns['地行:文字'].append(f"地行:{char_combo} from {sei}{mei}")
                            extractions_this_name += 1
                            continue

                        # パターン4: 地格:文字 (新発見)
                        chikaku_match = re.search(r'地格:([^\s]+)', sentence)
                        if chikaku_match:
                            char_combo = chikaku_match.group(1).strip()
                            found_patterns['地格:文字'].append(f"地格:{char_combo} from {sei}{mei}")
                            extractions_this_name += 1
                            print(f"      ✓ FOUND NEW PATTERN: 地格:{char_combo}")
                            continue

                        # パターン5: 文字の意味
                        char_meaning_match = re.search(r'^([一-龯]+)\s+文字の', sentence)
                        if char_meaning_match:
                            char = char_meaning_match.group(1).strip()
                            found_patterns['文字の意味'].append(f"{char} 文字の意味 from {sei}{mei}")
                            extractions_this_name += 1
                            continue

                        # パターン6: その他の単一文字パターン
                        single_char_match = re.search(r'^([一-龯]+)\s+(.+)', sentence)
                        if single_char_match:
                            char = single_char_match.group(1).strip()
                            detail = single_char_match.group(2).strip()[:30]
                            found_patterns['その他'].append(f"{char} {detail} from {sei}{mei}")
                            extractions_this_name += 1

                    if extractions_this_name > 0:
                        print(f"    ✓ Extracted {extractions_this_name} patterns")
                        success_count += 1
                        total_extractions += extractions_this_name
                    else:
                        print(f"    ✗ No patterns extracted")

                else:
                    print(f"    ✗ Empty or too short content")
            else:
                print(f"    ✗ No 文字による鑑定 section found")

        else:
            print(f"    ERROR: {result.stderr[:50]}")

        # レート制限対策
        time.sleep(0.3)

    except Exception as e:
        print(f"    EXCEPTION: {str(e)[:50]}")

print(f"\n{'='*70}")
print(f"COMPREHENSIVE PATTERN ANALYSIS")
print(f"{'='*70}")
print(f"Names with extractions: {success_count}/{len(test_names)}")
print(f"Total patterns extracted: {total_extractions}")

for pattern_type, examples in found_patterns.items():
    if examples:
        print(f"\n{pattern_type} ({len(examples)} examples):")
        for example in examples[:5]:  # 最初の5個だけ表示
            print(f"  - {example}")
        if len(examples) > 5:
            print(f"  ... and {len(examples) - 5} more")

print(f"\n{'='*70}")
print("MISSING PATTERNS ANALYSIS:")
if found_patterns['地格:文字']:
    print("❗ CRITICAL: 地格:文字 pattern found but not handled in current logic!")
else:
    print("All major patterns seem to be covered.")