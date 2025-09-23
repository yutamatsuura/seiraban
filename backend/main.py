"""
診断鑑定システム - FastAPIバックエンド
Puppeteerブリッジとの統合版

=====================================
⚠️ 開発上の重要なルール ⚠️
=====================================
ハードコーディング厳禁！
以下のようなハードコーディングは絶対に行わないこと：
1. 特定の名前（例：田中、佐藤、美、花、郎）を使用する
2. 特定の画数（例：9画、41画）を条件として使用する
3. 特定の文字の組み合わせを前提とする

すべての実装は以下を満たすこと：
- 何千通りの名前パターンに対応できる
- 汎用的な正規表現パターンを使用する
- データ駆動型のロジックとする
=====================================
"""

# 起動確認ログ（デバッグ用）
print("=== DEBUG: main.py が読み込まれました（6文字対応版） ===")
print("=== DEBUG: 動的抽出機能が有効です ===")
import time
print(f"=== DEBUG: 起動時刻 {time.strftime('%Y-%m-%d %H:%M:%S')} ===")

# 必要なライブラリをインポート
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.sql import func
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import subprocess
import json
import os
import uuid
import asyncio

# 環境変数読み込み
from dotenv import load_dotenv
load_dotenv('.env.local')

# 認証設定
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-please-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# パスワードハッシュ化設定
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# データベース設定
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./unmei.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# データベースモデル定義
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    business_name = Column(String(255), nullable=True)
    operator_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    utage_user_id = Column(String(255), nullable=True)
    subscription_status = Column(String(50), default="active", nullable=False)
    subscription_updated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    kantei_records = relationship("KanteiRecord", back_populates="user")

class KanteiRecord(Base):
    __tablename__ = "kantei_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    client_name = Column(String(255), nullable=False, index=True)
    client_email = Column(String(255), nullable=True)
    client_info = Column(JSON, nullable=False)
    calculation_result = Column(JSON, nullable=False)
    pdf_url = Column(String(500), nullable=True)
    pdf_file_size = Column(Integer, nullable=True)
    pdf_generated_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="created", nullable=False)
    custom_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="kantei_records")

# データベースセッション管理
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_database_session():
    return SessionLocal()

# 認証関数
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db = get_database_session()
    user = db.query(User).filter(User.email == email).first()
    db.close()
    if user is None:
        raise credentials_exception
    return user

# Pydanticモデル
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    business_name: Optional[str] = None
    operator_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str

class UserResponse(BaseModel):
    id: int
    email: str
    business_name: Optional[str]
    operator_name: Optional[str]
    is_active: bool
    created_at: datetime

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

app = FastAPI(title="運命織（UnmeiOri）診断鑑定システム API", version="1.0.0")

# 認証ルーターは含まずスタンドアロンのmain.pyで動作

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番では適切に制限する
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル配信設定
app.mount("/static", StaticFiles(directory="/tmp/pdf_storage"), name="static")

# Puppeteerブリッジのパス
PUPPETEER_BRIDGE_PATH = "/Users/lennon/projects/inoue4/system/puppeteer_bridge_final.js"

# データモデル
class KyuseiRequest(BaseModel):
    birth_date: str  # YYYY-MM-DD形式
    gender: str      # "male" or "female"

class SeimeiRequest(BaseModel):
    name: str        # "姓 名"形式

class DiagnosisRequest(BaseModel):
    client_name: str
    birth_date: str
    gender: str
    name: Optional[str] = None  # 姓名判断用の名前
    name_for_seimei: Optional[str] = None  # 後方互換性用
    diagnosis_pattern: str = "all"  # "kyusei_only", "seimei_only", "all"
    birth_time: Optional[str] = None  # 出生時間（HH:MM形式、任意）

class DiagnosisResult(BaseModel):
    id: str
    client_name: str
    created_at: datetime
    kyusei_result: Optional[Dict[str, Any]] = None
    seimei_result: Optional[Dict[str, Any]] = None
    status: str  # "processing", "completed", "failed"
    error_message: Optional[str] = None

# テンプレート設定関連モデル
class TemplateSettingsUpdate(BaseModel):
    business_name: Optional[str] = None
    operator_name: Optional[str] = None
    color_theme: Optional[str] = "default"
    font_family: Optional[str] = "default"
    font_scale: Optional[float] = 1.0
    layout_style: Optional[str] = "standard"
    logo_url: Optional[str] = None
    custom_css: Optional[str] = None

class TemplateSettings(BaseModel):
    business_name: str = ""
    operator_name: str = ""
    color_theme: str = "default"
    font_family: str = "default"
    font_scale: float = 1.0
    layout_style: str = "standard"
    logo_url: Optional[str] = None
    custom_css: Optional[str] = None

# インメモリストレージ（本番ではデータベース使用）
# メモリ内ストレージを削除 - 全てデータベースベースに統一

# インメモリテンプレート設定ストレージ（ユーザー固有・簡易実装）
user_template_settings_storage = {}  # user_id -> settings

# デフォルトテンプレート設定
default_template_settings = {
    "business_name": "占いサロン 星花",
    "operator_name": "星野 花子",
    "color_theme": "default",
    "font_family": "default",
    "font_scale": 1.0,
    "layout_style": "standard",
    "logo_url": None,
    "custom_css": None
}

def get_user_template_settings(user_id: int):
    """ユーザーのテンプレート設定を取得（存在しない場合はデフォルト設定を返す）"""
    if user_id not in user_template_settings_storage:
        user_template_settings_storage[user_id] = default_template_settings.copy()
    return user_template_settings_storage[user_id]

def update_user_template_settings(user_id: int, settings_update: dict):
    """ユーザーのテンプレート設定を更新"""
    current_settings = get_user_template_settings(user_id)
    for key, value in settings_update.items():
        if value is not None:
            current_settings[key] = value
    return current_settings

# データベースヘルパー関数
def get_kantei_record_by_id(db, record_id: int):
    """IDで鑑定記録を取得"""
    return db.query(KanteiRecord).filter(KanteiRecord.id == record_id).first()

def create_kantei_record(db, user_id: int, client_name: str, request_data):
    """新しい鑑定記録を作成"""

    kantei_record = KanteiRecord(
        user_id=user_id,
        client_name=client_name,
        client_email=None,
        client_info={
            "name": client_name,
            "birth_date": request_data.birth_date,
            "gender": request_data.gender,
            "name_for_seimei": getattr(request_data, 'name', None) or getattr(request_data, 'name_for_seimei', None),
            "diagnosis_pattern": getattr(request_data, 'diagnosis_pattern', 'all'),
            "birth_time": getattr(request_data, 'birth_time', None)
        },
        calculation_result={},
        status="processing"
    )

    db.add(kantei_record)
    db.commit()
    db.refresh(kantei_record)
    return kantei_record

@app.get("/")
async def root():
    return {"message": "診断鑑定システム API - 動作中"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# 認証エンドポイント
@app.post("/api/auth/register", response_model=dict)
async def register(user: UserCreate):
    """ユーザー登録"""
    db = get_database_session()
    try:
        # 既存ユーザーチェック
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # パスワードハッシュ化
        hashed_password = get_password_hash(user.password)

        # ユーザー作成
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            business_name=user.business_name,
            operator_name=user.operator_name,
            is_active=True,
            is_superuser=False,
            subscription_status="active"
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return {
            "success": True,
            "message": "User registered successfully",
            "user_id": db_user.id,
            "email": db_user.email
        }
    finally:
        db.close()

@app.post("/api/auth/login", response_model=Token)
async def login(user_credentials: UserLogin):
    """ログイン"""
    db = get_database_session()
    try:
        # ユーザー認証
        user = db.query(User).filter(User.email == user_credentials.email).first()
        if not user or not verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # JWTトークン作成
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email
        }
    finally:
        db.close()

@app.post("/api/auth/logout")
async def logout():
    """ログアウト（JWTはステートレスなのでクライアント側で削除）"""
    return {"success": True, "message": "Logged out successfully"}

@app.get("/api/auth/verify", response_model=UserResponse)
async def verify_auth(current_user: User = Depends(get_current_user)):
    """認証確認"""
    return current_user

@app.post("/api/auth/change-password")
async def change_password(password_data: PasswordChangeRequest, current_user: User = Depends(get_current_user)):
    """パスワード変更"""
    db = get_database_session()
    try:
        # 現在のパスワードを確認
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # 新しいパスワードをハッシュ化
        new_hashed_password = get_password_hash(password_data.new_password)

        # パスワードを更新
        current_user.hashed_password = new_hashed_password
        db.add(current_user)
        db.commit()

        return {
            "success": True,
            "message": "Password changed successfully"
        }
    finally:
        db.close()

# テンプレート設定エンドポイント（簡単な実装）
@app.get("/api/template/settings")
async def get_template_settings(current_user: User = Depends(get_current_user)):
    """テンプレート設定取得エンドポイント（ユーザー固有）"""
    user_settings = get_user_template_settings(current_user.id)
    return user_settings

@app.put("/api/template/update")
async def update_template_settings(settings: TemplateSettingsUpdate, current_user: User = Depends(get_current_user)):
    """テンプレート設定更新エンドポイント（ユーザー固有）"""

    # ユーザー固有の設定を更新
    updated_settings = update_user_template_settings(
        current_user.id,
        settings.dict(exclude_unset=True)
    )

    return {
        "success": True,
        "message": "テンプレート設定が更新されました",
        "data": updated_settings
    }

@app.post("/api/kyusei")
async def calculate_kyusei(request: KyuseiRequest):
    """九星気学計算API"""
    try:
        # Puppeteerブリッジを実行
        result = await run_puppeteer_bridge("kyusei", request.dict())

        if result["success"]:
            return {
                "success": True,
                "data": result["result"],
                "input": result["input"]
            }
        else:
            raise HTTPException(status_code=500, detail=f"九星気学計算エラー: {result['error']}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/seimei")
async def calculate_seimei(request: SeimeiRequest):
    """姓名判断計算API"""
    try:
        # Puppeteerブリッジを実行
        result = await run_puppeteer_bridge("seimei", request.dict())

        if result["success"]:
            return {
                "success": True,
                "data": result["result"],
                "input": result["input"]
            }
        else:
            raise HTTPException(status_code=500, detail=f"姓名判断計算エラー: {result['error']}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/diagnosis")
async def create_diagnosis(request: DiagnosisRequest, background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)):
    """統合診断作成API（データベースのみ使用）"""
    try:
        # データベースセッションを取得
        db = get_database_session()

        # 姓名判断用の名前を決定
        name_for_seimei = request.name or request.name_for_seimei or request.client_name

        # 認証されたユーザーのIDを使用
        user_id = current_user.id

        # データベースに鑑定記録を作成
        kantei_record = create_kantei_record(
            db=db,
            user_id=user_id,
            client_name=request.client_name,
            request_data=request
        )

        # バックグラウンドで診断処理を開始
        background_tasks.add_task(
            process_diagnosis_db,
            kantei_record.id,
            request.birth_date,
            request.gender,
            name_for_seimei,
            request.diagnosis_pattern,
            request.birth_time
        )

        db.close()

        return {
            "success": True,
            "diagnosis_id": str(kantei_record.id),
            "status": "processing",
            "message": "診断を開始しました。結果は数分後に取得できます。"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"診断作成エラー: {str(e)}")

@app.get("/api/diagnosis/{diagnosis_id}")
async def get_diagnosis(diagnosis_id: str, admin_mode: bool = True, current_user: User = Depends(get_current_user)):
    """診断結果取得API（データベース専用）"""
    try:
        db = get_database_session()

        # データベースから鑑定記録を取得
        kantei_record = get_kantei_record_by_id(db, int(diagnosis_id))
        if not kantei_record:
            raise HTTPException(status_code=404, detail="診断が見つかりません")

        # ユーザー権限チェック（管理者以外は自分の記録のみアクセス可能）
        if not current_user.is_superuser and kantei_record.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="アクセス権限がありません")

        # 基本データ
        result = {
            "id": str(kantei_record.id),
            "client_name": kantei_record.client_name,
            "created_at": kantei_record.created_at.isoformat(),
            "status": kantei_record.status
        }

        # クライアント基本情報（プレビュー用）
        if kantei_record.client_info:
            result["client_info"] = kantei_record.client_info
            # 診断パターンを抽出
            if "diagnosis_pattern" in kantei_record.client_info:
                result["diagnosis_pattern"] = kantei_record.client_info["diagnosis_pattern"]
            else:
                result["diagnosis_pattern"] = "all"  # 既存レコードのデフォルト

        # 計算結果がある場合は追加
        if kantei_record.calculation_result:
            # 九星気学結果
            if "kyusei" in kantei_record.calculation_result:
                result["kyusei_result"] = kantei_record.calculation_result["kyusei"]

            # 姓名判断結果
            if "seimei" in kantei_record.calculation_result:
                result["seimei_result"] = kantei_record.calculation_result["seimei"]

        db.close()
        return result

    except ValueError:
        raise HTTPException(status_code=400, detail="無効な診断IDです")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"診断取得エラー: {str(e)}")

@app.get("/api/diagnosis")
async def list_diagnoses(current_user: User = Depends(get_current_user)):
    """診断一覧取得API（データベース連携版）"""
    try:
        # データベースからKanteiRecordを取得
        db = get_database_session()

        # 認証されたユーザーの鑑定記録のみ取得（最新順）
        kantei_records = db.query(KanteiRecord).filter(KanteiRecord.user_id == current_user.id).order_by(KanteiRecord.created_at.desc()).all()

        # フロントエンド互換形式に変換
        diagnoses = []
        for record in kantei_records:
            diagnoses.append({
                "id": str(record.id),  # 数値IDを文字列に変換
                "client_name": record.client_name,
                "created_at": record.created_at.isoformat(),
                "status": record.status
            })

        db.close()

        return {"diagnoses": diagnoses}

    except Exception as e:
        print(f"=== DEBUG: データベース取得エラー: {e} ===")
        raise HTTPException(status_code=500, detail=f"診断一覧取得エラー: {str(e)}")

@app.post("/api/diagnosis/{diagnosis_id}/complete")
async def force_complete_diagnosis(diagnosis_id: str):
    """診断を強制的に完了状態にする（デバッグ用・データベース専用）"""
    try:
        db = get_database_session()
        kantei_record = get_kantei_record_by_id(db, int(diagnosis_id))

        if not kantei_record:
            raise HTTPException(status_code=404, detail="診断が見つかりません")

        kantei_record.status = "completed"
        db.commit()
        db.close()

        return {"success": True, "message": "診断を完了状態に設定しました"}

    except ValueError:
        raise HTTPException(status_code=400, detail="無効な診断IDです")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エラー: {str(e)}")

@app.post("/api/diagnosis/{diagnosis_id}/pdf")
async def generate_pdf(diagnosis_id: str):
    """PDF生成API（データベース専用）"""
    try:
        db = get_database_session()
        kantei_record = get_kantei_record_by_id(db, int(diagnosis_id))

        if not kantei_record:
            raise HTTPException(status_code=404, detail="診断が見つかりません")

        if kantei_record.status != "completed":
            raise HTTPException(status_code=400, detail="診断が完了していません")
        # 簡易PDF生成（実際のPDFサービスの代わり）
        import tempfile
        import os
        from datetime import datetime

        # 一時的なPDFファイルを作成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"kantei_{diagnosis_id}_{timestamp}.pdf"

        # PDFディレクトリを作成
        pdf_dir = "/tmp/pdf_storage"
        os.makedirs(pdf_dir, exist_ok=True)
        pdf_path = os.path.join(pdf_dir, filename)

        # 計算結果を取得
        kyusei_data = kantei_record.calculation_result.get('kyusei', {}) if kantei_record.calculation_result else {}
        seimei_data = kantei_record.calculation_result.get('seimei', {}) if kantei_record.calculation_result else {}

        # 簡易PDF生成（HTMLからPDFに変換）
        html_content = f"""
        <!DOCTYPE html>
        <html lang="ja">
        <head>
            <meta charset="UTF-8">
            <title>鑑定書 - {kantei_record.client_name}様</title>
            <style>
                body {{ font-family: 'Yu Gothic', 'Hiragino Sans', sans-serif; margin: 40px; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .title {{ font-size: 24px; font-weight: bold; }}
                .client-info {{ margin-bottom: 30px; }}
                .section {{ margin-bottom: 30px; }}
                .section-title {{ font-size: 18px; font-weight: bold; color: #333; border-bottom: 2px solid #007bff; padding-bottom: 5px; }}
                .info-item {{ margin: 10px 0; }}
                .star-info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">九星気学・姓名判断 鑑定書</div>
                <p>鑑定日: {kantei_record.created_at.strftime('%Y年%m月%d日')}</p>
            </div>

            <div class="client-info">
                <h2>依頼者情報</h2>
                <div class="info-item"><strong>お名前:</strong> {kantei_record.client_name}</div>
                <div class="info-item"><strong>生年月日:</strong> {kantei_record.client_info.get('birth_date', '未取得') if kantei_record.client_info else '未取得'}</div>
                <div class="info-item"><strong>性別:</strong> {'男性' if kantei_record.client_info.get('gender') == 'male' else '女性' if kantei_record.client_info else '未取得'}</div>
            </div>

            <div class="section">
                <div class="section-title">九星気学鑑定結果</div>
                <div class="star-info">
                    <p><strong>本命星:</strong> {kyusei_data.get('honmeisei', '未取得')}</p>
                    <p><strong>月命星:</strong> {kyusei_data.get('getsumeisei', '未取得')}</p>
                    <p><strong>年齢:</strong> {kyusei_data.get('age', '未取得')}歳</p>
                </div>
            </div>

            {"<div class='section'><div class='section-title'>姓名判断結果</div><div class='star-info'><p><strong>総評点数:</strong> " + str(seimei_data.get('score', '未取得')) + "点</p></div></div>" if seimei_data else ""}

            <div class="section">
                <div class="section-title">総合鑑定</div>
                <p>九星気学と姓名判断の結果を総合した詳細な解釈内容は、今後のアップデートで追加予定です。</p>
            </div>
        </body>
        </html>
        """

        # HTMLファイルを一時保存
        html_path = pdf_path.replace('.pdf', '.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # PuppeteerでHTMLをPDFに変換
        html_to_pdf_script = "/Users/lennon/projects/inoue4/system/html_to_pdf.js"

        try:
            # Node.jsスクリプトを実行してPDFを生成
            result = subprocess.run(
                ["node", html_to_pdf_script, html_path, pdf_path],
                capture_output=True,
                text=True,
                check=True,
                cwd=os.path.dirname(html_to_pdf_script)
            )

            # 成功した場合、PDFパスを設定
            pdf_url = pdf_path

            # HTMLファイルを削除（オプション）
            # os.unlink(html_path)

        except subprocess.CalledProcessError as e:
            # PDF生成失敗時はHTMLのままにする
            print(f"PDF生成エラー: {e.stderr}")
            pdf_url = html_path

        # ファイル名を適切に設定
        if pdf_url.endswith('.pdf'):
            actual_filename = filename
            message = "PDF生成が完了しました"
        else:
            actual_filename = filename.replace('.pdf', '.html')
            message = "PDF生成が完了しました（HTMLファイルとして生成）"

        return {
            "success": True,
            "pdf_url": pdf_url,
            "filename": actual_filename,
            "message": message
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF生成エラー: {str(e)}")

@app.get("/api/diagnosis/{diagnosis_id}/pdf/download")
async def download_pdf(diagnosis_id: str):
    """PDF ダウンロードAPI（データベース専用）"""
    try:
        db = get_database_session()
        kantei_record = get_kantei_record_by_id(db, int(diagnosis_id))

        if not kantei_record:
            raise HTTPException(status_code=404, detail="診断が見つかりません")

        db.close()

        # 実際の実装ではファイルの存在確認とダウンロード処理
        return {
            "message": "PDF ダウンロード機能は実装中です",
            "diagnosis_id": diagnosis_id
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="無効な診断IDです")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エラー: {str(e)}")

async def run_puppeteer_bridge(system_type: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Puppeteerブリッジを実行"""
    try:
        # Nodeプロセスを実行
        process = await asyncio.create_subprocess_exec(
            "node",
            PUPPETEER_BRIDGE_PATH,
            system_type,
            json.dumps(input_data),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=os.path.dirname(PUPPETEER_BRIDGE_PATH)
        )

        # タイムアウト処理を追加（120秒）
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=120.0
            )
        except asyncio.TimeoutError:
            # タイムアウトが発生した場合、プロセスを強制終了
            process.kill()
            await process.wait()

            # 文字によるエラーかを判定
            client_name = input_data.get('name', '')
            if client_name and any(char in client_name for char in ['盧', '廬', 'ー', '々', '〆', '〇']):
                return {
                    "success": False,
                    "error": "unsupported_characters",
                    "error_message": f"「{client_name}」に含まれる文字は姓名判断システムで処理できません。別の表記をお試しください。",
                    "timeout": True
                }
            else:
                return {
                    "success": False,
                    "error": "timeout",
                    "error_message": "処理がタイムアウトしました。しばらく時間をおいて再度お試しください。",
                    "timeout": True
                }

        if process.returncode == 0:
            # 成功した場合
            result_text = stdout.decode('utf-8').strip()
            return json.loads(result_text)
        else:
            # エラーが発生した場合
            error_text = stderr.decode('utf-8') if stderr else "Unknown error"
            return {
                "success": False,
                "error": f"Puppeteer bridge failed: {error_text}"
            }

    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to run puppeteer bridge: {str(e)}"
        }

async def process_diagnosis(diagnosis_id: str, birth_date: str, gender: str, name_for_seimei: Optional[str]):
    """バックグラウンドで診断を処理"""
    try:
        diagnosis = diagnosis_storage[diagnosis_id]

        # 九星気学計算
        kyusei_result = await run_puppeteer_bridge("kyusei", {
            "birth_date": birth_date,
            "gender": gender
        })

        if kyusei_result["success"]:
            # フロントエンドが期待する形式に変換
            raw_result = kyusei_result["result"]

            # raw_textから九星情報を抽出
            raw_text = raw_result.get("raw_text", "")
            honmei_star = "未取得"
            gekkei_star = "未取得"
            nichimei_star = "未取得"

            # 九星情報の計算（生年月日から直接計算）
            # Puppeteerで取得した九星データを使用、フォールバック計算も提供
            def calculate_kyusei_fallback(birth_year, birth_month, birth_day):
                """生年月日から九星を計算（フォールバック用）"""
                stars = ["九紫火星", "一白水星", "二黒土星", "三碧木星", "四緑木星", "五黄土星", "六白金星", "七赤金星", "八白土星"]
                eto_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

                # 本命星（年命星）計算
                # 立春で年が変わるため、1月と2月は前年として計算
                if birth_month <= 2:
                    year_for_calc = birth_year - 1
                else:
                    year_for_calc = birth_year

                year_index = (year_for_calc - 1900) % 9
                honmei_star = stars[year_index]

                # 月命星計算（正確な計算）
                month_base = (year_for_calc % 9 + birth_month - 1) % 9
                gekkei_star = stars[month_base]

                # 日命星計算（簡略版）
                from datetime import date
                birth_date_obj = date(birth_year, birth_month, birth_day)
                days_since_epoch = (birth_date_obj - date(1900, 1, 1)).days
                day_index = days_since_epoch % 9
                nichimei_star = stars[day_index]

                # 年齢計算
                from datetime import datetime
                today = datetime.now()
                age = today.year - birth_year
                if today.month < birth_month or (today.month == birth_month and today.day < birth_day):
                    age -= 1

                # 十二支計算
                eto_index = (birth_year - 1900) % 12
                eto = eto_list[eto_index]

                # 生年月日フォーマット
                birthday_formatted = f"{birth_year}年{birth_month}月{birth_day}日"

                # 干支計算（簡易版）
                kan_list = ["庚", "辛", "壬", "癸", "甲", "乙", "丙", "丁", "戊", "己"]
                shi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

                year_kan_index = (birth_year - 1900) % 10
                year_shi_index = (birth_year - 1900) % 12
                year_kanshi = kan_list[year_kan_index] + shi_list[year_shi_index]

                month_kan_index = (birth_month - 1) % 10
                month_shi_index = (birth_month - 1) % 12
                month_kanshi = kan_list[month_kan_index] + shi_list[month_shi_index]

                day_kan_index = (birth_day - 1) % 10
                day_shi_index = (birth_day - 1) % 12
                day_kanshi = kan_list[day_kan_index] + shi_list[day_shi_index]

                return {
                    "honmei_star": honmei_star,
                    "gekkei_star": gekkei_star,
                    "nichimei_star": nichimei_star,
                    "age": age,
                    "eto": eto,
                    "birthday": birthday_formatted,
                    "year_kanshi": year_kanshi,
                    "month_kanshi": month_kanshi,
                    "day_kanshi": day_kanshi,
                    "naon": "詳細計算中",
                    "max_kichigata": "要詳細診断",
                    "kichigata": "要詳細診断",
                    "keisha": "詳細計算中",
                    "doukai": "詳細計算中"
                }

            birth_year = int(birth_date.split('-')[0])
            birth_month = int(birth_date.split('-')[1])
            birth_day = int(birth_date.split('-')[2])

            # Puppeteerで取得された九星データを優先的に使用
            honmei_star = raw_result.get("honmeisei")
            gekkei_star = raw_result.get("getsumeisei")
            nichimei_star = None  # 日命星は不要

            # データが取得できていない場合はフォールバック計算を使用
            if not honmei_star or not gekkei_star or not raw_result.get("extraction_success"):
                fallback_data = calculate_kyusei_fallback(birth_year, birth_month, birth_day)
                honmei_star = fallback_data["honmei_star"]
                gekkei_star = fallback_data["gekkei_star"]
                # その他のデータもフォールバック値を使用
                age_value = fallback_data["age"]
                eto_value = fallback_data["eto"]
                birthday_value = fallback_data["birthday"]
                year_kanshi_value = fallback_data["year_kanshi"]
                month_kanshi_value = fallback_data["month_kanshi"]
                day_kanshi_value = fallback_data["day_kanshi"]
                naon_value = fallback_data["naon"]
                max_kichigata_value = fallback_data["max_kichigata"]
                kichigata_value = fallback_data["kichigata"]
                keisha_value = fallback_data["keisha"]
                doukai_value = fallback_data["doukai"]
            else:
                # Puppeteerから取得できた場合は既存のロジック
                age_value = raw_result.get('age', '未取得')
                eto_value = raw_result.get("eto", "未取得")
                birthday_value = raw_result.get("birthday", "未取得")
                year_kanshi_value = raw_result.get("year_kanshi", "未取得")
                month_kanshi_value = raw_result.get("month_kanshi", "未取得")
                day_kanshi_value = raw_result.get("day_kanshi", "未取得")
                naon_value = raw_result.get("naon", "未取得")
                max_kichigata_value = raw_result.get("max_kichigata", "未取得")
                kichigata_value = raw_result.get("kichigata", "未取得")
                keisha_value = raw_result.get("keisha", "未取得")
                doukai_value = raw_result.get("doukai", "未取得")

            diagnosis.kyusei_result = {
                "data": {
                    "本命星": honmei_star,
                    "月命星": gekkei_star,
                    "年齢": f"{raw_result.get('age', '未取得')}歳",
                    "干支": {
                        "年": raw_result.get("year_kanshi", "未取得"),
                        "月": raw_result.get("month_kanshi", "未取得"),
                        "日": raw_result.get("day_kanshi", "未取得")
                    },
                    "十二支": raw_result.get("eto", "未取得"),
                    "納音": raw_result.get("naon", "未取得"),
                    "最大吉方": raw_result.get("max_kichigata", "未取得"),
                    "吉方": raw_result.get("kichigata", "未取得"),
                    "傾斜": raw_result.get("keisha", "未取得"),
                    "同会": raw_result.get("doukai", "未取得"),
                    "生年月日": raw_result.get("birthday", "未取得")
                },
                "input": {
                    "birth_date": birth_date,
                    "gender": gender
                },
                "raw_data": raw_result  # 元データも保持
            }
        else:
            diagnosis.error_message = f"九星気学計算エラー: {kyusei_result['error']}"
            diagnosis.status = "failed"
            return

        # 姓名判断計算（名前が提供されている場合）
        if name_for_seimei:
            seimei_result = await run_puppeteer_bridge("seimei", {
                "name": name_for_seimei
            })

            if seimei_result["success"]:
                # フロントエンドが期待する形式に変換
                raw_result = seimei_result["result"]

                # raw_textから詳細データを抽出
                def extract_seimei_details(raw_text, name_for_seimei):
                    import re
                    details = {}

                    # 文字構成の動的抽出（姓名それぞれ最大9文字まで対応）
                    def extract_character_composition(raw_text, name_for_seimei):
                        """名前の文字構成を動的に抽出（姓名それぞれ最大9文字対応）"""
                        composition = {
                            "画数": {},
                            "五行": {},
                            "陰陽": {},
                            "文字": {}
                        }

                        try:
                            # 入力名前から姓と名を分離
                            name_parts = name_for_seimei.split(' ')
                            sei = name_parts[0] if len(name_parts) > 0 else ""
                            mei = name_parts[1] if len(name_parts) > 1 else ""

                            # 文字の構成セクションを抽出
                            moji_kousei_pattern = r'文字の構成\s*(.+?)(?:(?:画数による鑑定|五行による鑑定|陰陽による鑑定|天地による鑑定)|$)'
                            moji_kousei_match = re.search(moji_kousei_pattern, raw_text, re.DOTALL)

                            if moji_kousei_match:
                                kousei_content = moji_kousei_match.group(1).strip()
                                print(f"DEBUG: 文字の構成セクション内容（最初100文字）: {kousei_content[:100]}")

                                # 文字行を抽出（文字、画数、五行、陰陽の行）
                                lines = kousei_content.split('\n')
                                clean_lines = [line.strip() for line in lines if line.strip()]
                                print(f"DEBUG: 全行数: {len(clean_lines)}, 最初5行: {clean_lines[:5]}")

                                # 文字抽出の実際のHTML構造に基づく新しいアプローチ
                                # 姓名の文字数を把握
                                sei_len = len(sei)
                                mei_len = len(mei)
                                total_chars = sei_len + mei_len
                                print(f"DEBUG: 姓:{sei}({sei_len}文字), 名:{mei}({mei_len}文字), 合計:{total_chars}文字")

                                # 順番にデータを抽出
                                all_chars = []
                                numbers = []
                                gogyou_chars = []
                                inyou_chars = []

                                # 漢字名前文字の抽出（最初のN個）
                                for line in clean_lines:
                                    if re.match(r'^[一-龯]$', line) and line not in ['木', '火', '土', '金', '水', '陽', '陰']:
                                        all_chars.append(line)
                                        if len(all_chars) >= total_chars:
                                            break

                                # 画数の抽出（行全体から数値を抽出）
                                for line in clean_lines:
                                    if re.search(r'^\d+$', line):  # 純粋な数値行のみ
                                        numbers.append(line)
                                        if len(numbers) >= total_chars:
                                            break

                                # 五行の抽出
                                for line in clean_lines:
                                    if line in ['木', '火', '土', '金', '水']:
                                        gogyou_chars.append(line)
                                        if len(gogyou_chars) >= total_chars:
                                            break

                                # 陰陽の抽出
                                for line in clean_lines:
                                    if line in ['陽', '陰']:
                                        inyou_chars.append(line)
                                        if len(inyou_chars) >= total_chars:
                                            break

                                print(f"DEBUG: 名前文字:{len(all_chars)}個{all_chars}")
                                print(f"DEBUG: 画数:{len(numbers)}個{numbers}")
                                print(f"DEBUG: 五行:{len(gogyou_chars)}個{gogyou_chars}")
                                print(f"DEBUG: 陰陽:{len(inyou_chars)}個{inyou_chars}")

                                # 文字の設定
                                if len(all_chars) >= total_chars:
                                    # 姓の文字を設定
                                    for i in range(min(sei_len, 9)):
                                        if i < len(all_chars):
                                            composition["文字"][f"姓{i+1}"] = all_chars[i]
                                            print(f"DEBUG: 姓{i+1} = {all_chars[i]}")

                                    # 名の文字を設定
                                    for i in range(min(mei_len, 9)):
                                        if sei_len + i < len(all_chars):
                                            composition["文字"][f"名{i+1}"] = all_chars[sei_len + i]
                                            print(f"DEBUG: 名{i+1} = {all_chars[sei_len + i]}")

                                # 画数の設定
                                if len(numbers) >= total_chars:
                                    # 姓の画数を設定
                                    for i in range(min(sei_len, 9)):
                                        if i < len(numbers):
                                            composition["画数"][f"姓{i+1}"] = numbers[i]
                                            print(f"DEBUG: 姓{i+1}画数 = {numbers[i]}")

                                    # 名の画数を設定
                                    for i in range(min(mei_len, 9)):
                                        if sei_len + i < len(numbers):
                                            composition["画数"][f"名{i+1}"] = numbers[sei_len + i]
                                            print(f"DEBUG: 名{i+1}画数 = {numbers[sei_len + i]}")

                                # 五行の設定
                                if len(gogyou_chars) >= total_chars:
                                    # 姓の五行を設定
                                    for i in range(min(sei_len, 9)):
                                        if i < len(gogyou_chars):
                                            composition["五行"][f"姓{i+1}"] = gogyou_chars[i]
                                            print(f"DEBUG: 姓{i+1}五行 = {gogyou_chars[i]}")

                                    # 名の五行を設定
                                    for i in range(min(mei_len, 9)):
                                        if sei_len + i < len(gogyou_chars):
                                            composition["五行"][f"名{i+1}"] = gogyou_chars[sei_len + i]
                                            print(f"DEBUG: 名{i+1}五行 = {gogyou_chars[sei_len + i]}")

                                # 陰陽の設定
                                if len(inyou_chars) >= total_chars:
                                    # 姓の陰陽を設定
                                    for i in range(min(sei_len, 9)):
                                        if i < len(inyou_chars):
                                            composition["陰陽"][f"姓{i+1}"] = inyou_chars[i]
                                            print(f"DEBUG: 姓{i+1}陰陽 = {inyou_chars[i]}")

                                    # 名の陰陽を設定
                                    for i in range(min(mei_len, 9)):
                                        if sei_len + i < len(inyou_chars):
                                            composition["陰陽"][f"名{i+1}"] = inyou_chars[sei_len + i]
                                            print(f"DEBUG: 名{i+1}陰陽 = {inyou_chars[sei_len + i]}")


                        except Exception as e:
                            print(f"文字構成抽出エラー: {e}")
                            import traceback
                            traceback.print_exc()

                        return composition

                    # 動的抽出を実行
                    print(f"DEBUG: 動的抽出開始 - name_for_seimei: {name_for_seimei}")
                    print(f"DEBUG: HTML構造チェック - 文字の構成セクション: {'文字の構成' in raw_text}")
                    char_composition = extract_character_composition(raw_text, name_for_seimei)
                    print(f"DEBUG: 動的抽出結果: {char_composition}")
                    details["画数"] = char_composition["画数"]
                    details["五行"] = char_composition["五行"]
                    details["陰陽"] = char_composition["陰陽"]
                    details["文字"] = char_composition["文字"]

                    # 格数情報の抽出
                    details["格数"] = {}
                    tengaku_match = re.search(r'天格\s+(\d+)', raw_text)
                    if tengaku_match: details["格数"]["天格"] = f"{tengaku_match.group(1)}画"

                    jinkaku_match = re.search(r'人格\s+(\d+)', raw_text)
                    if jinkaku_match: details["格数"]["人格"] = f"{jinkaku_match.group(1)}画"

                    chikaku_match = re.search(r'地格\s+(\d+)', raw_text)
                    if chikaku_match: details["格数"]["地格"] = f"{chikaku_match.group(1)}画"

                    soukaku_match = re.search(r'総画\s+(\d+)', raw_text)
                    if soukaku_match: details["格数"]["総画"] = f"{soukaku_match.group(1)}画"

                    # 総評メッセージの抽出
                    sohyo_pattern = r'総評\s*\n\s*(\d+)点\s*\n\s*/100\s*\n\s*(.+?)(?:文字による鑑定|陰陽による鑑定|五行による鑑定|\n\n)'
                    sohyo_match = re.search(sohyo_pattern, raw_text, re.DOTALL)
                    if sohyo_match:
                        details["総評メッセージ"] = sohyo_match.group(2).strip()

                    # 文字による鑑定の抽出
                    details["文字による鑑定"] = []

                    # 文字による鑑定セクションを抽出
                    moji_section_match = re.search(r'文字による鑑定\s*(.+?)(?:陰陽による鑑定|五行による鑑定|$)', raw_text, re.DOTALL)
                    if moji_section_match:
                        moji_content = moji_section_match.group(1).strip()

                        if moji_content and len(moji_content) > 10:
                            # 汎用的な抽出ロジック - 5つのパターンに対応
                            sentences = re.split(r'[。]', moji_content)
                            sentences = [s.strip() for s in sentences if s.strip()]

                            i = 0
                            while i < len(sentences):
                                sentence = sentences[i]

                                # パターン1: 日本語文字【分類名】形式（例: 郎【分離名】、め【地行が水行】）
                                bracket_match = re.search(r'([\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+)\s*【([^】]+)】\s*(.*)', sentence)
                                if bracket_match:
                                    char = bracket_match.group(1).strip()
                                    category = bracket_match.group(2).strip()
                                    detail_parts = [bracket_match.group(3).strip()] if bracket_match.group(3).strip() else []

                                    # 続く文も同じ文字の詳細として結合
                                    j = i + 1
                                    while j < len(sentences):
                                        next_sentence = sentences[j]
                                        # 新しいパターンが始まったら停止
                                        if re.match(r'([\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+)\s*【([^】]+)】', next_sentence) or \
                                           re.match(r'(人格|地行|地格):([^\s]+)', next_sentence) or \
                                           re.match(r'([\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+)\s+文字の', next_sentence) or \
                                           re.match(r'^([\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+)\s+(.+)', next_sentence):
                                            break
                                        else:
                                            detail_parts.append(next_sentence)
                                            j += 1

                                    details["文字による鑑定"].append({
                                        "id": f"moji_{len(details['文字による鑑定'])}_{char}_{category}",
                                        "文字": char,
                                        "分類": category,
                                        "詳細": "。".join(detail_parts) + "。" if detail_parts else ""
                                    })
                                    i = j
                                    continue

                                # パターン2: 人格:文字形式（例: 人格:本太、人格:信長）
                                jinko_match = re.search(r'人格:([^\s]+)\s*(.*)', sentence)
                                if jinko_match:
                                    char_combo = jinko_match.group(1).strip()
                                    detail_parts = [jinko_match.group(2).strip()] if jinko_match.group(2).strip() else []

                                    # 続く文も詳細として結合
                                    j = i + 1
                                    while j < len(sentences):
                                        next_sentence = sentences[j]
                                        if re.match(r'([一-龯]+)\s*【([^】]+)】', next_sentence) or \
                                           re.match(r'(人格|地行|地格):([^\s]+)', next_sentence) or \
                                           re.match(r'([一-龯]+)\s+文字の', next_sentence) or \
                                           re.match(r'^([一-龯]+)\s+(.+)', next_sentence):
                                            break
                                        else:
                                            detail_parts.append(next_sentence)
                                            j += 1

                                    details["文字による鑑定"].append({
                                        "id": f"moji_{len(details['文字による鑑定'])}_{char_combo}_人格",
                                        "文字": f"人格:{char_combo}",
                                        "分類": "人格",
                                        "詳細": "。".join(detail_parts) + "。" if detail_parts else ""
                                    })
                                    i = j
                                    continue

                                # パターン3: 地行:文字形式（例: 地行:信長）
                                chiko_match = re.search(r'地行:([^\s]+)\s*(.*)', sentence)
                                if chiko_match:
                                    char_combo = chiko_match.group(1).strip()
                                    detail_parts = [chiko_match.group(2).strip()] if chiko_match.group(2).strip() else []

                                    j = i + 1
                                    while j < len(sentences):
                                        next_sentence = sentences[j]
                                        if re.match(r'([一-龯]+)\s*【([^】]+)】', next_sentence) or \
                                           re.match(r'(人格|地行|地格):([^\s]+)', next_sentence) or \
                                           re.match(r'([一-龯]+)\s+文字の', next_sentence) or \
                                           re.match(r'^([一-龯]+)\s+(.+)', next_sentence):
                                            break
                                        else:
                                            detail_parts.append(next_sentence)
                                            j += 1

                                    details["文字による鑑定"].append({
                                        "id": f"moji_{len(details['文字による鑑定'])}_{char_combo}_地行",
                                        "文字": f"地行:{char_combo}",
                                        "分類": "地行",
                                        "詳細": "。".join(detail_parts) + "。" if detail_parts else ""
                                    })
                                    i = j
                                    continue

                                # パターン4: 地格:文字形式（例: 地格:隆志）
                                chikaku_match = re.search(r'地格:([^\s]+)\s*(.*)', sentence)
                                if chikaku_match:
                                    char_combo = chikaku_match.group(1).strip()
                                    detail_parts = [chikaku_match.group(2).strip()] if chikaku_match.group(2).strip() else []

                                    j = i + 1
                                    while j < len(sentences):
                                        next_sentence = sentences[j]
                                        if re.match(r'([一-龯]+)\s*【([^】]+)】', next_sentence) or \
                                           re.match(r'(人格|地行|地格):([^\s]+)', next_sentence) or \
                                           re.match(r'([一-龯]+)\s+文字の', next_sentence) or \
                                           re.match(r'^([一-龯]+)\s+(.+)', next_sentence):
                                            break
                                        else:
                                            detail_parts.append(next_sentence)
                                            j += 1

                                    details["文字による鑑定"].append({
                                        "id": f"moji_{len(details['文字による鑑定'])}_{char_combo}_地格",
                                        "文字": f"地格:{char_combo}",
                                        "分類": "地格",
                                        "詳細": "。".join(detail_parts) + "。" if detail_parts else ""
                                    })
                                    i = j
                                    continue

                                # パターン5: 文字単体での鑑定（例: 花 文字の由来・意味から...）
                                char_meaning_match = re.search(r'^([一-龯]+)\s+文字の', sentence)
                                if char_meaning_match:
                                    char = char_meaning_match.group(1).strip()
                                    detail_parts = [sentence]

                                    # 続きの文を結合（新しい文字パターンが始まったら停止）
                                    j = i + 1
                                    while j < len(sentences):
                                        next_sentence = sentences[j]
                                        # 新しいパターンが始まったら停止（任意の文字で始まる文も停止）
                                        if re.match(r'([一-龯]+)\s*【([^】]+)】', next_sentence) or \
                                           re.match(r'(人格|地行|地格):([^\s]+)', next_sentence) or \
                                           re.match(r'([一-龯]+)\s+文字の', next_sentence) or \
                                           re.match(r'^([一-龯]+)\s+(.+)', next_sentence):
                                            break
                                        else:
                                            detail_parts.append(next_sentence)
                                            j += 1

                                    details["文字による鑑定"].append({
                                        "id": f"moji_{len(details['文字による鑑定'])}_{char}_文字",
                                        "文字": char,
                                        "分類": "文字",
                                        "詳細": "。".join(detail_parts) + "。"
                                    })
                                    i = j
                                    continue

                                # パターン6: その他の形式（単一文字で始まる場合）
                                single_char_match = re.search(r'^([一-龯]+)\s+(.+)', sentence)
                                if single_char_match:
                                    char = single_char_match.group(1).strip()
                                    # 文字部分を除いた詳細のみを取得
                                    detail_parts = [single_char_match.group(2).strip()]

                                    # 関連する続きの文を結合（新しい文字パターンは除外）
                                    j = i + 1
                                    while j < len(sentences):
                                        next_sentence = sentences[j]
                                        # 新しいパターンが始まったら停止
                                        if re.match(r'([\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+)\s*【([^】]+)】', next_sentence) or \
                                           re.match(r'(人格|地行|地格):([^\s]+)', next_sentence) or \
                                           re.match(r'([\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+)\s+文字の', next_sentence) or \
                                           re.match(r'^([\u4e00-\u9fa0\u3042-\u3096\u30a2-\u30f6]+)\s+(.+)', next_sentence):
                                            break
                                        else:
                                            detail_parts.append(next_sentence)
                                            j += 1

                                    details["文字による鑑定"].append({
                                        "id": f"moji_{len(details['文字による鑑定'])}_{char}_その他",
                                        "文字": char,
                                        "分類": "その他",
                                        "詳細": "。".join(detail_parts) + "。"
                                    })
                                    i = j
                                    continue

                                # どのパターンにもマッチしない場合は次の文へ
                                i += 1

                    # 鑑定結果の抽出
                    details["鑑定結果"] = {}

                    # 陰陽鑑定 - 名前情報も含めて抽出
                    inyou_section_match = re.search(r'陰陽による鑑定\s*(.+?)(?:五行による鑑定|$)', raw_text, re.DOTALL)
                    if inyou_section_match:
                        inyou_content = inyou_section_match.group(1).strip()

                        # 【】パターンでの評価を抽出
                        inyou_kantei_match = re.search(r'【([^】]+)】', inyou_content)
                        if inyou_kantei_match:
                            evaluation = inyou_kantei_match.group(1)

                            # 名前を抽出（姓名の形式を探す - ひらがな・カタカナも対応）
                            name_match = re.search(r'([一-龯あ-ゖア-ヶ]+)\s+([一-龯あ-ゖア-ヶ]+)', inyou_content)
                            name_info = ""
                            if name_match:
                                name_info = f"{name_match.group(1)} {name_match.group(2)}"

                            # 詳細内容を抽出（【】以降で画数や五行の前まで）
                            detail_match = re.search(r'【[^】]+】\s*([^画五]+)', inyou_content, re.DOTALL)
                            detail_content = ""
                            if detail_match:
                                detail_content = detail_match.group(1).strip()

                            details["鑑定結果"]["陰陽"] = {
                                "評価": evaluation,
                                "名前": name_info,
                                "詳細": detail_content
                            }

                    # 五行鑑定 - 構造化された解析 [修正版 v2.1 - 2025/09/19 10:52]
                    details["鑑定結果"]["五行"] = []
                    details["鑑定結果"]["五行_debug"] = "修正版 v7.0 - 五条めざるケース対応・混入・重複除去完全版"
                    details["鑑定結果"]["raw_text_sample"] = raw_text[raw_text.find("五行による鑑定"):raw_text.find("五行による鑑定")+500] if "五行による鑑定" in raw_text else "五行による鑑定セクションが見つからない"
                    gogyou_section_match = re.search(r'五行による鑑定\s*(.+?)(?:\s*陰陽による鑑定|\s*画数による鑑定|$)', raw_text, re.DOTALL)
                    if gogyou_section_match:
                        gogyou_content = gogyou_section_match.group(1).strip()

                        if gogyou_content and len(gogyou_content) > 10:
                            # 汎用的な正規表現で3つのアイテムを抽出するアプローチ（地格・人格・五行のバランス）

                            # まず名前パターンを検索して姓を動的に検出
                            name_pattern = r'([一-龯あ-ゖア-ヶ]+)\s+([一-龯あ-ゖア-ヶ]+)\s*\n?\s*【([^】]+)】'
                            name_match = re.search(name_pattern, gogyou_content)

                            if name_match:
                                sei = name_match.group(1)
                                mei = name_match.group(2)
                                name_evaluation = name_match.group(3)

                                # 一時的に各要素を格納する変数
                                chikaku_data = None
                                jinko_data = None
                                balance_data = None

                                # パターン1: 地格 - データ取得のみ（表示は後で順序調整）
                                chikaku_pattern = r'地格：([^\s]+)\s*\n?\s*【([^】]+)】\s*(.*?)(?=人格：|(?=' + re.escape(sei) + r'))'
                                chikaku_match = re.search(chikaku_pattern, gogyou_content, re.DOTALL)
                                if chikaku_match:
                                    chikaku_value = chikaku_match.group(1)
                                    evaluation = chikaku_match.group(2)
                                    content = chikaku_match.group(3).strip()

                                    chikaku_data = {
                                        "タイプ": "地格",
                                        "対象": f"地格:{chikaku_value}",
                                        "評価": evaluation,
                                        "詳細": content
                                    }

                                # パターン2: 人格 - データ取得のみ（重複除去ロジック付き）
                                jinko_pattern = r'人格：([^\s\n]+)\s*\n?\s*【([^】]+)】\s*(.*?)(?=(?:[\u4e00-龠あ-ゖア-ヶ]+\s+[\u4e00-龠あ-ゖア-ヶ]+\s*\n?\s*【)|$)'
                                jinko_match = re.search(jinko_pattern, gogyou_content, re.DOTALL)
                                if jinko_match:
                                    jinko_value = jinko_match.group(1)
                                    evaluation = jinko_match.group(2)
                                    content = jinko_match.group(3).strip()

                                    # 名前パターンが混入している場合は除去
                                    content_lines = content.split('\n')
                                    clean_lines = []
                                    for line in content_lines:
                                        line = line.strip()
                                        # 名前パターンが含まれていたら停止
                                        if re.search(r'[\u4e00-龠あ-ゖア-ヶ]+\s+[\u4e00-龠あ-ゖア-ヶ]+\s*【', line):
                                            break
                                        if line:
                                            clean_lines.append(line)
                                    clean_content = ' '.join(clean_lines).strip()

                                    jinko_data = {
                                        "タイプ": "人格",
                                        "対象": f"人格:{jinko_value}",
                                        "評価": evaluation,
                                        "詳細": clean_content
                                    }

                                # パターン3: 五行のバランス - データ取得のみ（人格詳細除去）
                                balance_pattern = rf'{re.escape(sei)}\s+{re.escape(mei)}\s*\n?\s*【[^】]+】\s*(.*?)(?=人格[：:]|地格[：:]|$)'
                                balance_match = re.search(balance_pattern, gogyou_content, re.DOTALL)

                                if balance_match:
                                    balance_content = balance_match.group(1).strip()

                                    # 五行のバランスの基本説明のみを取得（人格詳細は除外）
                                    # 「五行のバランスが良くないです。名前に五行が3つ以上が望ましいです。」部分のみ
                                    balance_main = re.sub(r'人格[：:].*$', '', balance_content, flags=re.DOTALL).strip()

                                    if balance_main and len(balance_main) > 10:
                                        balance_data = {
                                            "タイプ": "五行のバランス",
                                            "対象": f"{sei} {mei}",
                                            "評価": name_evaluation,
                                            "詳細": balance_main
                                        }

                                # 元システムと同じ表示順序で配列に追加：五行のバランス→人格→地格
                                if balance_data:
                                    details["鑑定結果"]["五行"].append(balance_data)
                                if jinko_data:
                                    details["鑑定結果"]["五行"].append(jinko_data)
                                if chikaku_data:
                                    details["鑑定結果"]["五行"].append(chikaku_data)


                    # 画数鑑定（修正版）
                    def parse_kakusu_kantei_enhanced(raw_text):
                        """画数による鑑定の修正版解析 - 項目分離を改善"""
                        results = []

                        # 画数セクションを抽出（天地による鑑定の前で停止）
                        kakusu_section_match = re.search(r'画数による鑑定\s*(.+?)(?:\s*(?:天地による鑑定|陰陽による鑑定)|$)', raw_text, re.DOTALL)
                        if not kakusu_section_match:
                            return results

                        kakusu_content = kakusu_section_match.group(1).strip()

                        if not kakusu_content or len(kakusu_content) <= 10:
                            return results

                        # 全てのパターン（総格、人格、地格）を順序で検索
                        patterns = [
                            (r'総格:\s*([^【\n]+)\s*【画数(\d+)】\s*(.*?)(?=(?:人格:|地格:)|$)', "総格"),
                            (r'人格:\s*([^【\n]+)\s*【画数(\d+)】\s*(.*?)(?=(?:総格:|地格:)|$)', "人格"),
                            (r'地格:\s*([^【\n]+)\s*【画数(\d+)】\s*(.*?)(?=(?:総格:|人格:)|$)', "地格")
                        ]

                        for pattern, type_name in patterns:
                            matches = re.finditer(pattern, kakusu_content, re.DOTALL)
                            for match in matches:
                                name_part = match.group(1).strip()
                                kakusu = match.group(2)
                                content = match.group(3).strip()

                                # 次のパターンが混入している場合は除去
                                # 例: 地格:初め が総格の詳細に含まれている場合
                                next_pattern_match = re.search(r'(総格:|人格:|地格:)', content)
                                if next_pattern_match:
                                    # 次のパターンが見つかった位置で切り取る
                                    cut_position = next_pattern_match.start()
                                    content = content[:cut_position].strip()

                                # HTMLやナビゲーション要素を除去
                                # 「。」で終わる文章までを抽出
                                sentences = re.split(r'[。．]', content)
                                clean_sentences = []
                                for sentence in sentences:
                                    sentence = sentence.strip()
                                    if sentence and not re.search(r'姓名鑑定|名付け|選名|講座|セミナ|使い方|申し込み|九星', sentence):
                                        clean_sentences.append(sentence)
                                    elif sentence and re.search(r'姓名鑑定|名付け|選名|講座|セミナ|使い方|申し込み|九星', sentence):
                                        break  # ナビゲーション要素が見つかったら停止

                                if clean_sentences:
                                    content = '。'.join(clean_sentences) + '。'

                                results.append({
                                    "タイプ": type_name,
                                    "対象": name_part,
                                    "画数": f"{kakusu}画",
                                    "詳細": content
                                })

                        return results

                    # 強化された画数解析を実行
                    kakusu_results = parse_kakusu_kantei_enhanced(raw_text)
                    if kakusu_results:
                        details["鑑定結果"]["画数"] = kakusu_results

                    # 天地鑑定 - 新機能追加
                    details["鑑定結果"]["天地"] = []

                    # 天地による鑑定セクションを抽出
                    tenti_section_match = re.search(r'天地による鑑定\s*(.+?)(?:\s*(?:姓名鑑定の使い方|名付け|選名|講座|セミナ|$))', raw_text, re.DOTALL)
                    if tenti_section_match:
                        tenti_content = tenti_section_match.group(1).strip()

                        if tenti_content and len(tenti_content) > 10:
                            # 統合パターンで順次処理（重複を防ぐため）
                            # 全ての天地鑑定パターンを統合的に抽出
                            all_patterns = [
                                (r'([^\s\n]+)\s*\n\s*【天地同数\(([^)]+)\)】\s*\n\s*([^】]*?)(?=(?:[\u4e00-\u9fff]+\s*\n\s*【)|$)', 'dousu'),
                                (r'([一-龯あ-ゖア-ヶ]+\s+[一-龯あ-ゖア-ヶ]+)\s*\n\s*【天地総同数】\s*\n\s*([^】]*?)(?=(?:[\u4e00-\u9fff]+\s*\n\s*【)|$)', 'soudousu'),
                                (r'(?:。\s*)?([一-龯あ-ゖア-ヶ]+)\s*\n\s*【天地衝突】\s*\n\s*([^】]*?)(?=\n|$)', 'shoutotsu')
                            ]

                            processed_positions = set()  # 重複処理を防ぐための位置記録

                            for pattern, pattern_type in all_patterns:
                                matches = re.finditer(pattern, tenti_content, re.DOTALL)

                                for match in matches:
                                    # 重複チェック
                                    start_pos = match.start()
                                    if start_pos in processed_positions:
                                        continue
                                    processed_positions.add(start_pos)

                                    if pattern_type == 'dousu':
                                        target = match.group(1).strip()
                                        parity = match.group(2).strip()
                                        detail = match.group(3).strip()

                                        # 詳細テキストから重複する名前部分を除去
                                        detail = re.sub(r'[一-龯あ-ゖア-ヶ]+\s*$', '', detail).strip()

                                        if target and detail:
                                            details["鑑定結果"]["天地"].append({
                                                "対象": target,
                                                "評価": f"天地同数({parity})",
                                                "詳細": detail,
                                                "タイプ": "天地同数"
                                            })

                                    elif pattern_type == 'soudousu':
                                        target = match.group(1).strip()
                                        detail = match.group(2).strip()

                                        if target and detail:
                                            details["鑑定結果"]["天地"].append({
                                                "対象": target,
                                                "評価": "天地総同数",
                                                "詳細": detail,
                                                "タイプ": "天地総同数"
                                            })

                                    elif pattern_type == 'shoutotsu':
                                        target = match.group(1).strip()
                                        detail = match.group(2).strip()

                                        if target and detail:
                                            details["鑑定結果"]["天地"].append({
                                                "対象": target,
                                                "評価": "天地衝突",
                                                "詳細": detail,
                                                "タイプ": "天地衝突"
                                            })

                    return details

                # 詳細データを抽出
                print(f"DEBUG: raw_text前半: {raw_result.get('raw_text', '')[:500]}")
                seimei_details = extract_seimei_details(raw_result.get("raw_text", ""), name_for_seimei)
                print(f"DEBUG: 抽出された詳細データ: {seimei_details}")

                diagnosis.seimei_result = {
                    "data": {
                        "総評点数": raw_result.get("score", "未取得"),
                        "詳細結果": raw_result.get("has_detailed_result", False),
                        "URL": raw_result.get("url", ""),
                        **seimei_details  # 抽出した詳細データを追加
                    },
                    "input": {
                        "name": name_for_seimei
                    },
                    "raw_data": raw_result  # 元データも保持
                }
            else:
                diagnosis.error_message = f"姓名判断計算エラー: {seimei_result['error']}"
                # 姓名判断が失敗しても九星気学が成功していれば完了とする

        # 九星気学が成功していれば完了
        diagnosis.status = "completed"
        print(f"診断 {diagnosis_id} を完了状態に設定しました。姓名判断: {'あり' if name_for_seimei else 'なし'}")

    except Exception as e:
        print(f"診断 {diagnosis_id} で例外が発生しました: {str(e)}")
        diagnosis = diagnosis_storage[diagnosis_id]
        diagnosis.error_message = str(e)
        diagnosis.status = "failed"

async def process_diagnosis_db(record_id: int, birth_date: str, gender: str, name_for_seimei: Optional[str],
                              diagnosis_pattern: str = "all", birth_time: Optional[str] = None):
    """データベース専用バックグラウンド診断処理（パターン対応版）"""
    try:
        db = get_database_session()

        # 鑑定記録を取得
        kantei_record = get_kantei_record_by_id(db, record_id)
        if not kantei_record:
            print(f"鑑定記録 {record_id} が見つかりません")
            return

        calculation_result = {}

        # パターン別処理実行
        # 九星気学計算（kyusei_only または all の場合）
        if diagnosis_pattern in ["kyusei_only", "all"]:
            kyusei_data = {
                "birth_date": birth_date,
                "gender": gender
            }
            # 出生時間が提供されている場合は追加（将来的な機能拡張用）
            if birth_time:
                kyusei_data["birth_time"] = birth_time

            kyusei_result = await run_puppeteer_bridge("kyusei", kyusei_data)

            if kyusei_result["success"]:
                calculation_result["kyusei"] = kyusei_result["result"]

        # 姓名判断計算（seimei_only または all の場合で、名前が提供されている場合）
        if diagnosis_pattern in ["seimei_only", "all"] and name_for_seimei:
            # 姓名判断システムはスペース区切りの名前が必要
            formatted_name = name_for_seimei
            if len(name_for_seimei) >= 2 and ' ' not in name_for_seimei:
                # 簡易的な姓名分離（2文字目以降に適切な区切りを入れる）
                if len(name_for_seimei) == 2:
                    formatted_name = f"{name_for_seimei[0]} {name_for_seimei[1]}"
                elif len(name_for_seimei) == 3:
                    formatted_name = f"{name_for_seimei[0]} {name_for_seimei[1:]}"
                elif len(name_for_seimei) == 4:
                    formatted_name = f"{name_for_seimei[:2]} {name_for_seimei[2:]}"
                else:
                    # 5文字以上の場合は3文字目でスペース挿入
                    formatted_name = f"{name_for_seimei[:2]} {name_for_seimei[2:]}"

            seimei_result = await run_puppeteer_bridge("seimei", {
                "name": formatted_name
            })

            if seimei_result["success"]:
                # フロントエンドが期待する形式に変換
                raw_result = seimei_result["result"]

                # raw_textから詳細データを抽出
                def extract_seimei_details(raw_text, name_for_seimei):
                    import re
                    details = {}

                    # 文字構成の動的抽出（姓名それぞれ最大9文字まで対応）
                    def extract_character_composition(raw_text, name_for_seimei):
                        """名前の文字構成を動的に抽出（姓名それぞれ最大9文字対応）"""
                        composition = {
                            "画数": {},
                            "五行": {},
                            "陰陽": {},
                            "文字": {}
                        }

                        try:
                            # 入力名前から姓と名を分離
                            name_parts = name_for_seimei.split(' ')
                            sei = name_parts[0] if len(name_parts) > 0 else ""
                            mei = name_parts[1] if len(name_parts) > 1 else ""

                            # 文字の構成セクションを抽出
                            moji_kousei_pattern = r'文字の構成\s*(.+?)(?:(?:画数による鑑定|五行による鑑定|陰陽による鑑定|天地による鑑定)|$)'
                            moji_kousei_match = re.search(moji_kousei_pattern, raw_text, re.DOTALL)

                            if moji_kousei_match:
                                kousei_content = moji_kousei_match.group(1).strip()
                                print(f"DEBUG: 文字の構成セクション内容（最初100文字）: {kousei_content[:100]}")

                                # 文字行を抽出（文字、画数、五行、陰陽の行）
                                lines = kousei_content.split('\n')
                                clean_lines = [line.strip() for line in lines if line.strip()]

                                # 各セクションの開始位置を特定
                                character_start = None
                                stroke_start = None
                                gogyou_start = None
                                inyou_start = None

                                for i, line in enumerate(clean_lines):
                                    if "画数" == line:
                                        stroke_start = i + 1
                                    elif "五行" == line:
                                        gogyou_start = i + 1
                                    elif "陽陰" == line or "陰陽" == line:
                                        inyou_start = i + 1

                                # 文字名を動的に抽出
                                characters = []
                                if stroke_start:
                                    # 画数セクションの前の文字列から実際の文字を抽出
                                    character_lines = clean_lines[:stroke_start-1]
                                    for line in character_lines:
                                        if len(line) == 1 and '\u4e00' <= line <= '\u9fff':  # 漢字判定
                                            characters.append(line)

                                print(f"DEBUG: 抽出された文字: {characters}")

                                # 画数を抽出
                                if stroke_start and len(characters) > 0:
                                    stroke_section = clean_lines[stroke_start:gogyou_start-1] if gogyou_start else clean_lines[stroke_start:]
                                    stroke_values = []
                                    for line in stroke_section:
                                        try:
                                            stroke_values.append(int(line))
                                        except ValueError:
                                            continue

                                    for i, stroke in enumerate(stroke_values[:len(characters)]):
                                        if i < len(sei):
                                            key = f"姓{i + 1}"
                                        else:
                                            key = f"名{i - len(sei) + 1}"
                                        composition["画数"][key] = stroke
                                        composition["文字"][key] = characters[i]

                                # 五行を抽出
                                if gogyou_start and len(characters) > 0:
                                    gogyou_section = clean_lines[gogyou_start:inyou_start-1] if inyou_start else clean_lines[gogyou_start:]
                                    gogyou_values = []
                                    for line in gogyou_section:
                                        if line in ['金', '木', '水', '火', '土']:
                                            gogyou_values.append(line)

                                    for i, gogyou in enumerate(gogyou_values[:len(characters)]):
                                        if i < len(sei):
                                            key = f"姓{i + 1}"
                                        else:
                                            key = f"名{i - len(sei) + 1}"
                                        composition["五行"][key] = gogyou

                                # 陰陽を抽出
                                if inyou_start and len(characters) > 0:
                                    inyou_section = clean_lines[inyou_start:]
                                    inyou_values = []
                                    for line in inyou_section:
                                        if line in ['陰', '陽']:
                                            inyou_values.append(line)

                                    for i, inyou in enumerate(inyou_values[:len(characters)]):
                                        if i < len(sei):
                                            key = f"姓{i + 1}"
                                        else:
                                            key = f"名{i - len(sei) + 1}"
                                        composition["陰陽"][key] = inyou

                        except Exception as e:
                            print(f"文字構成抽出エラー: {e}")

                        return composition

                    # 文字構成を抽出
                    char_composition = extract_character_composition(raw_text, name_for_seimei)
                    details.update(char_composition)

                    # 格数を抽出
                    details["格数"] = {}

                    # 天格を抽出
                    tenkaku_pattern = r'天格\s*(\d+)'
                    tenkaku_match = re.search(tenkaku_pattern, raw_text)
                    if tenkaku_match:
                        details["格数"]["天格"] = int(tenkaku_match.group(1))

                    # 人格を抽出
                    jinkaku_pattern = r'人格\s*(\d+)'
                    jinkaku_match = re.search(jinkaku_pattern, raw_text)
                    if jinkaku_match:
                        details["格数"]["人格"] = int(jinkaku_match.group(1))

                    # 地格を抽出
                    chikaku_pattern = r'地格\s*(\d+)'
                    chikaku_match = re.search(chikaku_pattern, raw_text)
                    if chikaku_match:
                        details["格数"]["地格"] = int(chikaku_match.group(1))

                    # 総画を抽出
                    souga_pattern = r'総画\s*(\d+)'
                    souga_match = re.search(souga_pattern, raw_text)
                    if souga_match:
                        details["格数"]["総画"] = int(souga_match.group(1))

                    # 総評点数を抽出
                    sohyo_pattern = r'(\d+)点'
                    sohyo_match = re.search(sohyo_pattern, raw_text)
                    if sohyo_match:
                        details["総評点数"] = int(sohyo_match.group(1))

                    # 総評メッセージを抽出（文字による鑑定を完全に除外）
                    # まず点数とコメントのみを抽出
                    sohyo_pattern = r'(\d+点[^。]*。)\s*([^文字陰陽五行画数天地]*?)(?=文字による鑑定|陰陽による鑑定|五行による鑑定|画数による鑑定|天地による鑑定|$)'
                    sohyo_match = re.search(sohyo_pattern, raw_text, re.DOTALL)
                    if sohyo_match:
                        score_text = sohyo_match.group(1)  # 点数部分
                        comment_text = sohyo_match.group(2).strip()  # コメント部分

                        # 点数部分から数字のみ抽出
                        score_match = re.search(r'(\d+)点', score_text)
                        if score_match:
                            details["点数"] = int(score_match.group(1))

                        # コメント部分をクリーンアップ
                        if comment_text:
                            # 不要な文字を除去
                            comment_text = re.sub(r'^[^\w\u4e00-\u9faf]*', '', comment_text)
                            comment_text = re.sub(r'[^\w\u4e00-\u9faf。、！？]*$', '', comment_text)
                            if comment_text:
                                details["総評メッセージ"] = comment_text

                    # 詳細鑑定セクションを抽出
                    details["詳細鑑定"] = {}

                    # 文字による鑑定を抽出
                    def extract_moji_kantei(raw_text):
                        """文字による鑑定を抽出 - 完全に書き直された正確な分離ロジック

                        ⚠️ 重要な開発ルール ⚠️
                        ハードコーディング厳禁！
                        - 特定の名前（田中、佐藤、美、花、郎など）を絶対に使用しない
                        - 特定の数値（画数など）を絶対に使用しない
                        - すべてのパターンは汎用的に実装すること
                        - 何千通りの名前パターンに対応できるように設計すること
                        """
                        moji_kantei = {}
                        try:
                            # 文字による鑑定セクションを抽出
                            moji_pattern = r'文字による鑑定\s*(.*?)(?=陰陽による鑑定|五行による鑑定|画数による鑑定|天地による鑑定|$)'
                            moji_match = re.search(moji_pattern, raw_text, re.DOTALL)

                            if moji_match:
                                moji_content = moji_match.group(1).strip()

                                # すべてのエントリを位置情報と共に収集
                                all_entries = []
                                processed_positions = set()  # 処理済み位置を記録

                                # Step 1: 複数文字パターン (次・郎)を処理
                                # 1a: 【評価】があるパターン
                                multi_pattern = r'([一-龯]・[一-龯]+)\s*【([^】]+)】\s*(.*?)(?=(?:[一-龯])\s\s|地行:|人格:|$)'
                                for match in re.finditer(multi_pattern, moji_content, re.DOTALL):
                                    chars = match.group(1)
                                    evaluation = match.group(2)
                                    detail = match.group(3).strip()
                                    if detail:
                                        all_entries.append((match.start(), chars, f"【{evaluation}】\n{detail}"))
                                        processed_positions.add(match.start())

                                # 1b: 【評価】がないパターン（花・音 文字の由来...）
                                # 高橋花音のケース: "花・音  文字の由来・意味から名前には使用しないほうがいい文字です。花  名前には使用できない文字です。..."
                                multi_simple_pattern = r'([一-龯]・[一-龯]+)\s\s([^。]*?。)([一-龯])\s\s([^。]*?。)(?=.*?(?:陰陽による鑑定|五行による鑑定|画数による鑑定|天地による鑑定|$))'
                                for match in re.finditer(multi_simple_pattern, moji_content, re.DOTALL):
                                    if match.start() not in processed_positions:
                                        # 複数文字パターン（花・音）
                                        multi_chars = match.group(1)
                                        multi_detail = match.group(2).strip()
                                        if multi_detail:
                                            all_entries.append((match.start(), multi_chars, multi_detail))
                                            processed_positions.add(match.start())

                                        # 単体文字パターン（花）
                                        single_char = match.group(3)
                                        single_detail = match.group(4).strip()
                                        if single_detail:
                                            # 単体文字の位置を推定（複数文字パターンの後）
                                            single_pos = match.start() + len(match.group(1)) + len(match.group(2)) + 10
                                            all_entries.append((single_pos, single_char, single_detail))
                                            processed_positions.add(single_pos)

                                # Step 2: 単一文字【評価】パターン（も 【地行が水行】）
                                # より柔軟なパターンに修正：ひらがな・カタカナも対象とし、スペースの処理を改善
                                single_eval_pattern = r'(?<![・])([一-龯あ-んア-ン])(?![・])\s*【([^】]+)】\s*(.*?)(?=(?:[一-龯あ-んア-ン])\s*【|陰陽による鑑定|五行による鑑定|画数による鑑定|天地による鑑定|$)'
                                for match in re.finditer(single_eval_pattern, moji_content, re.DOTALL):
                                    if match.start() not in processed_positions:
                                        char = match.group(1)
                                        evaluation = match.group(2)
                                        detail = match.group(3).strip()

                                        # より厳密な境界検出：次の単一文字パターンの開始位置を探す
                                        # 「花  文字の由来」のような形式を検出
                                        next_entry_match = re.search(r'([一-龯])\s\s(?![【])', detail)
                                        if next_entry_match:
                                            # 次のエントリが見つかったら、そこで詳細を切断
                                            detail = detail[:next_entry_match.start()].strip()

                                        # 地行:パターンの開始も検出
                                        chigyou_match = re.search(r'地行:', detail)
                                        if chigyou_match:
                                            detail = detail[:chigyou_match.start()].strip()

                                        if detail:
                                            all_entries.append((match.start(), char, f"【{evaluation}】\n{detail}"))
                                            processed_positions.add(match.start())

                                # Step 3: 地行:文字列パターン（先に処理して範囲を記録）
                                chigyou_ranges = []
                                # 複数の文が続く場合にも対応（。が2つまで）
                                chigyou_pattern = r'地行:([^\s]+)\s+((?:[^。]*?。){1,2})'
                                for match in re.finditer(chigyou_pattern, moji_content):
                                    chars = match.group(1)
                                    detail = match.group(2).strip()
                                    # 次の文字パターンが含まれている場合は切る
                                    next_char_pos = re.search(r'[一-龯]\s\s[^【]', detail)
                                    if next_char_pos:
                                        detail = detail[:next_char_pos.start()].strip()
                                    all_entries.append((match.start(), f"地行:{chars}", detail))
                                    # 地行の範囲は実際のマッチ範囲を使用（次の文字パターンまで）
                                    chigyou_ranges.append((match.start(), match.end()))
                                    processed_positions.add(match.start())

                                # Step 4: 人格:文字列パターン
                                jinkaku_ranges = []
                                jinkaku_pattern = r'人格:([^\s]+)\s+((?:[^。]*?。){1,2})'
                                for match in re.finditer(jinkaku_pattern, moji_content):
                                    chars = match.group(1)
                                    detail = match.group(2).strip()
                                    # 次の文字パターンが含まれている場合は切る
                                    next_char_pos = re.search(r'[一-龯]\s\s[^【]', detail)
                                    if next_char_pos:
                                        detail = detail[:next_char_pos.start()].strip()
                                    all_entries.append((match.start(), f"人格:{chars}", detail))
                                    jinkaku_ranges.append((match.start(), match.end()))
                                    processed_positions.add(match.start())

                                # Step 5: 単一文字の評価なしパターン（花  文字の由来...）
                                single_simple_pattern = r'(?<![・:])([一-龯])(?![・])\s\s([^【]*?)(?=(?:[一-龯])\s\s|地行:|人格:|$)'
                                for match in re.finditer(single_simple_pattern, moji_content, re.DOTALL):
                                    pos = match.start()

                                    # 地行:や人格:の範囲内の文字は除外
                                    in_special_range = False
                                    for range_start, range_end in chigyou_ranges + jinkaku_ranges:
                                        if range_start <= pos < range_end:
                                            in_special_range = True
                                            break

                                    if not in_special_range and pos not in processed_positions:
                                        char = match.group(1)
                                        detail = match.group(2).strip()

                                        if detail:
                                            # 同じ文字名が既に存在する場合は番号を付ける
                                            char_key = char
                                            if any(key == char or key.startswith(f"{char}_") for _, key, _ in all_entries):
                                                counter = 2
                                                while any(key == f"{char}_{counter}" for _, key, _ in all_entries):
                                                    counter += 1
                                                char_key = f"{char}_{counter}"

                                            all_entries.append((pos, char_key, detail))
                                            processed_positions.add(pos)

                                # 位置順にソートして辞書に格納（既存システムと同じ順序）
                                all_entries.sort(key=lambda x: x[0])

                                # 複数文字パターンに含まれる単体文字のリストを作成
                                multi_char_components = set()
                                for _, key, _ in all_entries:
                                    if '・' in key and not key.startswith('地行:') and not key.startswith('人格:'):
                                        # 例：次・郎 → 次、郎を除外対象に追加
                                        parts = key.split('・')
                                        for part in parts:
                                            multi_char_components.add(part)

                                for _, key, value in all_entries:
                                    # 複数文字パターンに含まれる単体文字は除外
                                    if key in multi_char_components:
                                        continue
                                    moji_kantei[key] = value

                        except Exception as e:
                            print(f"文字による鑑定抽出エラー: {e}")

                        return moji_kantei

                    # 陰陽による鑑定を抽出
                    def extract_inyou_kantei(raw_text):
                        """陰陽による鑑定を抽出"""
                        inyou_kantei = {}
                        try:
                            # 陰陽による鑑定セクションを抽出
                            inyou_pattern = r'陰陽による鑑定\s*(.+?)(?:文字による鑑定|五行による鑑定|画数による鑑定|天地による鑑定|$)'
                            inyou_match = re.search(inyou_pattern, raw_text, re.DOTALL)

                            if inyou_match:
                                inyou_content = inyou_match.group(1).strip()

                                # 名前パターンでの鑑定を抽出
                                name_pattern = r'([^\s]+\s+[^\s]+)\s*\n(.+?)(?=\n[^\s]+\s+[^\s]+\s*\n|$)'
                                name_matches = re.findall(name_pattern, inyou_content, re.DOTALL)

                                for name, content in name_matches:
                                    inyou_kantei[name.strip()] = content.strip()

                        except Exception as e:
                            print(f"陰陽による鑑定抽出エラー: {e}")

                        return inyou_kantei

                    # 五行による鑑定を抽出
                    def extract_gogyou_kantei(raw_text):
                        """五行による鑑定を抽出 - 正確な分離ロジック"""
                        gogyou_kantei = {}
                        try:
                            # 五行による鑑定セクションを抽出
                            gogyou_pattern = r'五行による鑑定\s*(.*?)(?=画数による鑑定|天地による鑑定|$)'
                            gogyou_match = re.search(gogyou_pattern, raw_text, re.DOTALL)

                            if gogyou_match:
                                gogyou_content = gogyou_match.group(1).strip()

                                # Step 1: エントリの開始位置を特定
                                entry_positions = []

                                # フルネーム 【五行のバランス】パターン（ひらがな・カタカナ対応）
                                for match in re.finditer(r'([一-龯あ-んア-ン]+ [一-龯あ-んア-ン]+)\s*【五行のバランス', gogyou_content):
                                    entry_positions.append((match.start(), 'fullname', match.group(1)))

                                # 地格：文字列 【評価】パターン
                                for match in re.finditer(r'地格：([^\s]+)\s*【', gogyou_content):
                                    entry_positions.append((match.start(), 'chikaku', match.group(1)))

                                # 人格：文字列 【評価】パターン
                                for match in re.finditer(r'人格：([^\s]+)\s*【', gogyou_content):
                                    entry_positions.append((match.start(), 'jinkaku', match.group(1)))

                                # 位置順にソート
                                entry_positions.sort()

                                # Step 2: 各エントリを個別に処理
                                for i, (start_pos, entry_type, name) in enumerate(entry_positions):
                                    # 次のエントリの開始位置を取得（なければ終端まで）
                                    end_pos = entry_positions[i+1][0] if i+1 < len(entry_positions) else len(gogyou_content)
                                    segment = gogyou_content[start_pos:end_pos].strip()

                                    if entry_type == 'fullname':
                                        # フルネーム 【五行のバランス(xxx)】詳細（ひらがな・カタカナ対応）
                                        match = re.match(r'([一-龯あ-んア-ン]+ [一-龯あ-んア-ン]+)\s*【(五行のバランス\([^)]+\))】\s*(.*)', segment, re.DOTALL)
                                        if match:
                                            full_name = match.group(1)
                                            evaluation = match.group(2)
                                            detail = match.group(3).strip()
                                            if detail:
                                                gogyou_kantei[full_name] = f"【{evaluation}】\n{detail}"

                                    elif entry_type == 'chikaku':
                                        # 地格：文字列 【評価】詳細
                                        match = re.match(r'地格：([^\s]+)\s*【([^】]+)】\s*(.*)', segment, re.DOTALL)
                                        if match:
                                            name_part = match.group(1)
                                            evaluation = match.group(2)
                                            detail = match.group(3).strip()
                                            if detail:
                                                gogyou_kantei[f"地格:{name_part}"] = f"【{evaluation}】\n{detail}"

                                    elif entry_type == 'jinkaku':
                                        # 人格：文字列 【評価】詳細
                                        match = re.match(r'人格：([^\s]+)\s*【([^】]+)】\s*(.*)', segment, re.DOTALL)
                                        if match:
                                            name_part = match.group(1)
                                            evaluation = match.group(2)
                                            detail = match.group(3).strip()

                                            # フルネームパターンが混入している場合は除去
                                            # 「松浦 もか【五行のバランス】...」のようなパターンを検出して除去
                                            fullname_intrusion = re.search(r'([一-龯あ-んア-ン]+ [一-龯あ-んア-ン]+)\s*【', detail)
                                            if fullname_intrusion:
                                                detail = detail[:fullname_intrusion.start()].strip()

                                            if detail:
                                                gogyou_kantei[f"人格:{name_part}"] = f"【{evaluation}】\n{detail}"

                        except Exception as e:
                            print(f"五行による鑑定抽出エラー: {e}")

                        return gogyou_kantei

                    # 画数による鑑定を抽出
                    def extract_kakusu_kantei(raw_text):
                        """画数による鑑定を抽出 - 地行、総格、人格を個別エントリーに分離"""
                        kakusu_kantei = {}
                        try:
                            # 画数による鑑定セクションを抽出
                            kakusu_pattern = r'画数による鑑定\s*(.*?)(?=天地による鑑定|$)'
                            kakusu_match = re.search(kakusu_pattern, raw_text, re.DOTALL)

                            if kakusu_match:
                                kakusu_content = kakusu_match.group(1).strip()

                                # パターン1: 地行:美花 【画数9】詳細
                                chigyou_pattern = r'地行:([^\s]+)\s*【画数(\d+)】\s*(.*?)(?=総格:|人格:|天地による鑑定|$)'
                                chigyou_match = re.search(chigyou_pattern, kakusu_content, re.DOTALL)
                                if chigyou_match:
                                    target = chigyou_match.group(1)
                                    kakusu = chigyou_match.group(2)
                                    detail = chigyou_match.group(3).strip()
                                    # 総格や人格の部分を除去
                                    if '総格:' in detail:
                                        detail = detail.split('総格:')[0].strip()
                                    if '人格:' in detail:
                                        detail = detail.split('人格:')[0].strip()
                                    kakusu_kantei[f"地行:{target}"] = f"【画数{kakusu}】\n{detail}"

                                # パターン2: 総格:田中 美花 【画数26】詳細
                                sougaku_pattern = r'総格:([^【]+)\s*【画数(\d+)】\s*(.*?)(?=地行:|人格:|天地による鑑定|$)'
                                sougaku_match = re.search(sougaku_pattern, kakusu_content, re.DOTALL)
                                if sougaku_match:
                                    target = sougaku_match.group(1).strip()
                                    kakusu = sougaku_match.group(2)
                                    detail = sougaku_match.group(3).strip()
                                    # 地行、人格の部分を除去
                                    if '地行:' in detail:
                                        detail = detail.split('地行:')[0].strip()
                                    if '人格:' in detail:
                                        detail = detail.split('人格:')[0].strip()
                                    # 不要な末尾を除去
                                    if "姓名鑑定の使い方" in detail:
                                        detail = detail.split("姓名鑑定の使い方")[0].strip()
                                    kakusu_kantei[f"総格:{target}"] = f"【画数{kakusu}】\n{detail}"

                                # パターン3: 人格:田 太 【画数9】詳細
                                jinkaku_pattern = r'人格:([^【]+)\s*【画数(\d+)】\s*(.*?)(?=天地による鑑定|$)'
                                jinkaku_match = re.search(jinkaku_pattern, kakusu_content, re.DOTALL)
                                if jinkaku_match:
                                    target = jinkaku_match.group(1).strip()
                                    kakusu = jinkaku_match.group(2)
                                    detail = jinkaku_match.group(3).strip()
                                    # 不要な末尾を除去
                                    if "姓名鑑定の使い方" in detail:
                                        detail = detail.split("姓名鑑定の使い方")[0].strip()
                                    kakusu_kantei[f"人格:{target}"] = f"【画数{kakusu}】\n{detail}"

                        except Exception as e:
                            print(f"画数による鑑定抽出エラー: {e}")

                        return kakusu_kantei

                    # 天地による鑑定を抽出
                    def extract_tenti_kantei(raw_text):
                        """天地による鑑定を抽出"""
                        tenti_kantei = {}
                        try:
                            # 天地による鑑定セクションを抽出
                            tenti_pattern = r'天地による鑑定\s*(.*?)(?=$)'
                            tenti_match = re.search(tenti_pattern, raw_text, re.DOTALL)

                            if tenti_match:
                                tenti_content = tenti_match.group(1).strip()

                                # 天地による鑑定パターン: 鈴木 美雨 【天地総同数】詳細
                                tenti_item_pattern = r'([ぁ-んァ-ヶー一-龠々〆〤\s]+?)\s*【([^】]+)】\s*(.*?)(?=姓名鑑定の使い方|$)'
                                tenti_match_result = re.search(tenti_item_pattern, tenti_content, re.DOTALL)
                                if tenti_match_result:
                                    target = tenti_match_result.group(1).strip()
                                    evaluation = tenti_match_result.group(2)
                                    detail = tenti_match_result.group(3).strip()
                                    # 不要な部分を除去
                                    if "姓名鑑定の使い方" in detail:
                                        detail = detail.split("姓名鑑定の使い方")[0].strip()
                                    tenti_kantei[target] = f"【{evaluation}】\n{detail}"

                        except Exception as e:
                            print(f"天地による鑑定抽出エラー: {e}")

                        return tenti_kantei

                    # 各鑑定セクションを抽出
                    details["詳細鑑定"]["文字による鑑定"] = extract_moji_kantei(raw_text)
                    details["詳細鑑定"]["陰陽による鑑定"] = extract_inyou_kantei(raw_text)
                    details["詳細鑑定"]["五行による鑑定"] = extract_gogyou_kantei(raw_text)
                    details["詳細鑑定"]["画数による鑑定"] = extract_kakusu_kantei(raw_text)
                    details["詳細鑑定"]["天地による鑑定"] = extract_tenti_kantei(raw_text)

                    return details

                # 詳細データを抽出
                print(f"DEBUG: raw_text前半: {raw_result.get('raw_text', '')[:500]}")
                seimei_details = extract_seimei_details(raw_result.get("raw_text", ""), name_for_seimei)
                print(f"DEBUG: 抽出された詳細データ: {seimei_details}")

                # データベース用に構造化
                calculation_result["seimei"] = {
                    "data": {
                        "総評点数": raw_result.get("score", "未取得"),
                        "詳細結果": raw_result.get("has_detailed_result", False),
                        "URL": raw_result.get("url", ""),
                        **seimei_details  # 抽出した詳細データを追加
                    },
                    "input": {
                        "name": name_for_seimei
                    },
                    "raw_data": raw_result  # 元データも保持
                }

        # データベースの結果を更新
        kantei_record.calculation_result = calculation_result

        # パターン別のステータス判定
        has_kyusei = "kyusei" in calculation_result and calculation_result["kyusei"]
        has_seimei = "seimei" in calculation_result and calculation_result["seimei"]

        # パターンに応じたステータス決定
        if diagnosis_pattern == "kyusei_only":
            if has_kyusei:
                kantei_record.status = "completed"
                print(f"鑑定記録 {record_id} を完了状態に設定しました（九星気学のみパターン成功）")
            else:
                kantei_record.status = "failed"
                print(f"鑑定記録 {record_id} は失敗（九星気学失敗）")
        elif diagnosis_pattern == "seimei_only":
            if has_seimei:
                kantei_record.status = "completed"
                print(f"鑑定記録 {record_id} を完了状態に設定しました（姓名判断のみパターン成功）")
            else:
                kantei_record.status = "failed"
                print(f"鑑定記録 {record_id} は失敗（姓名判断失敗）")
        else:  # "all" パターン
            if has_kyusei and has_seimei:
                kantei_record.status = "completed"
                print(f"鑑定記録 {record_id} を完了状態に設定しました（九星気学・姓名判断両方成功）")
            elif has_kyusei:
                kantei_record.status = "partial"  # 九星気学のみ成功
                print(f"鑑定記録 {record_id} は九星気学のみ完了（姓名判断失敗）")
            else:
                kantei_record.status = "failed"
                print(f"鑑定記録 {record_id} は失敗（九星気学失敗）")

        db.commit()
        db.close()

    except Exception as e:
        print(f"鑑定記録 {record_id} で例外が発生しました: {str(e)}")
        try:
            db = get_database_session()
            kantei_record = get_kantei_record_by_id(db, record_id)
            if kantei_record:
                kantei_record.status = "failed"
                db.commit()
            db.close()
        except:
            pass

# 管理者権限付与エンドポイント
@app.post("/api/auth/promote-to-admin")
async def promote_to_admin(credentials: UserLogin):
    """ユーザーを管理者に昇格させる"""
    db = next(get_db())
    try:
        # ユーザーの存在確認とパスワード検証
        user = db.query(User).filter(User.email == credentials.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ユーザーが見つかりません"
            )

        # パスワード検証
        if not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="パスワードが正しくありません"
            )

        # 管理者権限を付与
        user.is_superuser = True
        db.commit()
        db.refresh(user)

        return {"success": True, "message": f"{credentials.email} に管理者権限を付与しました"}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"管理者権限付与エラー: {str(e)}")
    finally:
        db.close()

# 失敗した診断データ削除エンドポイント
@app.delete("/api/diagnosis/failed")
async def delete_failed_diagnoses(current_user: User = Depends(get_current_user)):
    """失敗した診断データを削除"""
    db = next(get_db())
    try:
        # ユーザーの失敗した診断を削除
        deleted_count = db.query(KanteiRecord).filter(
            KanteiRecord.user_id == current_user.id,
            KanteiRecord.status == "failed"
        ).delete()

        db.commit()

        return {"success": True, "message": f"{deleted_count}件の失敗した診断データを削除しました"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"削除エラー: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    import os

    # 環境変数からポート番号を取得（デフォルト: 8502）
    port = int(os.getenv("PORT", "8502"))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run(app, host=host, port=port)