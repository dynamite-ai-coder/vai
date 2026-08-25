from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=8000)
    use_browser: bool = False


class ChatResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    reply: str
    model_responses: dict = {}
    synthesis_info: dict = {}
    browser_result: Optional[str] = None


class ModelStatus(BaseModel):
    name: str
    role: str
    status: str
    model: str


class StatusResponse(BaseModel):
    status: str
    models: dict
    browser_use: bool
    all_keys_configured: bool
