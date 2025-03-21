from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

# import schema
from schema.call_bot import CallEndDemo

# For updating the time after the call
from services.postgres import update_time_of_call

# Now For /start call endpoint
from urllib.parse import quote
# import schema
from schema.call_bot import CallYourBot
# import variables from .evn for openai etc
import os
import httpx

# for db
from fastapi import Depends
from sqlalchemy.orm import Session
from db.postgres import get_db

# To check eligibility for if user has used the bot for more than 30 mins
from services.postgres import is_user_eligible_for_call




router = APIRouter()


@router.post("/call-with-bot-end")
def upload_call_data_on_mongodb(request :CallEndDemo, db: Session = Depends(get_db)):
    try:
        did_change = update_time_of_call(db,request.email,request.time)
        if did_change:
            return {"sucess": True, "details": " "}
    except HTTPException as http_exc:
        return JSONResponse(content={"detail": http_exc.detail}, status_code=http_exc.status_code)
    except Exception as e:
        print("Error in call_with_bot_end in main.py -> ",str(e))
        raise HTTPException(status_code=500, detail="An Error has occured")
    




@router.post("/start-call-yourself")
async def start_call(request: CallYourBot, db: Session = Depends(get_db)):
    try:
        sdp_offer = request.sdp_offer
        instructions =request.prompt
        voice_option = request.voice_name

        user_eligibility, total_time = is_user_eligible_for_call(db, request.email)
        if user_eligibility:
    # print("User prompt is: ",instructions)
    # patient_id = request.patient_id
            if not os.getenv('OPENAI_API_KEY'):
                raise HTTPException(status_code=500, detail="Missing OpenAI API key")
    # Build the URL with model and instructions passed as query parameters.
    # Use urllib.parse.quote to ensure proper URL-encoding of the instructions.
            query_params = (
                f"?model={os.getenv('MODEL')}"
                f"&instructions={quote(instructions)}"
                f"&voice={quote(voice_option)}"
                f"&cache=true"         # Enable caching
                # f"&cache_level=1"    # Optionally set cache level (if supported)
            )
            base_url = os.getenv('OPENAI_BASE_URL')
            url = f"{base_url}{query_params}"

            headers = {
                "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                "Content-Type": "application/sdp",  
            }

            async with httpx.AsyncClient() as client:
            # Send the SDP offer along with the query parameters.
                response = await client.post(url, headers=headers, data=sdp_offer)
        # print("Print response status: ",response.status_code)
                if response.status_code == 200 or response.status_code == 201:
                    return JSONResponse(
                        status_code=response.status_code,
                        content={"sdp_answer": response.text,"total_time": total_time}
                    )
                else:
                    return JSONResponse(status_code=500, content={"detail":"An Error occured"})
    except Exception as e:
        print("Error as: ", str(e))
        raise
