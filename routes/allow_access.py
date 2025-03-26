from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

# for decoding 
from services.custom_link import decode_token

# for creating new demo user
from services.postgres import grant_access_by_email

# For sendinf confirmation email to the carehome
from services.send_email import send_email_alert

from services.postgres import give_access_to_user_by_admin

from services.send_email import send_email_alert

router = APIRouter()

@router.get("/allow-demo-access/{encoded_data}")
def allow_demo_access(encoded_data: str):
    """Check if the token is authentic and allow access to the user also when we allow user the access we send him/her an email"""
    try:
        decoded = decode_token(encoded_data)
        print(decoded['email'])
        if decoded['allow_access']:
            did_upload = grant_access_by_email(decoded["email"])
            if did_upload:
                subject ="Your Request for demo bot has been granted"
                body = "Hi please go back to the login"
                did_send = send_email_alert(decoded['email'],subject, body)
                if did_send:
                    return JSONResponse(content={"status": True, "detail": " "}, status_code=200)
                else:
                    return JSONResponse(content={"status": False, "detail": "Couldn't send email"})
            else:
                return JSONResponse(content={"status": False, "detail": "user doesn't exist which is impossible"}, status_code=400)
        else: 
            return JSONResponse(content={"status": False, "detail": "Bad Link"}, status_code=400) 
    except Exception as e:
        print("Error: ",str(e))
        return JSONResponse(content={"details": "Error occured"}, status_code=500)
    

@router.post("/give-access-to-user")
def give_access_to_user(email: str):
    """
    Endpoint to give access to user
    """
    try:
        give_access_to_user_by_admin(email)
        # Send email to user to inform that they have access to the bot
        subject = "Your Request for demo bot has been granted"
        body = "Hi please go back to the login"
        did_send = send_email_alert(email, subject, body)
        if did_send:
            return JSONResponse(content={"status": True, "detail": "Access email sent to user"}, status_code=200)
        else:
            return JSONResponse(content={"status": False, "detail": "Couldn't send email"}, status_code=400)
    except HTTPException as http_exc:
        return JSONResponse(content={"status": False, "detail": http_exc.detail}, status_code=http_exc.status_code)
    except Exception as e:
        print(f"Error in give_access_to_user: {str(e)}")
        return JSONResponse(content={"status": False, "detail": "An unexpected error occurred"}, status_code=500)