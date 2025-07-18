
from fastapi import FastAPI, Depends
import os
from app.models import PromptResponse, PromptRequest
from pydantic import BaseModel
from app.gemini import Gemini
from app.auth.dependencies import get_user_identifier
from app.auth.throttling import apply_rate_limit
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# --- AI Configuration ---
def load_system_prompt():
    try:
        with open("src/prompts/system_prompt.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return None

system_prompt = load_system_prompt()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

ai_platform = Gemini(api_key=gemini_api_key, system_prompt=system_prompt)

# --- API Endpoints ---
@app.post("/chat", response_model=PromptResponse)
async def chat(request: PromptRequest, user_id: str = Depends(get_user_identifier)):
    apply_rate_limit(user_id)
    ai_reply = ai_platform.chat(request.prompt)
    formatted_reply = f'user: "{request.prompt}"\nmentor app: "{ai_reply}"'
    return PromptResponse(response=formatted_reply)

@app.get("/")
async def root():
    return {"message": "api is running"}
