"""
Authentication dependencies for the AI mentorship backend.
This module provides dependency injection functions for user authentication using Supabase.
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.infrastructure.external.supabase import get_user_by_token

# HTTP Bearer token scheme for authentication
security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user from Supabase.
    
    Args:
        credentials: HTTP Bearer token credentials
        
    Returns:
        Optional[Dict[str, Any]]: User data if authenticated, None if not authenticated
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    if not credentials:
        return None
    
    try:
        # Extract token from Bearer header
        token = credentials.credentials
        
        # Get user from Supabase using the token
        user = await get_user_by_token(token)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle other exceptions
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_user_identifier(user: Optional[Dict[str, Any]] = Depends(get_current_user)) -> str:
    """
    Get a user identifier for rate limiting and tracking.
    This maintains compatibility with the existing chat endpoint.
    
    Args:
        user: Current authenticated user data
        
    Returns:
        str: User ID if authenticated, "global_unauthenticated_user" if not
    """
    if user is None:
        return "global_unauthenticated_user"
    
    # Return the user's UUID from Supabase
    return user.get("id", "unknown_user")

async def require_authentication(user: Optional[Dict[str, Any]] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency that requires authentication for protected endpoints.
    
    Args:
        user: Current authenticated user data
        
    Returns:
        Dict[str, Any]: User data
        
    Raises:
        HTTPException: If user is not authenticated
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user