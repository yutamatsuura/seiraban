-- kantei-system-v2 初期データベース設定
-- PostgreSQL初期化スクリプト

-- 必要な拡張機能を有効化
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- データベースの文字セット確認
SELECT datname, datcollate, datctype FROM pg_database WHERE datname = current_database();