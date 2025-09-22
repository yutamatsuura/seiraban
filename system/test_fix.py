#!/usr/bin/env python3
import json
import subprocess

# Test the specific case that was reported
print("Testing fix for 松浦百花...")

result = subprocess.run(
    ['node', 'puppeteer_bridge_final.js', 'seimei', '{"name": "松浦百花"}'],
    capture_output=True, text=True, timeout=15
)

if result.returncode == 0:
    data = json.loads(result.stdout)
    raw_text = data['result']['raw_text']

    # Make a request to the backend to test the parsing
    import requests

    response = requests.post('http://localhost:8502/api/seimei', json={'name': '松浦百花'})
    if response.status_code == 200:
        backend_data = response.json()

        print("Backend response received successfully!")
        print(f"Score: {backend_data['score']}")

        if '文字による鑑定' in backend_data:
            moji_items = backend_data['文字による鑑定']
            print(f"\n文字による鑑定 items: {len(moji_items)}")

            for i, item in enumerate(moji_items):
                print(f"{i+1}. 文字: {item['文字']}")
                print(f"   分類: {item['分類']}")
                print(f"   詳細: {item['詳細'][:80]}...")
                print()

            # Check specifically for 花 character evaluations
            hana_items = [item for item in moji_items if '花' in item['文字']]
            print(f"花 character evaluations found: {len(hana_items)}")

            if len(hana_items) >= 2:
                print("✅ SUCCESS: Multiple 花 evaluations found!")
                for i, item in enumerate(hana_items):
                    print(f"  花 evaluation {i+1}: {item['詳細'][:60]}...")
            else:
                print("❌ ISSUE: Still only one 花 evaluation found")
                if hana_items:
                    print(f"  Combined content: {hana_items[0]['詳細']}")
        else:
            print("No 文字による鑑定 section found")
    else:
        print(f"Backend request failed: {response.status_code}")
        print(response.text)
else:
    print(f"Puppeteer failed: {result.stderr}")