"""
Supabase configuration and client setup for the AI mentorship backend.
This module handles Supabase client initialization and provides authentication utilities.
"""

import os
from typing import Optional, Dict, Any
from supabase import create_client, Client
from dotenv import load_dotenv
import jwt
from jwt.exceptions import InvalidTokenError

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
# --- NEW: Load the JWT Secret ---
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

# Validate required environment variables
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable is required")
if not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_ANON_KEY environment variable is required")
# --- NEW: Validate the JWT Secret ---
if not SUPABASE_JWT_SECRET:
    raise ValueError("SUPABASE_JWT_SECRET environment variable is required for token verification")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_supabase_client() -> Client:
    """
    Get the Supabase client instance.
    """
    return supabase

async def get_user_by_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Get user information from a JWT by securely verifying it with the project's JWT secret.
    """
    try:
        # --- CORRECTED LOGIC ---
        # Decode the JWT and verify its signature using the secret key.
        # The 'audience' must be 'authenticated' for Supabase tokens.
        decoded = jwt.decode(
            token, 
            SUPABASE_JWT_SECRET, 
            algorithms=["HS256"], 
            audience="authenticated"
        )
        
        user_id = decoded.get('sub')
        email = decoded.get('email')
        
        if user_id and email:
            return {
                "id": user_id,
                "email": email,
                "aud": decoded.get('aud'),
                "role": decoded.get('role'),
                "app_metadata": decoded.get('app_metadata', {}),
                "user_metadata": decoded.get('user_metadata', {})
            }
        return None
        
    except InvalidTokenError as e:
        # This will catch expired tokens, invalid signatures, etc.
        print(f"JWT Verification Error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during token verification: {e}")
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