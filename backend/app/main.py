"""
FastAPI main application

Phase S-1a: Authentication service layer implementation
- JWT authentication, password hashing, session management
- SQLAlchemy 2.0 compliant
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/Users/lennon/projects/inoue4/sindankantei/.env.local')

# Import API routers
from .api.api import api_router
from .database import test_connection

# Create FastAPI application
app = FastAPI(
    title=os.getenv("PROJECT_NAME", "kantei-system-v2"),
    description="Integrated divination system for Nine Star Ki, name analysis, and auspicious directions",
    version="2.0.0",
    debug=os.getenv("DEBUG", "False").lower() == "true"
)

# CORS configuration
origins = os.getenv("CORS_ORIGINS", "").split(",")
# Development CORS configuration
if os.getenv("DEBUG", "False").lower() == "true":
    origins.extend(["http://localhost:3000", "http://127.0.0.1:3000"])

if origins and any(origin.strip() for origin in origins):  # Only add if not empty
    valid_origins = [origin.strip() for origin in origins if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=valid_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    print(f"🌐 CORS enabled for origins: {valid_origins}")
else:
    # Fallback for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    print("🌐 CORS enabled for development origins")

# Include API router
api_v1_str = os.getenv("API_V1_STR", "/api/v1")
app.include_router(api_router, prefix=api_v1_str)


@app.on_event("startup")
async def startup_event():
    """Application startup event handler"""
    print("🚀 FastAPI application starting...")

    # Test database connection
    if test_connection():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")

    print(f"🌐 API endpoints: {api_v1_str}")
    print("📋 Available endpoints:")
    print(f"  - POST {api_v1_str}/auth/login")
    print(f"  - GET  {api_v1_str}/auth/verify")
    print(f"  - POST {api_v1_str}/auth/logout")


@app.get("/")
async def root():
    """Root endpoint - application information"""
    return {
        "message": "kantei-system-v2 API",
        "version": "2.0.0",
        "status": "running",
        "phase": "S-1a: Authentication service layer implementation",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "auth": f"{api_v1_str}/auth/"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = test_connection()
    return {
        "status": "healthy" if db_status else "unhealthy",
        "database": "connected" if db_status else "disconnected",
        "phase": "S-1a: Authentication service layer implementation"
    }