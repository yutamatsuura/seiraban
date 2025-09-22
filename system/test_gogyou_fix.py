#!/usr/bin/env python3
import requests
import json
import time

print("Testing 五行による鑑定 parsing fix...")
print("=" * 50)

try:
    # Give server time to start up
    time.sleep(2)

    # Test the backend parsing with sample data using a mock request
    # Since Puppeteer is timing out, let's test our parsing logic directly
    print("Testing backend parsing logic directly...")

    # Make the actual API call to check if Puppeteer is working
    print("Attempting API call to backend...")
    response = requests.post('http://localhost:8502/api/seimei',
                           json={'name': '松浦百花'},
                           timeout=30)

    if response.status_code == 200:
        data = response.json()
        print("✅ Backend response received successfully!")
        print(f"Score: {data['score']}")

        # Check 五行による鑑定 data
        if '五行による鑑定' in data:
            gogyou_items = data['五行による鑑定']
            print(f"\n五行による鑑定 items found: {len(gogyou_items)}")

            for i, item in enumerate(gogyou_items):
                print(f"\n{i+1}. タイプ: {item.get('タイプ', 'N/A')}")
                print(f"   対象: {item.get('対象', 'N/A')}")
                print(f"   評価: {item.get('評価', 'N/A')}")
                print(f"   詳細: {item.get('詳細', 'N/A')[:100]}...")

                # Check for truncation issues
                detail = item.get('詳細', '')
                if "松浦。" in detail and not "松浦 百花" in detail:
                    print("   ❌ ISSUE: Content still truncated at '松浦。'")
                elif len(detail) > 50:
                    print("   ✅ Content looks complete")
                else:
                    print("   ❓ Content might be too short")

            # Check for expected patterns
            jinko_items = [item for item in gogyou_items if item.get('タイプ') == '人格']
            balance_items = [item for item in gogyou_items if item.get('タイプ') == '五行バランス']

            print(f"\n人格 items: {len(jinko_items)}")
            print(f"五行バランス items: {len(balance_items)}")

            if len(jinko_items) >= 1 and len(balance_items) >= 1:
                print("✅ SUCCESS: Found both 人格 and 五行バランス items!")
            else:
                print("❌ Missing expected item types")

        else:
            print("❌ No 五行による鑑定 data found")

        # Check raw structure for debugging
        print(f"\nResponse keys: {list(data.keys())}")

    else:
        print(f"❌ Backend request failed: {response.status_code}")
        print(f"Response: {response.text}")

except requests.Timeout:
    print("❌ Request timed out - Puppeteer bridge might still be having issues")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nTest completed!")