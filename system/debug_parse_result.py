#!/usr/bin/env python3
import json
import sys

# 上記のAPIレスポンスから生データをパースする
if __name__ == "__main__":
    # まず生データを確認
    with open('gojo_response.json', 'r', encoding='utf-8') as f:
        response_data = json.load(f)

    raw_text = response_data['data']['raw_text']
    print("=== 生データ ===")
    print(raw_text)
    print("\n" + "="*70)

    # ここでバックエンドが実際にどのようにパースしているかを確認
    # run_puppeteer_bridge関数の内部でパース処理が実行されていることが分かった