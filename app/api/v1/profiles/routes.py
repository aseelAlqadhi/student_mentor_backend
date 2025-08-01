"""
Profile API endpoints.
This module handles profile-related operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.models import UserProfile
from app.features.profiles.services import get_user_profile
from app.api.v1.auth.dependencies import require_authentication
from typing import Dict, Any

# Create router for profile endpoints
router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(user: Dict[str, Any] = Depends(require_authentication)):
    """
    Get the current user's profile.
    
    Args:
        user: Current authenticated user data
        
    Returns:
        UserProfile: The user's profile data
    """
    try:
        user_id = user.get("id")
        profile = await get_user_profile(user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving profile: {str(e)}"
        ) 