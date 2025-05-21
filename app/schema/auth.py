from pydantic import BaseModel

class RegisterAccess(BaseModel):
    name: str
    email: str
    phone_number: str



class LoginRequest(BaseModel):
    email: str