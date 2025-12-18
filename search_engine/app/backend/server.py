# app/backend/server.py
"""
FastAPI server for the search engine.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .api import router
from .loader import search_engine

# Create FastAPI app
app = FastAPI(
    title="AIT Search Engine API",
    description="Fast and intelligent search engine with semantic capabilities",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api", tags=["search"])


@app.on_event("startup")
async def startup_event():
    """Initialize search engine on startup"""
    print("=" * 60)
    print("Starting AIT Search Engine API Server")
    print("=" * 60)
    # The search_engine singleton is already initialized via loader import
    print("Server is ready to accept requests!")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\nShutting down AIT Search Engine API Server...")


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (disable in production)
        log_level="info"
    )
