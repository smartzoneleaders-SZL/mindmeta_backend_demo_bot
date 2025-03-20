from fastapi import APIRouter
from fastapi.responses import JSONResponse

# for schema
from schema.auth import RegisterAccess, LoginRequest


# For encoding service
from services.custom_link import generate_token

# for sending emails
from services.send_email import send_email_alert

# Check postgres db to verify 48 hours demo user
from services.postgres import validate_user


router = APIRouter()

@router.post("/register-for-access")
def register_for_access(request: RegisterAccess):
    """To send email to admin for 48 hour demo access of the bot"""
    try:
        encoded_data = generate_token(request.name, request.email, request.phone_number)
        access_link = f"http://192.168.10.16:8000/api/allow-access/allow-demo-access/{encoded_data}"
        subject = "Someone is requesting for the demo of the bot"
        body = f"""Hi Kamran, {request.name} is asking for the access to the demo bot under email id: {request.email}
                Click the link below to send allow them.
                {access_link}
        """
        did_send_email = send_email_alert("devsarab01@gmail.com",subject,body)
        if did_send_email:
            return JSONResponse(content={"request_sent": True, "details": "Your request for demo bot has been sent. Please be patient. Your request will be granted soon"}, status_code=200)
        else:
            return JSONResponse(content={{"request_sent": False, "details": "There was an error sending your request to the admin"}}, status_code=400)
    except Exception as e:
        print("Error is: ",str(e))
        return JSONResponse(content={"details": "An Error occured"}, status_code= 500)


@router.post("/login")
def login(request: LoginRequest):
    """To login user and verify the user access"""
    try:
        validated = validate_user(request.email)
        if validated:
            return JSONResponse(content={"access": validated, "details": " "}, status_code=200 )
        else:
            return JSONResponse(content={"access": validated, "details": "User didn't register"}, status_code=404 )
    except Exception as e:
        return JSONResponse(content={"detail": "An Error has occured"}, status_code=500)