#!/usr/bin/env python3
"""
ユーザーデータと鑑定記録の確認スクリプト
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# アプリケーションパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import User, KanteiRecord
from app.database import engine, SessionLocal

def check_user_data():
    db = SessionLocal()

    try:
        # matsuura.yuta@gmail.com のユーザー情報確認
        user = db.query(User).filter(User.email == "matsuura.yuta@gmail.com").first()

        if user:
            print(f"ユーザー情報:")
            print(f"  ID: {user.id}")
            print(f"  Email: {user.email}")
            print(f"  Business Name: {user.business_name}")
            print(f"  Created At: {user.created_at}")
            print()

            # このユーザーの鑑定記録数を確認
            count = db.query(KanteiRecord).filter(KanteiRecord.user_id == user.id).count()
            print(f"このユーザー（ID: {user.id}）の鑑定記録数: {count}件")

            # 最新5件を表示
            records = db.query(KanteiRecord).filter(
                KanteiRecord.user_id == user.id
            ).order_by(KanteiRecord.created_at.desc()).limit(5).all()

            if records:
                print(f"\n最新の鑑定記録（5件）:")
                for record in records:
                    client_name = "不明"
                    if record.client_info:
                        client_name = record.client_info.get("name", "不明")
                    print(f"  ID: {record.id}, Client: {client_name}, Created: {record.created_at}")
        else:
            print("matsuura.yuta@gmail.com というユーザーが見つかりません")

        # 全ユーザーとその鑑定記録数を確認
        print("\n全ユーザーの鑑定記録数:")
        users = db.query(User).all()
        for u in users:
            count = db.query(KanteiRecord).filter(KanteiRecord.user_id == u.id).count()
            print(f"  User ID {u.id} ({u.email}): {count}件")

    finally:
        db.close()

if __name__ == "__main__":
    check_user_data()