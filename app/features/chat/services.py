"""
Chat history management for multi-area conversations.
This module handles storing and retrieving chat history for different areas.
"""
import os
from typing import List, Optional
from datetime import datetime
from app.shared.models import ChatMessage
from supabase import create_client

# Create a privileged client that uses the service key
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set for the service client.")
supabase_service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


async def save_chat_message(user_id: str, area: str, message_type: str, content: str) -> str:
    """
    Save a chat message to the database.
    """
    try:
        message_data = {
            "user_id": user_id,
            "area": area.lower(),
            "message_type": message_type,
            "content": content,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Use the new service client for all database operations
        response = supabase_service_client.table("chat_history").insert(message_data).execute()
        
        if response.data:
            return response.data[0]["id"]
        else:
            raise Exception("Failed to save chat message")
            
    except Exception as e:
        raise Exception(f"Error saving chat message: {e}")

async def get_chat_history(user_id: str, area: str, limit: int = 50) -> List[ChatMessage]:
    """
    Retrieve chat history for a specific area.
    """
    try:
        response = supabase_service_client.table("chat_history")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("area", area.lower())\
            .order("created_at", desc=False)\
            .limit(limit)\
            .execute()
        
        if response.data:
            return [ChatMessage(**msg) for msg in response.data]
        else:
            return []
            
    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        return []

async def get_recent_context(user_id: str, area: str, message_count: int = 10) -> str:
    """
    Get recent conversation context for AI processing.
    """
    try:
        messages = await get_chat_history(user_id, area, message_count)
        
        if not messages:
            return ""
        
        context_parts = []
        for msg in messages:
            role = "User" if msg.message_type == "user" else "Assistant"
            context_parts.append(f"{role}: {msg.content}")
        
        return "\n".join(context_parts)
        
    except Exception as e:
        print(f"Error getting conversation context: {e}")
        return ""

async def clear_chat_history(user_id: str, area: str) -> bool:
    """
    Clear chat history for a specific area.
    """
    try:
        # Use the service client here as well
        response = supabase_service_client.table("chat_history")\
            .delete()\
            .eq("user_id", user_id)\
            .eq("area", area.lower())\
            .execute()
        
        return True
        
    except Exception as e:
        print(f"Error clearing chat history: {e}")
        return False

async def get_user_areas_with_history(user_id: str) -> List[str]:
    """
    Get list of areas where the user has chat history.
    """
    try:
        # Use the service client here as well
        response = supabase_service_client.table("chat_history")\
            .select("area")\
            .eq("user_id", user_id)\
            .execute()
        
        if response.data:
            areas = list(set([msg["area"] for msg in response.data]))
            return areas
        else:
            return []
            
    except Exception as e:
        print(f"Error getting user areas: {e}")
        return []

async def get_message_count_by_area(user_id: str) -> dict:
    """
    Get message count for each area.
    """
    try:
        # Use the service client here as well
        response = supabase_service_client.table("chat_history")\
            .select("area")\
            .eq("user_id", user_id)\
            .execute()
        
        if response.data:
            area_counts = {}
            for msg in response.data:
                area = msg["area"]
                area_counts[area] = area_counts.get(area, 0) + 1
            
            return area_counts
        else:
            return {}
            
    except Exception as e:
        print(f"Error getting message counts: {e}")
        return {}