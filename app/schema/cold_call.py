from pydantic import BaseModel

class ColdCallRequest(BaseModel):
    script: str