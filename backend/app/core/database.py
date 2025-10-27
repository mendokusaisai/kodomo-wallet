"""
データベース設定と接続セットアップ
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import database_settings

# SQLAlchemyエンジンの作成
if not database_settings.database_url:
    raise ValueError("DATABASE_URL environment variable is not set")

engine = create_engine(
    database_settings.database_url,
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
