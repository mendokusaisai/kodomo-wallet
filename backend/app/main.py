"""
Kodomo Wallet API - FastAPIアプリケーション（GraphQL対応）
"""

from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.api.graphql.schema import schema
from app.core.config import cors_settings
from app.core.context import GraphQLContext


# GraphQLコンテキスト取得関数 - 依存性注入によりサービスを提供
async def get_context() -> AsyncGenerator[dict[str, Any]]:
    """
    データベースセッションとサービスをGraphQLコンテキストに提供します。

    GraphQLContextマネージャーを使用してリソースのクリーンアップを保証します。
    セッションはリクエスト完了後に自動的にクローズされます。

    Yields:
        dict: データベースセッションと注入されたサービスを含むコンテキスト
    """
    async with GraphQLContext() as ctx:
        yield ctx.to_dict()


# GraphQLルーター（コンテキスト付き）
graphql_app = GraphQLRouter(schema, context_getter=get_context)

# FastAPIアプリケーション
app = FastAPI(
    title="Kodomo Wallet API",
    description="親子で使えるお小遣い管理アプリの GraphQL API",
    version="0.1.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQLエンドポイント
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    """ルートエンドポイント（API情報を返す）"""
    return {
        "message": "Kodomo Wallet API",
        "version": "0.1.0",
        "endpoints": {"graphql": "/graphql", "docs": "/docs", "redoc": "/redoc"},
    }


@app.get("/health")
def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
