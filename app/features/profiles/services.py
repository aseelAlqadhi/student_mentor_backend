"""
User profile management and onboarding functionality.
"""
import os
from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client
from app.shared.models import UserProfile, OnboardingRequest

# --- Create a privileged client using the Service Key ---
# This client will be used for ALL profile operations to bypass RLS.
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set for the service client.")
supabase_service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

async def create_user_profile(user_id: str) -> UserProfile:
    """
    Create a new user profile using the service role.
    """
    try:
        profile_data = { "user_id": user_id, "onboarding_completed": False }
        response = supabase_service_client.table("user_profiles").insert(profile_data).execute()
        
        if response.data:
            return UserProfile(**response.data[0])
        raise Exception("Failed to create user profile in database.")
    except Exception as e:
        raise Exception(f"Error creating user profile: {e}")

async def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """
    Retrieve a user's profile from the database using the service role.
    """
    try:
        response = supabase_service_client.table("user_profiles").select("*").eq("user_id", user_id).single().execute()
        
        if response.data:
            return UserProfile(**response.data)
        return None
    except Exception as e:
        print(f"Error retrieving user profile: {e}")
        return None

async def update_user_profile(user_id: str, onboarding_data: OnboardingRequest) -> UserProfile:
    """
    Update user profile with onboarding responses using the service role.
    """
    try:
        update_data = {
            "challenges_goals": onboarding_data.challenges_goals,
            "living_situation": onboarding_data.living_situation,
            "guidance_preference": onboarding_data.guidance_preference,
            "onboarding_completed": True,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        response = supabase_service_client.table("user_profiles").update(update_data).eq("user_id", user_id).execute()
        
        if response.data:
            return UserProfile(**response.data[0])
        raise Exception("Failed to update user profile")
    except Exception as e:
        raise Exception(f"Error updating user profile: {e}")

async def check_onboarding_status(user_id: str) -> Dict[str, Any]:
    """
    Check onboarding status. If a profile doesn't exist, create one.
    """
    try:
        profile = await get_user_profile(user_id)
        if profile:
            return {"onboarding_completed": profile.onboarding_completed, "profile": profile}
        
        new_profile = await create_user_profile(user_id)
        return {"onboarding_completed": False, "profile": new_profile}
    except Exception as e:
        print(f"Error in check_onboarding_status for user {user_id}: {e}")
        return {"onboarding_completed": False, "profile": None}

async def get_user_context_for_ai(user_id: str) -> Optional[str]:
    """
    Get user profile context to enhance AI responses.
    """
    profile = await get_user_profile(user_id)
    
    if not profile or not profile.onboarding_completed:
        return None
        
    context_parts = []
    if profile.challenges_goals:
        context_parts.append(f"Student's main challenges/goals: {profile.challenges_goals}")
    if profile.living_situation:
        context_parts.append(f"Living situation and support system: {profile.living_situation}")
    if profile.guidance_preference:
        context_parts.append(f"Preferred guidance style: {profile.guidance_preference}")
        
    return " | ".join(context_parts) if context_parts else None