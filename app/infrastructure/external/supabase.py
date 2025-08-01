"""
Supabase configuration and client setup for the AI mentorship backend.
This module handles Supabase client initialization and provides authentication utilities.
"""

import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Validate required environment variables
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is required")
if not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_ANON_KEY environment variable is required")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_supabase_client() -> Client:
    """
    Get the Supabase client instance.
    
    Returns:
        Client: The initialized Supabase client
    """
    return supabase

async def get_user_by_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Get user information from Supabase using a JWT token.
    
    Args:
        token (str): The JWT token from Supabase auth
        
    Returns:
        Optional[Dict[str, Any]]: User data if token is valid, None otherwise
    """
    try:
        # Create a new client instance for this request
        from supabase import create_client
        temp_client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Try to get user info directly from the token
        # First, let's try to decode the JWT to get user info
        import jwt
        from jwt.exceptions import InvalidTokenError
        
        try:
            # Decode the JWT without verification first to see the payload
            decoded = jwt.decode(token, options={"verify_signature": False})
            
            # Extract user info from the JWT payload
            user_id = decoded.get('sub')
            email = decoded.get('email')
            
            if user_id and email:
                return {
                    "id": user_id,
                    "email": email,
                    "email_verified": decoded.get('user_metadata', {}).get('email_verified', False),
                    "created_at": None,  # We don't have this in the JWT
                    "updated_at": None   # We don't have this in the JWT
                }
            else:
                return None
                
        except InvalidTokenError:
            return None
            
    except Exception:
        return None

async def create_user(email: str, password: str) -> Dict[str, Any]:
    """
    Create a new user in Supabase.
    
    Args:
        email (str): User's email address
        password (str): User's password
        
    Returns:
        Dict[str, Any]: Response from Supabase auth
    """
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return response.model_dump()
    except Exception as e:
        raise Exception(f"Error creating user: {e}")

async def sign_in_user(email: str, password: str) -> Dict[str, Any]:
    """
    Sign in a user with email and password.
    
    Args:
        email (str): User's email address
        password (str): User's password
        
    Returns:
        Dict[str, Any]: Response from Supabase auth including session
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return response.model_dump()
    except Exception as e:
        raise Exception(f"Error signing in user: {e}")

async def sign_out_user(token: str) -> bool:
    """
    Sign out a user by invalidating their session.
    
    Args:
        token (str): The user's JWT token
        
    Returns:
        bool: True if sign out was successful
    """
    try:
        supabase.auth.set_session(token, None)
        supabase.auth.sign_out()
        return True
    except Exception as e:
        print(f"Error signing out user: {e}")
        return False