from pydantic import BaseModel
class SDPRequest(BaseModel):
    sdp_offer: str
    patient_id: str
    # prompt: str


class RequestData(BaseModel):
    patient_id:str

class CallYourBot(BaseModel):
    sdp_offer: str
    prompt: str
    voice_name: str