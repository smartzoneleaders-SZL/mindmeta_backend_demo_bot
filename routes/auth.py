from fastapi import APIRouter
from fastapi.responses import JSONResponse

# for schema
from schema.auth import RegisterAccess, LoginRequest


# For encoding service
from services.custom_link import generate_token

# for sending emails
from services.send_email import send_email_alert

# Check postgres db to verify 48 hours demo user
from services.postgres import add_demo_history, is_user_eligible_for_call, validate_user

# check if user already exist in out database   and create a demo user
from services.postgres import does_user_exist, create_new_demo_access, delete_user_from_db

from fastapi import HTTPException
import os

# for db
from fastapi import Depends
from sqlalchemy.orm import Session
from db.postgres import get_db

router = APIRouter()

@router.post("/register-for-access")
def register_for_access(request: RegisterAccess):
    """To send email to admin for 48 hour demo access of the bot"""
    try:
        user =  does_user_exist(request.email)
        if user:
            return JSONResponse(content={"request_sent": False, "detail": "User already exist"},status_code=409)
        did_create = create_new_demo_access(request.email,request.name,request.phone_number)
        print("did_create: ",did_create)
        if did_create:
            encoded_data = generate_token(request.name, request.email, request.phone_number)
            access_link = f"{os.getenv('BACKEND_LINK')}/api/allow-access/allow-demo-access/{encoded_data}"
            subject = "Someone is requesting for the demo of the bot"
            body = f"""Hi Kamran, {request.name} is asking for the access to the demo bot under email id: {request.email}
                    Click the link below to send allow them.
                    {access_link}
            """
            did_send_email = send_email_alert(os.getenv('ADMIN_EMAIL'),subject,body)
            if did_send_email:
                return JSONResponse(content={"request_sent": True, "detail": "Your request for demo bot has been sent. Please be patient. Your request will be granted soon"}, status_code=200)
            else:
                return JSONResponse(content={"request_sent": False, "detail": "There was an error sending your request to the admin"}, status_code=400)
        else:
            return JSONResponse(content={"detail": "Error while creating user in DB"}, status_code=500)
    except Exception as e:
        print("Error Is: ",str(e))
        return JSONResponse(content={"detail": "An Error occured"}, status_code= 500)




@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """To login user and verify the user access"""
    try:
        validated = validate_user(request.email)
        if(validated):
            is_eligible, total_time = is_user_eligible_for_call(db, request.email)
            if is_eligible:
                return JSONResponse(content={"access": True, "detail": ""}, status_code=200)
            else:
                add_demo_history(request.email)
                delete_user_from_db(request.email)
                return JSONResponse(content={"access": False, "detail": "Demo time (30 minutes) used. Please register again to continue."}, status_code=403)
    except HTTPException as http_exc:
        # Extract details and status code from the HTTPException.
        return JSONResponse(content={"detail": http_exc.detail}, status_code=http_exc.status_code)
    except Exception as e:
        print("Error on /login endpoint: ", str(e))
        return JSONResponse(content={"detail": "An Error has occurred"}, status_code=500)
