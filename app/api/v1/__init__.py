"""
API v1 - Main router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.chat.routes import router as chat_router
from app.api.v1.onboarding.routes import router as onboarding_router
from app.api.v1.profiles.routes import router as profiles_router

# Create v1 router
router = APIRouter()

# Include feature routers
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(chat_router, prefix="/chat", tags=["Chat"])
router.include_router(onboarding_router, prefix="/onboarding", tags=["Onboarding"])
router.include_router(profiles_router, prefix="/profiles", tags=["Profiles"]) 