from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from datetime import datetime

# Existing chat models
class PromptRequest(BaseModel):
    prompt: str # json body request  -> {"prompt":"..."}

class PromptResponse(BaseModel):
    response: str # return json body ->{"res":"..."}

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

class AuthResponse(BaseModel):
    """Model for authentication response"""
    user: UserResponse
    access_token: str
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None

class TokenResponse(BaseModel):
    """Model for token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str
    message: str
