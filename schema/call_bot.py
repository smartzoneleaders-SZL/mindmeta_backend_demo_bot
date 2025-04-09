from pydantic import BaseModel
class SDPRequest(BaseModel):
    sdp_offer: str
    patient_id: str
    schedule_id: str


class RequestData(BaseModel):
    patient_id:str

class CallYourBot(BaseModel):
    email: str
    sdp_offer: str
    prompt: str
    voice_name: str

class CallEndDemo(BaseModel):
    time:int
    email: str