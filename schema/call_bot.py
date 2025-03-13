from pydantic import BaseModel
class SDPRequest(BaseModel):
    sdp_offer: str
    prompt: str