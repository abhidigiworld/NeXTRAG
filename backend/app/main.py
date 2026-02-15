"""
SmartRAG AI - FastAPI Application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn

from app.config import settings
from app.api.routes import router
from app.utils.logger import logger
from app.services.vector_store import vector_store

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="SmartRAG AI",
    description="Retrieval-Augmented Generation AI Assistant with Dynamic Data Source Selection",
    version="1.0.0"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url, 
        "https://69917a62be9967b01572d83f--smartrag.netlify.app",
        "https://smartrag.netlify.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Starting SmartRAG AI application")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Embedding Provider: {settings.embedding_provider}")
    logger.info(f"Search Provider: {settings.search_provider}")
    
    # Validate API keys
    try:
        settings.validate_api_keys()
        logger.info("API key validation passed")
    except ValueError as e:
        logger.warning(f"API key validation warning: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down SmartRAG AI application")
    
    # Cleanup expired sessions
    cleaned = vector_store.cleanup_expired_sessions()
    logger.info(f"Cleaned up {cleaned} expired sessions")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "code": "INTERNAL_ERROR"
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SmartRAG AI API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
