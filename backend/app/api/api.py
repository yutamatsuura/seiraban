"""
API router integration

Phase S-1a: Authentication service layer implementation
Integration of all API endpoint routing
"""

from fastapi import APIRouter

from .endpoints import auth, kantei, admin

# Main API router
api_router = APIRouter()

# Include authentication endpoint for Phase S-1a
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include admin endpoints for management
api_router.include_router(admin.router, prefix="/admin", tags=["管理者機能"])

# Include kantei endpoints for Phase S-2a
api_router.include_router(kantei.router, prefix="/kantei", tags=["鑑定計算API群"])

