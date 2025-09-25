#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from bs4 import BeautifulSoup
import re

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_html_file('existing-system-proxy.html')
        elif self.path.startswith('/api/existing-system'):
            self.handle_existing_system_request()
        else:
            self.send_404()

    def do_POST(self):
        if self.path == '/api/proxy-existing-system':
            self.handle_proxy_request()
        else:
            self.send_404()

    def handle_existing_system_request(self):
        """既存システムのデータを取得"""
        try:
            # パラメータを解析
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)

            year = params.get('year', ['1982'])[0]
            month = params.get('month', ['10'])[0]
            day = params.get('day', ['12'])[0]
            gender = params.get('gender', ['male'])[0]

            # 既存システムにリクエスト
            existing_url = f"https://kigaku-navi.com/qsei/ban_kipou.php"
            data = {
                'year': year,
                'month': month,
                'day': day,
                'gender': gender
            }

            response = requests.post(existing_url, data=data, timeout=10)

            if response.status_code == 200:
                # HTMLを解析して方位盤データを抽出
                soup = BeautifulSoup(response.text, 'html.parser')

                # 方位盤情報を抽出
                hoiban_data = self.extract_hoiban_data(soup)

                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                self.wfile.write(json.dumps(hoiban_data, ensure_ascii=False).encode('utf-8'))
            else:
                self.send_error_response("既存システムからの応答エラー")

        except Exception as e:
            print(f"Error: {e}")
            self.send_error_response(str(e))

    def handle_proxy_request(self):
        """POSTリクエストを処理"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            # 既存システムに転送
            existing_url = "https://kigaku-navi.com/qsei/ban_kipou.php"

            response = requests.post(existing_url, data=data, timeout=10)

            if response.status_code == 200:
                # レスポンスのHTMLを整形
                cleaned_html = self.clean_html_response(response.text)

                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()

                self.wfile.write(cleaned_html.encode('utf-8'))
            else:
                self.send_error_response("既存システムエラー")

        except Exception as e:
            print(f"Proxy Error: {e}")
            self.send_error_response(str(e))

    def extract_hoiban_data(self, soup):
        """HTMLから方位盤データを抽出"""
        data = {
            "birth_info": {},
            "year_ban": {},
            "month_ban": {},
            "day_ban": {},
            "kipou_info": []
        }

        try:
            # 生年月日情報を抽出
            birth_elements = soup.find_all(text=re.compile(r'\d{4}年\d{1,2}月\d{1,2}日'))
            if birth_elements:
                data["birth_info"]["date"] = birth_elements[0].strip()

            # 本命星・月命星を抽出
            qsei_elements = soup.find_all(text=re.compile(r'[一二三四五六七八九][白黒碧緑黄紫赤][水土木金火]星'))
            if len(qsei_elements) >= 2:
                data["birth_info"]["year_qsei"] = qsei_elements[0].strip()
                data["birth_info"]["month_qsei"] = qsei_elements[1].strip()

            # 方位盤の九星配置を抽出
            numbers = soup.find_all(text=re.compile(r'^[1-9]$'))
            if len(numbers) >= 24:  # 年盤8 + 月盤8 + 日盤8
                data["year_ban"]["kiban"] = [int(n.strip()) for n in numbers[0:8]]
                data["month_ban"]["kiban"] = [int(n.strip()) for n in numbers[8:16]]
                data["day_ban"]["kiban"] = [int(n.strip()) for n in numbers[16:24]]

            # 吉凶情報を抽出
            kipou_keywords = ['最大吉方', '吉方', '凶方', '五黄殺', '暗剣殺', '本命殺', '月命殺']
            for keyword in kipou_keywords:
                elements = soup.find_all(text=re.compile(keyword))
                for elem in elements:
                    data["kipou_info"].append({
                        "type": keyword,
                        "text": elem.strip()
                    })

        except Exception as e:
            print(f"Data extraction error: {e}")

        return data

    def clean_html_response(self, html):
        """HTMLレスポンスを整形"""
        soup = BeautifulSoup(html, 'html.parser')

        # 不要な要素を削除
        for element in soup(['script', 'style', 'nav', 'header', 'footer']):
            element.decompose()

        # 方位盤関連の要素のみを抽出
        hoiban_content = soup.find('body')
        if hoiban_content:
            return str(hoiban_content)
        else:
            return html

    def send_html_file(self, filename):
        """HTMLファイルを送信"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(content.encode('utf-8'))
        except FileNotFoundError:
            self.send_404()

    def send_error_response(self, message):
        """エラーレスポンスを送信"""
        self.send_response(500)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        error_data = {"error": message}
        self.wfile.write(json.dumps(error_data, ensure_ascii=False).encode('utf-8'))

    def send_404(self):
        """404エラーを送信"""
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"404 Not Found")

def run_server(port=8081):
    """プロキシサーバーを起動"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProxyHandler)
    print(f"プロキシサーバーが起動しました: http://localhost:{port}")
    print("既存システムのデータを取得できます")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()