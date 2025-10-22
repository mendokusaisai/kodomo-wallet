"""
Kodomo Wallet API - FastAPI application with GraphQL.
"""

from app.api.graphql.schema import schema
from app.core.config import settings
from app.core.database import SessionLocal
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter


# Context getter for GraphQL
async def get_context():
    """Provide database session to GraphQL context"""
    db = SessionLocal()
    try:
        return {"db": db}
    finally:
        pass  # We'll close it in the finally block after the request


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
    allow_origins=settings.CORS_ORIGINS,
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
