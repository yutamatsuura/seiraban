#!/usr/bin/env python3
import requests
import json

print("Testing backend fix for 松浦百花...")

try:
    response = requests.post('http://localhost:8502/api/seimei', json={'name': '松浦百花'})

    if response.status_code == 200:
        data = response.json()
        print("✅ Backend response received successfully!")
        print(f"Score: {data['score']}")

        if '文字による鑑定' in data:
            moji_items = data['文字による鑑定']
            print(f"\n文字による鑑定 items: {len(moji_items)}")

            for i, item in enumerate(moji_items):
                print(f"{i+1}. 文字: {item['文字']}")
                print(f"   分類: {item['分類']}")
                print(f"   詳細: {item['詳細'][:100]}...")
                print()

            # Check specifically for 花 character evaluations
            hana_items = [item for item in moji_items if '花' in item['文字']]
            print(f"花 character evaluations found: {len(hana_items)}")

            if len(hana_items) >= 2:
                print("✅ SUCCESS: Multiple 花 evaluations found!")
                for i, item in enumerate(hana_items):
                    print(f"  花 evaluation {i+1}: {item['詳細'][:80]}...")
            elif len(hana_items) == 1:
                print("❌ ISSUE: Still only one 花 evaluation found")
                print(f"  Combined content: {hana_items[0]['詳細']}")

                # Check if it contains both evaluations merged
                if "文字の由来・意味から" in hana_items[0]['詳細'] and "名前には使用できない文字です" in hana_items[0]['詳細']:
                    print("  ⚠️  Both evaluations are merged into one item!")
            else:
                print("❌ No 花 evaluations found at all")
        else:
            print("❌ No 文字による鑑定 section found")
    else:
        print(f"❌ Backend request failed: {response.status_code}")
        print(response.text)

except Exception as e:
    print(f"❌ Error: {e}")