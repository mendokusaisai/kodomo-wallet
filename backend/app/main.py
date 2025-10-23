"""
Kodomo Wallet API - FastAPI application with GraphQL.
"""

from collections.abc import AsyncGenerator
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

from app.api.graphql.schema import schema
from app.core.config import cors_settings
from app.core.context import GraphQLContext


# Context getter for GraphQL - provides services via dependency injection
async def get_context() -> AsyncGenerator[dict[str, Any]]:
    """
    Provide database session and services to GraphQL context.

    Uses GraphQLContext manager to ensure proper resource cleanup.
    The session will be automatically closed after the request completes.

    Yields:
        dict: Context containing database session and injected services
    """
    async with GraphQLContext() as ctx:
        yield ctx.to_dict()


# GraphQL Router with context
graphql_app = GraphQLRouter(schema, context_getter=get_context)

# FastAPI application
app = FastAPI(
    title="Kodomo Wallet API",
    description="親子で使えるお小遣い管理アプリの GraphQL API",
    version="0.1.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "Kodomo Wallet API",
        "version": "0.1.0",
        "endpoints": {"graphql": "/graphql", "docs": "/docs", "redoc": "/redoc"},
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
