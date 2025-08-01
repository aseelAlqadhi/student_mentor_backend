"""
Chat history management for multi-area conversations.
This module handles storing and retrieving chat history for different areas.
"""

from typing import List, Optional
from datetime import datetime
from app.shared.models import ChatMessage
from app.infrastructure.external.supabase import get_supabase_client

# Get Supabase client
supabase = get_supabase_client()

async def save_chat_message(user_id: str, area: str, message_type: str, content: str) -> str:
    """
    Save a chat message to the database.
    
    Args:
        user_id (str): The user's unique identifier
        area (str): The conversation area (health, career, finance, general)
        message_type (str): Type of message ('user' or 'assistant')
        content (str): The message content
        
    Returns:
        str: The ID of the saved message
    """
    try:
        # Prepare message data
        message_data = {
            "user_id": user_id,
            "area": area.lower(),
            "message_type": message_type,
            "content": content,
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Insert into chat_history table
        response = supabase.table("chat_history").insert(message_data).execute()
        
        if response.data:
            return response.data[0]["id"]
        else:
            raise Exception("Failed to save chat message")
            
    except Exception as e:
        raise Exception(f"Error saving chat message: {e}")

async def get_chat_history(user_id: str, area: str, limit: int = 50) -> List[ChatMessage]:
    """
    Retrieve chat history for a specific area.
    
    Args:
        user_id (str): The user's unique identifier
        area (str): The conversation area
        limit (int): Maximum number of messages to retrieve
        
    Returns:
        List[ChatMessage]: List of chat messages
    """
    try:
        # Query chat_history table
        response = supabase.table("chat_history")\
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
    
    Args:
        user_id (str): The user's unique identifier
        area (str): The conversation area
        message_count (int): Number of recent messages to include
        
    Returns:
        str: Formatted conversation context
    """
    try:
        # Get recent messages
        messages = await get_chat_history(user_id, area, message_count)
        
        if not messages:
            return ""
        
        # Format conversation context
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
    
    Args:
        user_id (str): The user's unique identifier
        area (str): The conversation area to clear
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Delete messages for the specific area
        response = supabase.table("chat_history")\
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
    
    Args:
        user_id (str): The user's unique identifier
        
    Returns:
        List[str]: List of areas with chat history
    """
    try:
        # Query distinct areas for the user
        response = supabase.table("chat_history")\
            .select("area")\
            .eq("user_id", user_id)\
            .execute()
        
        if response.data:
            # Extract unique areas
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
    
    Args:
        user_id (str): The user's unique identifier
        
    Returns:
        dict: Dictionary with area names as keys and message counts as values
    """
    try:
        # Query message counts by area
        response = supabase.table("chat_history")\
            .select("area")\
            .eq("user_id", user_id)\
            .execute()
        
        if response.data:
            # Count messages by area
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