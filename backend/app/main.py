import strawberry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter


# GraphQL スキーマ（後で実装）
@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "Hello from Kodomo Wallet API!"


schema = strawberry.Schema(query=Query)
graphql_app = GraphQLRouter(schema)

# FastAPI アプリケーション
app = FastAPI(
    title="Kodomo Wallet API",
    description="親子で使えるお小遣い管理アプリの GraphQL API",
    version="0.1.0",
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js の開発サーバー
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL エンドポイント
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    return {"message": "Kodomo Wallet API", "graphql": "/graphql", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
