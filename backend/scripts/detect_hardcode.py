#!/usr/bin/env python3
"""
ハードコード検出スクリプト

このスクリプトは以下のハードコードされた値を検出します：
- ユーザーID (user_id = 数値)
- ポート番号 (port = 数値)
- マジックナンバー
- ハードコードされたURL
- その他の設定値
"""

import re
import sys
import ast
from pathlib import Path
from typing import List, Tuple, Dict

class HardcodeDetector:
    def __init__(self):
        # 検出パターン定義
        self.patterns = {
            'user_id': [
                r'user_id\s*=\s*\d+',
                r'USER_ID\s*=\s*\d+',
            ],
            'port': [
                r'port\s*=\s*\d{4,5}',
                r'PORT\s*=\s*\d{4,5}',
            ],
            'magic_numbers': [
                r'[^a-zA-Z_]\d{2,}(?!\s*[),\]])',  # 2桁以上の数字（配列インデックスや引数以外）
            ],
            'hardcoded_urls': [
                r'["\']https?://[^"\']+["\']',
            ],
            'hardcoded_paths': [
                r'["\'][/\\][^"\']*["\']',
            ]
        }

        # 除外パターン（正当な使用）
        self.exclude_patterns = [
            r'#.*',  # コメント行
            r'""".*?"""',  # ドキュメント文字列
            r"'''.*?'''",  # ドキュメント文字列
            r'test_.*\.py',  # テストファイル（ファイル名）
            r'migrations?/',  # マイグレーションファイル
            r'__version__\s*=',  # バージョン定義
            r'HTTP_\d+',  # HTTPステータスコード
            r'status\.HTTP_\d+',  # HTTPステータスコード
            r'@router\.',  # FastAPIルーターのデコレータ
            r'@app\.',  # FastAPIアプリのデコレータ
            r'"[/{}a-zA-Z_-]*"',  # APIパス（スラッシュで始まるパス）
            r"'[/{}a-zA-Z_-]*'",  # APIパス（シングルクォート）
            r'f"[^"]*{[^}]*}[^"]*"',  # f-string
            r"f'[^']*{[^}]*}[^']*'",  # f-string（シングルクォート）
        ]

    def is_excluded(self, line: str, file_path: str) -> bool:
        """除外パターンに該当するかチェック"""
        # ファイルパスの除外チェック
        for pattern in self.exclude_patterns:
            if re.search(pattern, file_path):
                return True

        # 行内容の除外チェック
        for pattern in self.exclude_patterns:
            if re.search(pattern, line):
                return True

        return False

    def detect_in_file(self, file_path: str) -> List[Tuple[int, str, str]]:
        """ファイル内のハードコードを検出"""
        violations = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # 除外パターンチェック
                if self.is_excluded(line.strip(), file_path):
                    continue

                # 各パターンでチェック
                for category, patterns in self.patterns.items():
                    for pattern in patterns:
                        matches = re.finditer(pattern, line)
                        for match in matches:
                            violations.append((
                                line_num,
                                category,
                                line.strip(),
                                match.group()
                            ))

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

        return violations

    def check_files(self, file_paths: List[str]) -> Dict[str, List]:
        """複数ファイルをチェック"""
        all_violations = {}

        for file_path in file_paths:
            if Path(file_path).suffix == '.py':
                violations = self.detect_in_file(file_path)
                if violations:
                    all_violations[file_path] = violations

        return all_violations

def main():
    if len(sys.argv) < 2:
        print("Usage: python detect_hardcode.py <file1> [file2] ...")
        sys.exit(1)

    detector = HardcodeDetector()
    file_paths = sys.argv[1:]

    violations = detector.check_files(file_paths)

    if violations:
        print("🚫 ハードコードが検出されました！")
        print("=" * 60)

        for file_path, file_violations in violations.items():
            print(f"\n📁 {file_path}")
            print("-" * 40)

            for line_num, category, line, match in file_violations:
                print(f"  Line {line_num}: [{category.upper()}] {match}")
                print(f"    {line}")

        print("\n" + "=" * 60)
        print("❌ コミットを拒否します。")
        print("💡 対処方法:")
        print("   • 環境変数を使用: os.getenv('VARIABLE_NAME')")
        print("   • 設定ファイルを使用: config.py または .env")
        print("   • 定数を定義: constants.py")
        print("   • 依存注入を使用: Depends(get_current_user)")

        sys.exit(1)
    else:
        print("✅ ハードコード検出: OK")
        sys.exit(0)

if __name__ == "__main__":
    main()