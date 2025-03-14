from pydantic import BaseModel
class SDPRequest(BaseModel):
    sdp_offer: str
    patient_id: str