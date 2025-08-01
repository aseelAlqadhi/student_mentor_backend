"""
API Layer - Main router for all API endpoints
"""

from fastapi import APIRouter
from app.api.v1 import router as v1_router

# Create main API router
api_router = APIRouter()

# Include v1 API routes
api_router.include_router(v1_router, prefix="/v1") 