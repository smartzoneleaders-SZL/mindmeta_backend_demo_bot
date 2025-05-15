from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response, JSONResponse
import asyncio


from schema.call_bot import TelephonicCall


from services.postgres import get_patient_id_from_schedule_id



from services.postgres import get_time_from_schedule_call_using_patient_id, get_voice_from_db, get_first_name_of_patient, get_carehome_id_from_patient_id
from services.eleven_lab_services import eleven_labs_voices

# for db
from fastapi import Depends
from sqlalchemy.orm import Session
from db.postgres import get_db

# for call
import argparse
from services.telephonic_service import voice_bot_demo

router = APIRouter()



@router.post("/call-telephonic", status_code=status.HTTP_204_NO_CONTENT)
async def call_on_telephone(request: TelephonicCall, db: Session = Depends(get_db)):
    try:
        # Step 1: Collect required data synchronously
        patient_id = get_patient_id_from_schedule_id(db, request.schedule_id)
        call_time = get_time_from_schedule_call_using_patient_id(request.schedule_id)
        voice = get_voice_from_db(patient_id)
        voice_id = eleven_labs_voices.get(voice, "gUbIduqGzBP438teh4ZA")
        patient_first_name = get_first_name_of_patient(patient_id)
        carehome_id = get_carehome_id_from_patient_id(patient_id)

        # args for the voice bot
        def create_args():
            parser = argparse.ArgumentParser()
            parser.add_argument('--server')
            parser.add_argument('--username')
            parser.add_argument('--password')
            parser.add_argument('--domain')
            parser.add_argument('--destination')
            parser.add_argument('--voice-id', default=voice_id)
            parser.add_argument('--latency', type=int, default=4)
            parser.add_argument('--debug-level', type=int, default=1)
            args = parser.parse_args([])  # Avoid using CLI args
            args.server = "wss://example.com:8080/ws"
            args.username = "your_sip_username"
            args.password = "your_sip_password"
            args.domain = "your_sip_domain"
            args.destination = request.phone_number  # Or from patient info
            return args

        args = create_args()


        asyncio.create_task(voice_bot_demo(args))


        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except HTTPException as http_exc:
        return JSONResponse(content={"detail": http_exc.detail}, status_code=http_exc.status_code)
    except Exception as e:
        raise HTTPException(status_code=500, detail="An error occurred")
                      