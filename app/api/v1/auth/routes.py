"""
Authentication routes for the AI mentorship backend.
This module provides API endpoints for user authentication using Supabase.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.models import UserSignUp, UserSignIn, UserResponse, AuthResponse, TokenResponse, ErrorResponse, EnhancedUserResponse
from app.infrastructure.external.supabase import get_supabase_client
from app.api.v1.auth.dependencies import get_current_user, get_user_identifier, require_authentication
from app.api.v1.auth.throttling import (
    get_user_rate_limit_status, 
    get_all_rate_limit_status, 
    reset_user_rate_limit, 
    reset_all_rate_limits,
    update_rate_limit_config
)
# --- IMPORT THE PROFILE SERVICE ---
from app.features.profiles.services import get_user_profile, create_user_profile
from datetime import datetime
from app.features.profiles.services import create_user_profile
# Create router for auth endpoints
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Get Supabase client
supabase = get_supabase_client()

def convert_datetime_to_string(dt) -> Optional[str]:
    """Convert datetime object to ISO string format"""
    if dt is None:
        return None
    if isinstance(dt, str):
        return dt
    return dt.isoformat()

@router.post("/signup")
async def signup(user_data: UserSignUp):
    """
    Handles user registration by creating an auth user and their database profile.
    """
    try:
        # Step 1: Create the user in Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
        })

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration failed. This email may already be in use."
            )
        
        new_user = auth_response.user

        # Step 2: Create the corresponding user profile
        try:
            # CORRECTED: Call create_user_profile with only the user_id
            await create_user_profile(new_user.id)
        except Exception as profile_error:
            print(f"CRITICAL: Profile creation failed for user {new_user.id}: {profile_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not initialize user profile after registration."
            )

        # Step 3: Return a simple success message
        return {"message": "User registered successfully. Please check your email for confirmation."}
            
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during signup: {str(e)}"
        )

# --- The rest of your file (signin, me, etc.) remains the same ---
# ... (signin, signout, me, and rate-limit routes are unchanged) ...
@router.post("/signin", response_model=AuthResponse)
async def signin(user_data: UserSignIn):
    """
    Sign in an existing user with email and password.
    
    Args:
        user_data: User sign-in data (email, password)
        
    Returns:
        AuthResponse: Authentication response with user data and access token
    """
    try:
        # Sign in user
        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        if response.user and response.session:
            # Calculate expires_in from the session
            expires_in = None
            if hasattr(response.session, 'expires_at') and response.session.expires_at:
                import time
                current_time = int(time.time())
                expires_in = response.session.expires_at - current_time
            
            return AuthResponse(
                user=UserResponse(
                    id=response.user.id,
                    email=response.user.email,
                    created_at=response.user.created_at
                ),
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                expires_in=expires_in,
                message="Sign in successful"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Sign in failed: {str(e)}"
        )

@router.post("/signout")
async def signout(user: Dict[str, Any] = Depends(require_authentication)):
    """
    Sign out the current user.
    
    Args:
        user: Current authenticated user data
        
    Returns:
        dict: Sign out confirmation message
    """
    try:
        # Sign out user
        supabase.auth.sign_out()
        
        return {
            "message": "Sign out successful",
            "user_id": user.get("id")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sign out failed: {str(e)}"
        )

@router.get("/me", response_model=EnhancedUserResponse)
async def get_current_user_info(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get comprehensive information about the current user including profile data.
    
    Args:
        user: Current authenticated user data
        
    Returns:
        EnhancedUserResponse: User information with profile data
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        from app.features.profiles.services import get_user_profile
        user_id = user.get("id")
        profile = await get_user_profile(user_id)

        # Build enhanced response with profile data
        response_data = {
            "id": user.get("id"),
            "email": user.get("email"),
            "onboarding_completed": False,
            "challenges_goals": None,
            "living_situation": None,
            "guidance_preference": None,
            "profile_created_at": None,
            "profile_updated_at": None
        }
        
        # Add auth timestamps if they exist
        if user.get("created_at"):
            response_data["created_at"] = convert_datetime_to_string(user.get("created_at"))

        if profile:
            response_data.update({
                "onboarding_completed": profile.onboarding_completed,
                "challenges_goals": profile.challenges_goals,
                "living_situation": profile.living_situation,
                "guidance_preference": profile.guidance_preference,
                "profile_created_at": convert_datetime_to_string(profile.created_at),
                "profile_updated_at": convert_datetime_to_string(profile.updated_at)
            })
            
            # Use profile's updated_at as the main updated_at field if available
            if profile.updated_at:
                response_data["updated_at"] = convert_datetime_to_string(profile.updated_at)
            elif user.get("updated_at"):
                response_data["updated_at"] = convert_datetime_to_string(user.get("updated_at"))
        else:
            # If no profile, use auth user's updated_at if available
            if user.get("updated_at"):
                response_data["updated_at"] = convert_datetime_to_string(user.get("updated_at"))

        return EnhancedUserResponse(**response_data)

    except Exception as e:
        # If there's an error getting profile data, return basic user info
        return EnhancedUserResponse(
            id=user.get("id"),
            email=user.get("email"),
            onboarding_completed=False
        )

@router.get("/callback")
async def auth_callback():
    """
    Handle email confirmation redirects from Supabase.
    
    Returns:
        dict: Callback confirmation message
    """
    return {
        "message": "Email confirmation callback received",
        "status": "success"
    }

# --- Rate Limit Management Endpoints ---

@router.get("/rate-limit/status")
async def get_rate_limit_status(user: Dict[str, Any] = Depends(require_authentication)):
    """
    Get rate limit status for the current authenticated user.
    
    Args:
        user: Current authenticated user data
        
    Returns:
        dict: Rate limit status information
    """
    user_id = user.get("id")
    return get_user_rate_limit_status(user_id)

@router.get("/rate-limit/status/all")
async def get_all_users_rate_limit_status(user: Dict[str, Any] = Depends(require_authentication)):
    """
    Get rate limit status for all users (admin function).
    
    Args:
        user: Current authenticated user data
        
    Returns:
        dict: Rate limit status for all users
    """
    # In a real application, you might want to add admin role checking here
    return get_all_rate_limit_status()

@router.post("/rate-limit/reset/{user_id}")
async def reset_specific_user_rate_limit(
    user_id: str, 
    current_user: Dict[str, Any] = Depends(require_authentication)
):
    """
    Reset rate limit for a specific user (admin function).
    
    Args:
        user_id: ID of the user to reset rate limit for
        current_user: Current authenticated user data
        
    Returns:
        dict: Reset confirmation message
    """
    # In a real application, you might want to add admin role checking here
    return reset_user_rate_limit(user_id)

@router.post("/rate-limit/reset/all")
async def reset_all_users_rate_limits(current_user: Dict[str, Any] = Depends(require_authentication)):
    """
    Reset rate limits for all users (admin function).
    
    Args:
        current_user: Current authenticated user data
        
    Returns:
        dict: Reset confirmation message
    """
    # In a real application, you might want to add admin role checking here
    return reset_all_rate_limits()

@router.post("/rate-limit/config/update")
async def update_rate_limits_config(
    auth_limit: Optional[int] = None,
    auth_window: Optional[int] = None,
    global_limit: Optional[int] = None,
    global_window: Optional[int] = None,
    current_user: Dict[str, Any] = Depends(require_authentication)
):
    """
    Update rate limit configuration (admin function).
    
    Args:
        auth_limit: New limit for authenticated users
        auth_window: New time window for authenticated users
        global_limit: New limit for unauthenticated users
        global_window: New time window for unauthenticated users
        current_user: Current authenticated user data
        
    Returns:
        dict: Updated configuration
    """
    # In a real application, you might want to add admin role checking here
    return update_rate_limit_config(
        auth_limit=auth_limit,
        auth_window=auth_window,
        global_limit=global_limit,
        global_window=global_window
    )