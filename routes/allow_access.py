from fastapi import APIRouter
from fastapi.responses import JSONResponse

# for decoding 
from services.custom_link import decode_token

# for creating new demo user
from services.postgres import create_new_demo_access

# For sendinf confirmation email to the carehome
from services.send_email import send_email_alert

router = APIRouter()

@router.get("/allow-demo-access/{encoded_data}")
def allow_demo_access(encoded_data: str):
    """Check if the token is authentic and allow access to the user also when we allow user the access we send him/her an email"""
    try:
        decoded = decode_token(encoded_data)
        print(decoded['email'])
        if decoded['allow_access']:
            did_upload = create_new_demo_access(decoded["email"], decoded["name"], decoded["phone_number"])
            if did_upload:
                subject ="Your Request for demo bot has been granted"
                body = "Hi please go back to the login"
                did_send = send_email_alert(decoded['email'],subject, body)
                if did_send:
                    return JSONResponse(content={"status": True, "detail": " "}, status_code=200)
                else:
                    return JSONResponse(content={"status": False, "detail": "Couldn't send email"})
            else:
                return JSONResponse(content={"status": False, "detail": "Database Error"}, status_code=400)
        else: 
            return JSONResponse(content={"status": False, "detail": "Bad Link"}, status_code=400) 
    except Exception as e:
        print("Error: ",str(e))
        return JSONResponse(content={"details": "Error occured"}, status_code=500)
