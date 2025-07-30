"""
Authentication routes for the AI mentorship backend.
This module provides API endpoints for user authentication using Supabase.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from app.models import UserSignUp, UserSignIn, AuthResponse, UserResponse, ErrorResponse
from app.supabase import create_user, sign_in_user, sign_out_user, get_user_by_token
from app.auth.dependencies import get_current_user
from typing import Dict, Any
from datetime import datetime

# Create router for auth endpoints
router = APIRouter(prefix="/auth", tags=["authentication"])

def convert_datetime_to_string(dt_value):
    """Convert datetime object to ISO string format"""
    if isinstance(dt_value, datetime):
        return dt_value.isoformat()
    return dt_value

@router.post("/signup", response_model=AuthResponse)
async def signup(user_data: UserSignUp):
    """
    Register a new user account.
    
    Args:
        user_data: User registration data (email and password)
        
    Returns:
        AuthResponse: User data and authentication tokens
        
    Raises:
        HTTPException: If registration fails
    """
    try:
        # Create user in Supabase
        response = await create_user(user_data.email, user_data.password)
        
        # Extract user and session data
        user = response.get("user", {})
        session = response.get("session", {})
        
        # Check if user was created successfully
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user account"
            )
        
        # If no session is returned, it might be because email confirmation is required
        if not session:
            return AuthResponse(
                user=UserResponse(
                    id=user.get("id"),
                    email=user.get("email"),
                    created_at=convert_datetime_to_string(user.get("created_at")),
                    updated_at=convert_datetime_to_string(user.get("updated_at"))
                ),
                access_token="",  # No token until email is confirmed
                refresh_token=None,
                expires_in=None
            )
        
        # Format response with session data
        return AuthResponse(
            user=UserResponse(
                id=user.get("id"),
                email=user.get("email"),
                created_at=convert_datetime_to_string(user.get("created_at")),
                updated_at=convert_datetime_to_string(user.get("updated_at"))
            ),
            access_token=session.get("access_token"),
            refresh_token=session.get("refresh_token"),
            expires_in=session.get("expires_in")
        )
        
    except Exception as e:
        # Handle specific Supabase errors
        error_message = str(e)
        if "already registered" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        elif "password" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 6 characters long"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Registration failed: {error_message}"
            )

@router.post("/signin", response_model=AuthResponse)
async def signin(user_data: UserSignIn):
    """
    Sign in an existing user.
    
    Args:
        user_data: User login data (email and password)
        
    Returns:
        AuthResponse: User data and authentication tokens
        
    Raises:
        HTTPException: If login fails
    """
    try:
        # Sign in user with Supabase
        response = await sign_in_user(user_data.email, user_data.password)
        
        # Extract user and session data
        user = response.get("user", {})
        session = response.get("session", {})
        
        if not user or not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Format response
        return AuthResponse(
            user=UserResponse(
                id=user.get("id"),
                email=user.get("email"),
                created_at=convert_datetime_to_string(user.get("created_at")),
                updated_at=convert_datetime_to_string(user.get("updated_at"))
            ),
            access_token=session.get("access_token"),
            refresh_token=session.get("refresh_token"),
            expires_in=session.get("expires_in")
        )
        
    except Exception as e:
        # Handle authentication errors
        error_message = str(e)
        if "invalid" in error_message.lower() or "credentials" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Sign in failed: {error_message}"
            )

@router.post("/signout")
async def signout(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Sign out the current user.
    
    Args:
        user: Current authenticated user data
        
    Returns:
        dict: Success message
        
    Raises:
        HTTPException: If user is not authenticated
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        # Note: For proper signout, we need the user's token
        # This endpoint will be called with the Bearer token in the header
        # The actual signout will be handled by the frontend clearing the token
        return {"message": "Successfully signed out"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sign out failed: {str(e)}"
        )

@router.post("/callback")
async def auth_callback_post(data: dict):
    """
    Handle authentication callbacks from the frontend (email confirmation, etc.)
    
    Args:
        data: Dictionary containing access_token, refresh_token, etc.
        
    Returns:
        dict: Success message with token information
    """
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No access token provided"
        )
    
    return {
        "message": "Email confirmed successfully!",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "note": "You can now use the access_token to authenticate with the API"
    }

@router.get("/callback")
async def auth_callback(access_token: str = None, refresh_token: str = None, error: str = None):
    """
    Handle authentication callbacks from Supabase (email confirmation, etc.)
    
    Args:
        access_token: JWT access token from Supabase
        refresh_token: Refresh token from Supabase
        error: Error message if authentication failed
        
    Returns:
        dict: Success or error message
    """
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Authentication error: {error}"
        )
    
    if access_token:
        return {
            "message": "Email confirmed successfully!",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "note": "You can now use the access_token to authenticate with the API"
        }
    
    return {
        "message": "Authentication callback received",
        "note": "Check the URL parameters for access_token and refresh_token"
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Get current user information.
    
    Args:
        user: Current authenticated user data
        
    Returns:
        UserResponse: Current user data
        
    Raises:
        HTTPException: If user is not authenticated
    """
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    return UserResponse(
        id=user.get("id"),
        email=user.get("email"),
        created_at=convert_datetime_to_string(user.get("created_at")),
        updated_at=convert_datetime_to_string(user.get("updated_at"))
    )