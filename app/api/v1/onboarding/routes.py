"""
Onboarding API endpoints for user profile setup.
This module handles the onboarding questionnaire flow for new users.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.shared.models import OnboardingRequest, OnboardingResponse, OnboardingStatusResponse
from app.features.profiles.services import check_onboarding_status, update_user_profile
from app.api.v1.auth.dependencies import get_user_identifier

# Create router for onboarding endpoints
router = APIRouter(prefix="/onboarding", tags=["onboarding"])

@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(user_id: str = Depends(get_user_identifier)):
    """
    Check if the current user has completed the onboarding process.
    
    Args:
        user_id: User identifier from authentication
        
    Returns:
        OnboardingStatusResponse: Status of onboarding completion and profile data
    """
    try:
        # Get onboarding status for the user
        status_data = await check_onboarding_status(user_id)
        
        return OnboardingStatusResponse(
            onboarding_completed=status_data["onboarding_completed"],
            profile=status_data["profile"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking onboarding status: {str(e)}"
        )

@router.post("/submit", response_model=OnboardingResponse)
async def submit_onboarding(
    onboarding_data: OnboardingRequest,
    user_id: str = Depends(get_user_identifier)
):
    """
    Submit onboarding questionnaire responses for the current user.
    
    Args:
        onboarding_data: The onboarding questionnaire responses
        user_id: User identifier from authentication
        
    Returns:
        OnboardingResponse: Success status and updated profile data
    """
    try:
        # Validate that all required fields are provided
        if not onboarding_data.challenges_goals.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Challenges and goals field is required"
            )
            
        if not onboarding_data.living_situation.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Living situation field is required"
            )
            
        if not onboarding_data.guidance_preference:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Guidance preference is required"
            )
        
        # Ensure user profile exists before updating
        # This will create a profile if it doesn't exist
        await check_onboarding_status(user_id)
        
        # Update user profile with onboarding data
        updated_profile = await update_user_profile(user_id, onboarding_data)
        
        return OnboardingResponse(
            success=True,
            message="Onboarding completed successfully! Your profile has been updated.",
            profile=updated_profile
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting onboarding data: {str(e)}"
        )

@router.get("/questions")
async def get_onboarding_questions():
    """
    Get the onboarding questions for the frontend to display.
    
    Returns:
        dict: The onboarding questions and their metadata
    """
    return {
        "questions": [
            {
                "id": "challenges_goals",
                "question": "What are your biggest challenges or goals right now across health, career, and finances? Be as specific as possible about what you're trying to achieve or overcome.",
                "type": "text",
                "required": True,
                "placeholder": "Describe your current challenges and goals..."
            },
            {
                "id": "living_situation", 
                "question": "What's your current living situation and support system? (e.g., studying abroad, living independently, family support available, etc.)",
                "type": "text",
                "required": True,
                "placeholder": "Describe your living situation and support network..."
            },
            {
                "id": "guidance_preference",
                "question": "How do you prefer to receive guidance?",
                "type": "select",
                "required": True,
                "options": [
                    {"value": "supportive_empathetic", "label": "Supportive - Encouraging and positive"},
                    {"value": "action_oriented_practical", "label": "Action-oriented - Focused on practical steps"},
                    {"value": "analytical_detailed", "label": "Analytical - Detailed analysis and reasoning"},
                    {"value": "empathetic_understanding", "label": "Empathetic - Understanding and compassionate"},
                    {"value": "challenge_focused_growth", "label": "Challenge-focused - Pushing you to grow"},
                    {"value": "balanced_mixed", "label": "Balanced - Mix of empathy and practical advice"},
                    {"value": "motivational_inspiring", "label": "Motivational - Energetic and inspiring"},
                    {"value": "reflective_deepthinking", "label": "Reflective - Helps you analyze and think deeply"}
                ]
            }
        ]
    } 
