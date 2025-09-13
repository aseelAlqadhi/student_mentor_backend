"""
Multi-area chat API endpoints.
This module handles area-specific chat conversations with separate threads.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Path
from typing import List
from app.shared.models import AreaChatRequest, AreaChatResponse, ChatHistoryResponse
from app.features.chat.services import save_chat_message, get_chat_history, clear_chat_history, get_user_areas_with_history, get_message_count_by_area
from app.features.profiles.services import get_user_context_for_ai
from app.api.v1.auth.dependencies import get_user_identifier
from app.features.chat.ai.gemini import Gemini
from app.features.chat.ai.prompts import get_area_prompt, get_available_areas
import os

# Create router for area chat endpoints
router = APIRouter(prefix="/chat", tags=["area-chat"])

# Initialize AI platform
gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

# Create AI instances for each area
ai_instances = {}
for area in get_available_areas():
    area_prompt = get_area_prompt(area)
    ai_instances[area] = Gemini(api_key=gemini_api_key, system_prompt=area_prompt)

@router.post("/{area}", response_model=AreaChatResponse)
async def area_chat(
    request: AreaChatRequest,
    area: str = Path(..., description="Chat area: health, career, finance, or general"),
    user_id: str = Depends(get_user_identifier)
):
    """
    Send a message to the AI mentor for a specific area.
    
    Args:
        area: The conversation area (health, career, finance, general)
        request: The chat request with prompt
        user_id: User identifier from authentication
        
    Returns:
        AreaChatResponse: AI mentor's response for the specific area
    """
    try:
        # Validate area
        area = area.lower()
        if area not in get_available_areas():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid area. Available areas: {', '.join(get_available_areas())}"
            )
        
        # Get user context for enhanced responses
        user_context = await get_user_context_for_ai(user_id)
        
        # Get recent conversation context
        from app.features.chat.services import get_recent_context
        conversation_context = await get_recent_context(user_id, area, 10)
        
        # Prepare the enhanced prompt
        enhanced_prompt_parts = []
        
        # Add user context if available
        if user_context:
            enhanced_prompt_parts.append(f"User Context: {user_context}")
        
        # Add conversation context if available
        if conversation_context:
            enhanced_prompt_parts.append(f"Recent Conversation:\n{conversation_context}")
        
        # Add current user message
        enhanced_prompt_parts.append(f"Current User Message: {request.prompt}")
        
        # Combine all parts
        enhanced_prompt = "\n\n".join(enhanced_prompt_parts)
        
        # Get AI response using area-specific instance
        ai_instance = ai_instances[area]
        ai_reply = ai_instance.chat(enhanced_prompt)
        
        # Save user message to chat history
        await save_chat_message(user_id, area, "user", request.prompt)
        
        # Save AI response to chat history
        message_id = await save_chat_message(user_id, area, "assistant", ai_reply)
        
        return AreaChatResponse(
            response=ai_reply,
            area=area,
            message_id=message_id
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.get("/{area}/history", response_model=ChatHistoryResponse)
async def get_area_chat_history(
    area: str = Path(..., description="Chat area: health, career, finance, or general"),
    limit: int = 50,
    user_id: str = Depends(get_user_identifier)
):
    """
    Get chat history for a specific area.
    
    Args:
        area: The conversation area
        limit: Maximum number of messages to retrieve
        user_id: User identifier from authentication
        
    Returns:
        ChatHistoryResponse: Chat history for the specified area
    """
    try:
        # Validate area
        area = area.lower()
        if area not in get_available_areas():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid area. Available areas: {', '.join(get_available_areas())}"
            )
        
        # Get chat history
        messages = await get_chat_history(user_id, area, limit)
        
        return ChatHistoryResponse(
            area=area,
            messages=messages,
            total_messages=len(messages)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving chat history: {str(e)}"
        )

@router.delete("/{area}/history")
async def clear_area_chat_history(
    area: str = Path(..., description="Chat area: health, career, finance, or general"),
    user_id: str = Depends(get_user_identifier)
):
    """
    Clear chat history for a specific area.
    
    Args:
        area: The conversation area to clear
        user_id: User identifier from authentication
        
    Returns:
        dict: Success message
    """
    try:
        # Validate area
        area = area.lower()
        if area not in get_available_areas():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid area. Available areas: {', '.join(get_available_areas())}"
            )
        
        # Clear chat history
        success = await clear_chat_history(user_id, area)
        
        if success:
            return {"message": f"Chat history cleared for {area} area"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear chat history"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error clearing chat history: {str(e)}"
        )

@router.get("/areas")
async def get_user_chat_areas(user_id: str = Depends(get_user_identifier)):
    """
    Get list of areas where the user has chat history.
    
    Args:
        user_id: User identifier from authentication
        
    Returns:
        dict: List of areas with chat history and message counts
    """
    try:
        # Get areas with history
        areas_with_history = await get_user_areas_with_history(user_id)
        
        # Get message counts by area
        message_counts = await get_message_count_by_area(user_id)
        
        # Get all available areas
        all_areas = get_available_areas()
        
        # Prepare response
        areas_info = []
        for area in all_areas:
            areas_info.append({
                "area": area,
                "has_history": area in areas_with_history,
                "message_count": message_counts.get(area, 0)
            })
        
        return {
            "areas": areas_info,
            "total_areas": len(all_areas),
            "areas_with_history": len(areas_with_history)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user areas: {str(e)}"
        )

@router.get("/areas/available")
async def get_available_chat_areas():
    """
    Get list of all available chat areas.
    
    Returns:
        dict: List of available areas with descriptions
    """
    area_descriptions = {
        "health": "Health and wellness guidance including physical health, mental health, and lifestyle balance",
        "career": "Career development, job search, skill building, and professional growth",
        "finance": "Financial literacy, budgeting, debt management, and money management",
        "general": "General academic and personal development support"
    }
    
    areas = get_available_areas()
    return {
        "areas": [
            {
                "name": area,
                "description": area_descriptions.get(area, "General support area")
            }
            for area in areas
        ]
    } 