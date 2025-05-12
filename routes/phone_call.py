from fastapi import FastAPI, HTTPException

import asyncio
from services.opensips_ws_lib import OpenSIPSClient


app = FastAPI()


@app.post("/call-user")
async def call_user(patient_id):
    try:
        
        ## We will use user id to get its number form postgres db then call it
        
        
        # but right now sinply call a dummy number for testing 
        
        dummy_number = "+1234567890"
        
        # Create the client
        client = OpenSIPSClient(
            server_uri="wss://ats-demo.call-matrix.com:6061",
            username="test_test.com",
            password="l3tMe.Test",
            domain="tenant_2"
        )

        # Connect
        if not await client.connect():
            raise HTTPException(status_code=500, detail="Failed to connect to SIP server")

        # Register
        if not await client.register():
            raise HTTPException(status_code=500, detail="Failed to register with SIP server")

        # Place the call
        result = await client.place_call(dummy_number, timeout=30)
        if result["success"]:
            call_id = result["call_id"]
            print(f"Call answered: {call_id}")

            # Play an audio file 
            await client.play_audio_to_call(call_id, "./my_test_file.wav")
            await asyncio.sleep(10)

            await client.end_call(call_id)
            await client.disconnect()

            return {"status": "success", "call_id": call_id}
        else:
            await client.disconnect()
            return {"status": "failed", "reason": result["state"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Call failed: {str(e)}")
