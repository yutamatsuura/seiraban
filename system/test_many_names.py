#!/usr/bin/env python3
import json
import subprocess
import re
import time

# 100パターンの名前リスト（漢字、ひらがな、カタカナ、様々な画数の組み合わせ）
test_names = [
    # 一般的な名前
    ("田中", "太郎"), ("佐藤", "花子"), ("鈴木", "一郎"), ("高橋", "美咲"), ("伊藤", "翔太"),
    ("渡辺", "真美"), ("山本", "太郎"), ("中村", "恵子"), ("小林", "健太"), ("加藤", "愛"),
    ("吉田", "大輔"), ("山田", "花子"), ("佐々木", "慎一"), ("山口", "由美"), ("松本", "拓也"),
    ("井上", "香織"), ("木村", "雅人"), ("林", "美穂"), ("清水", "康介"), ("山崎", "麻衣"),
    ("森", "直樹"), ("池田", "さくら"), ("橋本", "隼人"), ("石川", "理恵"), ("斉藤", "洋平"),

    # 特殊な漢字、画数が多い名前
    ("織田", "信長"), ("豊臣", "秀吉"), ("徳川", "家康"), ("武田", "信玄"), ("上杉", "謙信"),
    ("毛利", "元就"), ("島津", "義久"), ("伊達", "政宗"), ("真田", "幸村"), ("前田", "利家"),
    ("黒田", "官兵衛"), ("細川", "忠興"), ("小早川", "隆景"), ("立花", "宗茂"), ("加藤", "清正"),
    ("福島", "正則"), ("石田", "三成"), ("大谷", "吉継"), ("宇喜多", "秀家"), ("小西", "行長"),

    # 読み方が特殊な名前
    ("神", "風"), ("鬼", "塚"), ("龍", "馬"), ("虎", "之介"), ("鳳", "凰"),
    ("麒", "麟"), ("鶴", "岡"), ("亀", "田"), ("狼", "煙"), ("鷹", "山"),

    # ひらがな・カタカナ含む
    ("田中", "あい"), ("佐藤", "ゆい"), ("鈴木", "えみ"), ("高橋", "かな"), ("伊藤", "みお"),
    ("山田", "ソラ"), ("中村", "レナ"), ("小林", "ハル"), ("加藤", "ユウ"), ("吉田", "リン"),

    # 一文字名前
    ("木", "蓮"), ("金", "剛"), ("水", "晶"), ("火", "龍"), ("土", "方"),
    ("石", "橋"), ("山", "本"), ("川", "上"), ("海", "老"), ("森", "田"),

    # 三文字姓・名
    ("佐々木", "太郎"), ("長谷川", "花子"), ("小野寺", "一郎"), ("菊地原", "美咲"), ("宇都宮", "翔太"),

    # 珍しい漢字
    ("藤原", "龍之介"), ("源", "義経"), ("平", "清盛"), ("足利", "尊氏"), ("北条", "時宗"),
    ("新田", "義貞"), ("楠木", "正成"), ("名和", "長年"), ("赤松", "則村"), ("山名", "時氏"),

    # 現代的な名前
    ("田中", "ユウト"), ("佐藤", "ハルカ"), ("鈴木", "ソウタ"), ("高橋", "アオイ"), ("伊藤", "ヒナタ"),
    ("山田", "リク"), ("中村", "ミオ"), ("小林", "ハナ"), ("加藤", "タクミ"), ("吉田", "サクラ"),

    # 特定の画数パターン
    ("一", "一"), ("二", "二"), ("三", "三"), ("四", "四"), ("五", "五"),
    ("六", "六"), ("七", "七"), ("八", "八"), ("九", "九"), ("十", "十"),
]

print(f"Testing {len(test_names)} name patterns...")

results_with_moji = []
results_without_moji = []
error_count = 0

for i, (sei, mei) in enumerate(test_names, 1):
    try:
        print(f"\n{i:3d}. Testing: {sei} {mei}")

        # Puppeteerでテスト実行
        result = subprocess.run(
            ['node', 'puppeteer_bridge_final.js', 'seimei', f'{{"name": "{sei} {mei}"}}'],
            capture_output=True, text=True, timeout=30
        )

        if result.returncode == 0:
            data = json.loads(result.stdout)
            raw_text = data['result']['raw_text']
            score = data['result']['score']

            # 文字による鑑定の有無をチェック
            if '文字による鑑定' in raw_text:
                moji_section_match = re.search(r'文字による鑑定\s*(.+?)(?:陰陽による鑑定|五行による鑑定|$)', raw_text, re.DOTALL)
                if moji_section_match:
                    moji_content = moji_section_match.group(1).strip()
                    if moji_content and len(moji_content) > 10:  # 実質的な内容があるかチェック
                        results_with_moji.append({
                            'name': f"{sei} {mei}",
                            'score': score,
                            'moji_content': moji_content[:200] + '...' if len(moji_content) > 200 else moji_content
                        })
                        print(f"    ✓ Has 文字による鑑定 (score: {score})")
                        print(f"    Content: {moji_content[:100]}...")
                    else:
                        results_without_moji.append({
                            'name': f"{sei} {mei}",
                            'score': score,
                            'reason': 'Empty moji content'
                        })
                        print(f"    ✗ Empty 文字による鑑定 (score: {score})")
                else:
                    results_without_moji.append({
                        'name': f"{sei} {mei}",
                        'score': score,
                        'reason': 'No moji section match'
                    })
                    print(f"    ✗ No 文字による鑑定 section (score: {score})")
            else:
                results_without_moji.append({
                    'name': f"{sei} {mei}",
                    'score': score,
                    'reason': 'No moji keyword'
                })
                print(f"    ✗ No 文字による鑑定 keyword (score: {score})")
        else:
            error_count += 1
            print(f"    ERROR: {result.stderr[:100]}")

        # APIレート制限回避のため少し待機
        time.sleep(0.5)

    except Exception as e:
        error_count += 1
        print(f"    EXCEPTION: {str(e)[:100]}")
        time.sleep(1)

print(f"\n{'='*60}")
print(f"SUMMARY")
print(f"{'='*60}")
print(f"Total tested: {len(test_names)}")
print(f"With 文字による鑑定: {len(results_with_moji)}")
print(f"Without 文字による鑑定: {len(results_without_moji)}")
print(f"Errors: {error_count}")

# 文字による鑑定があった名前の詳細を出力
if results_with_moji:
    print(f"\n{'='*60}")
    print(f"NAMES WITH 文字による鑑定 ({len(results_with_moji)} names)")
    print(f"{'='*60}")
    for result in results_with_moji:
        print(f"Name: {result['name']} (Score: {result['score']})")
        print(f"Content: {result['moji_content']}")
        print("-" * 40)

# 文字による鑑定がなかった名前の理由を出力
if results_without_moji:
    print(f"\n{'='*60}")
    print(f"NAMES WITHOUT 文字による鑑定 ({len(results_without_moji)} names)")
    print(f"{'='*60}")
    reason_counts = {}
    for result in results_without_moji:
        reason = result.get('reason', 'Unknown')
        reason_counts[reason] = reason_counts.get(reason, 0) + 1
        print(f"{result['name']} (Score: {result['score']}) - {reason}")

    print(f"\nReason breakdown:")
    for reason, count in reason_counts.items():
        print(f"  {reason}: {count} names")

# 結果をJSONファイルに保存
output_data = {
    'summary': {
        'total_tested': len(test_names),
        'with_moji': len(results_with_moji),
        'without_moji': len(results_without_moji),
        'errors': error_count
    },
    'results_with_moji': results_with_moji,
    'results_without_moji': results_without_moji
}

with open('moji_test_results.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"\nResults saved to moji_test_results.json")