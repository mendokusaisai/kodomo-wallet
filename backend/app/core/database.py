"""
Database configuration and connection setup.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# .envファイルの読み込み
load_dotenv()

# データベースURL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# SQLAlchemyエンジンの作成
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 接続の健全性チェック
    pool_size=10,
    max_overflow=20,
)

# セッションファクトリー
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ベースクラス
Base = declarative_base()


def get_db():
    """
    データベースセッションを取得する依存性注入用関数
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
