from pydantic import BaseModel, EmailStr
from typing import Optional, Union, Literal, List
from datetime import datetime

# Existing chat models
class PromptRequest(BaseModel):
    prompt: str # json body request  -> {"prompt":"..."}

class PromptResponse(BaseModel):
    response: str # return json body ->{"res":"..."}

# Multi-Area Chat Models
class AreaChatRequest(BaseModel):
    """Model for area-specific chat requests"""
    prompt: str
    area: str = "general"  # Default to general if not specified

class ChatMessage(BaseModel):
    """Model for individual chat messages"""
    id: Optional[str] = None
    message_type: str  # "user" or "assistant"
    content: str
    created_at: Optional[Union[str, datetime]] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class ChatHistoryResponse(BaseModel):
    """Model for chat history response"""
    area: str
    messages: List[ChatMessage]
    total_messages: int

class AreaChatResponse(BaseModel):
    """Model for area-specific chat response"""
    response: str
    area: str
    message_id: Optional[str] = None

# Authentication models
class UserSignUp(BaseModel):
    """Model for user registration request"""
    email: EmailStr
    password: str

class UserSignIn(BaseModel):
    """Model for user login request"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Model for user data response"""
    id: str
    email: str
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None
    
    class Config:
        # Allow datetime objects to be converted to strings
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class EnhancedUserResponse(BaseModel):
    """Enhanced model for user data response including profile information"""
    id: str
    email: str
    # Auth user timestamps
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None
    # Profile information
    onboarding_completed: bool = False
    challenges_goals: Optional[str] = None
    living_situation: Optional[str] = None
    guidance_preference: Optional[str] = None
    profile_created_at: Optional[Union[str, datetime]] = None
    profile_updated_at: Optional[Union[str, datetime]] = None
    
    class Config:
        # Allow datetime objects to be converted to strings
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        # Exclude None values from JSON response
        exclude_none = True

class AuthResponse(BaseModel):
    """Model for authentication response"""
    user: UserResponse
    access_token: str
    refresh_token: str  # Changed from Optional to required
    expires_in: Optional[int] = None
    message: Optional[str] = None
    
    class Config:
        # Exclude None values from JSON response
        exclude_none = True

class TokenResponse(BaseModel):
    """Model for token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str
    message: str

# Onboarding and User Profile Models
class OnboardingRequest(BaseModel):
    """Model for onboarding questionnaire submission"""
    challenges_goals: str  # Question 1: Challenges/goals across health, career, finances
    living_situation: str  # Question 2: Current living situation and support system
    guidance_preference: Literal["supportive", "action-oriented", "analytical", "empathetic", "challenge-focused"]  # Question 3: Guidance preference

class UserProfile(BaseModel):
    """Model for user profile data"""
    id: Optional[str] = None  # Primary key from database
    user_id: str
    challenges_goals: Optional[str] = None
    living_situation: Optional[str] = None
    guidance_preference: Optional[str] = None
    onboarding_completed: bool = False
    created_at: Optional[Union[str, datetime]] = None
    updated_at: Optional[Union[str, datetime]] = None
    
    class Config:
        # Allow datetime objects to be converted to strings
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class OnboardingStatusResponse(BaseModel):
    """Model for onboarding status check response"""
    onboarding_completed: bool
    profile: Optional[UserProfile] = None

class OnboardingResponse(BaseModel):
    """Model for onboarding submission response"""
    success: bool
    message: str
    profile: UserProfile
