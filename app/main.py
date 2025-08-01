"""
Main FastAPI application for the AI mentorship backend.
This module sets up the FastAPI app with authentication and chat endpoints.
"""

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.shared.models import PromptResponse, PromptRequest
from app.features.profiles.services import get_user_context_for_ai
from app.features.chat.ai.gemini import Gemini
from app.api.v1.auth.dependencies import get_user_identifier
from app.api.v1.auth.throttling import apply_rate_limit
from app.api.v1.auth.routes import router as auth_router
from app.api.v1.onboarding.routes import router as onboarding_router
from app.api.v1.chat.routes import router as area_chat_router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Mentor Backend",
    description="Backend API for AI mentorship application with Supabase authentication",
    version="1.0.0"
)

# Include authentication routes
app.include_router(auth_router)

# Include onboarding routes
app.include_router(onboarding_router)

# Include area chat routes
app.include_router(area_chat_router)

# Mount static files for auth callback page
try:
    app.mount("/public", StaticFiles(directory="public"), name="public")
except:
    # Create public directory if it doesn't exist
    os.makedirs("public", exist_ok=True)
    app.mount("/public", StaticFiles(directory="public"), name="public")

# --- AI Configuration ---
def load_system_prompt():
    """
    Load the system prompt for the AI mentor.
    Returns a default prompt if the file is not found.
    """
    try:
        # Try to load from the correct path
        with open("app/features/chat/ai/system_prompt.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Return a default system prompt if file doesn't exist
        return """You are an AI mentor designed to help students with their academic and personal development. 
        Provide thoughtful, encouraging, and educational responses. Be supportive while also challenging 
        students to think critically and grow."""

# Load system prompt and initialize AI
system_prompt = load_system_prompt()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

# Initialize the AI platform
ai_platform = Gemini(api_key=gemini_api_key, system_prompt=system_prompt)

# --- API Endpoints ---
@app.post("/chat", response_model=PromptResponse)
async def chat(request: PromptRequest, user_id: str = Depends(get_user_identifier)):
    """
    Chat endpoint for AI mentorship conversations.
    
    Args:
        request: The chat prompt from the user
        user_id: User identifier for rate limiting
        
    Returns:
        PromptResponse: AI mentor's response
    """
    # Apply rate limiting
    apply_rate_limit(user_id)
    
    # Get user context for enhanced AI responses
    user_context = await get_user_context_for_ai(user_id)
    
    # Prepare the prompt with user context if available
    if user_context:
        enhanced_prompt = f"User Context: {user_context}\n\nUser Question: {request.prompt}"
    else:
        enhanced_prompt = request.prompt
    
    # Get AI response with enhanced context
    ai_reply = ai_platform.chat(enhanced_prompt)
    
    # Format the response
    formatted_reply = f'user: "{request.prompt}"\nmentor app: "{ai_reply}"'
    
    return PromptResponse(response=formatted_reply)

@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running.
    
    Returns:
        dict: API status message
    """
    return {
        "message": "AI Mentor Backend API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/auth-callback")
async def auth_callback_page():
    """
    Serve the auth callback HTML page for handling Supabase redirects.
    
    Returns:
        FileResponse: The auth callback HTML page
    """
    return FileResponse("public/auth-callback.html")

@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "ai_platform": "gemini",
        "authentication": "supabase"
    }
