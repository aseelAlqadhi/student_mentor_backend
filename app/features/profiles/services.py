"""
User profile management and onboarding functionality.
This module handles user profile creation, onboarding questionnaire processing,
and profile retrieval for AI context enhancement.
"""

import os
from typing import Optional, Dict, Any
from datetime import datetime
from app.shared.models import UserProfile, OnboardingRequest
from app.infrastructure.external.supabase import get_supabase_client

# Get Supabase client
supabase = get_supabase_client()

async def create_user_profile(user_id: str) -> UserProfile:
    """
    Create a new user profile in the database.
    
    Args:
        user_id (str): The user's unique identifier from Supabase auth
        
    Returns:
        UserProfile: The created user profile
    """
    try:
        # Create profile with default values
        profile_data = {
            "user_id": user_id,
            "onboarding_completed": False,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Insert into user_profiles table
        response = supabase.table("user_profiles").insert(profile_data).execute()
        
        if response.data:
            return UserProfile(**response.data[0])
        else:
            raise Exception("Failed to create user profile")
            
    except Exception as e:
        raise Exception(f"Error creating user profile: {e}")

async def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """
    Retrieve a user's profile from the database.
    
    Args:
        user_id (str): The user's unique identifier
        
    Returns:
        Optional[UserProfile]: User profile if found, None otherwise
    """
    try:
        # Query user_profiles table
        response = supabase.table("user_profiles").select("*").eq("user_id", user_id).execute()
        
        if response.data:
            profile = UserProfile(**response.data[0])
            return profile
        else:
            return None
            
    except Exception as e:
        print(f"Error retrieving user profile: {e}")
        return None

async def update_user_profile(user_id: str, onboarding_data: OnboardingRequest) -> UserProfile:
    """
    Update user profile with onboarding questionnaire responses.
    
    Args:
        user_id (str): The user's unique identifier
        onboarding_data (OnboardingRequest): The onboarding questionnaire responses
        
    Returns:
        UserProfile: The updated user profile
    """
    try:
        # Prepare update data
        update_data = {
            "challenges_goals": onboarding_data.challenges_goals,
            "living_situation": onboarding_data.living_situation,
            "guidance_preference": onboarding_data.guidance_preference,
            "onboarding_completed": True,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Update user_profiles table
        response = supabase.table("user_profiles").update(update_data).eq("user_id", user_id).execute()
        
        if response.data:
            return UserProfile(**response.data[0])
        else:
            raise Exception("Failed to update user profile")
            
    except Exception as e:
        raise Exception(f"Error updating user profile: {e}")

async def check_onboarding_status(user_id: str) -> Dict[str, Any]:
    """
    Check if a user has completed the onboarding process.
    
    Args:
        user_id (str): The user's unique identifier
        
    Returns:
        Dict[str, Any]: Dictionary with onboarding status and profile data
    """
    try:
        profile = await get_user_profile(user_id)
        
        if profile:
            return {
                "onboarding_completed": profile.onboarding_completed,
                "profile": profile
            }
        else:
            # Create profile if it doesn't exist
            profile = await create_user_profile(user_id)
            return {
                "onboarding_completed": False,
                "profile": profile
            }
            
    except Exception as e:
        print(f"Error checking onboarding status: {e}")
        return {
            "onboarding_completed": False,
            "profile": None
        }

async def get_user_context_for_ai(user_id: str) -> Optional[str]:
    """
    Get user profile context to enhance AI responses.
    
    Args:
        user_id (str): The user's unique identifier
        
    Returns:
        Optional[str]: Formatted context string for AI, None if no profile
    """
    try:
        profile = await get_user_profile(user_id)
        
        if not profile or not profile.onboarding_completed:
            return None
            
        # Format user context for AI
        context_parts = []
        
        if profile.challenges_goals:
            context_parts.append(f"Student's main challenges/goals: {profile.challenges_goals}")
            
        if profile.living_situation:
            context_parts.append(f"Living situation and support system: {profile.living_situation}")
            
        if profile.guidance_preference:
            context_parts.append(f"Preferred guidance style: {profile.guidance_preference}")
            
        if context_parts:
            return " | ".join(context_parts)
        else:
            return None
            
    except Exception as e:
        print(f"Error getting user context for AI: {e}")
        return None 