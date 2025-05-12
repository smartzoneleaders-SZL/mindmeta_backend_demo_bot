from pydantic import BaseModel
class SDPRequest(BaseModel):
    sdp_offer: str
    patient_id: str
    schedule_id: str


class RequestData(BaseModel):
    patient_id:str

class ShouldAllowCall(BaseModel):
    email: str


class CallEndDemo(BaseModel):
    time:int
    email: str