from pydantic import BaseModel

class PromptRequest(BaseModel):
    prompt: str # json body request  -> {"prompt":"..."}

class PromptResponse(BaseModel):
    response: str # retuurn json body ->{"res":"..."}
