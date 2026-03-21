"""
Kodomo Wallet API - FastAPIアプリケーション（GraphQL対応）
"""

import logging
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.api.graphql.schema import schema
from app.core.config import cors_settings
from app.core.context import GraphQLContext, verify_firebase_token

logger = logging.getLogger(__name__)


# GraphQLコンテキスト取得関数 - 依存性注入によりサービスを提供
async def get_context(request: Request) -> AsyncGenerator[dict[str, Any]]:
    """
    Authorizationヘッダーから Firebase ID トークンを検証し、
    サービスをGraphQLコンテキストに提供します。

    Yields:
        dict: current_uid と注入されたサービスを含むコンテキスト
    """
    async with GraphQLContext() as ctx:
        authorization: str = request.headers.get("authorization", "")
        if authorization.startswith("Bearer "):
            token = authorization.removeprefix("Bearer ")
            try:
                decoded = verify_firebase_token(token)
                ctx.current_uid = decoded.get("uid")
            except Exception:
                logger.warning("Firebase token verification failed")
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
