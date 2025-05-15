from fastapi import HTTPException

from db.mongo_db import db
from datetime import datetime, timezone



import base64
from bson.binary import Binary



# For logging
import logging
logger = logging.getLogger(__name__)

async def upload_chat_history_on_mongodb(patient_id: str, call_id: str, new_chats: list, carehome_id: str, sentiment):
    try:
       
        new_chats.insert(0, {"user_sentiment": sentiment})

        # Validate structure
        if not new_chats or "user_sentiment" not in new_chats[0]:
            raise ValueError("new_chats must start with a 'user_sentiment' entry.")

        sentiment = new_chats[0]["user_sentiment"]
        conversation = new_chats[1:]

        # Create the call entry
        call_entry = {
            "call_id": Binary(base64.b64decode(call_id), subtype=4),
            "call_time": datetime.now(timezone.utc),
            "sentiment_analysis": sentiment,
            "conversation": conversation
        }

        # Match document by patient ID
        filter_query = {"patient_id": patient_id}

        # Only set patient_id and carehome_id on insert (not calls!)
        update_query = {
            "$setOnInsert": {
                "patient_id": patient_id,
                "carehome_id": carehome_id
            },
            "$push": {
                "calls": call_entry
            }
        }

        result = await db.chats.update_one(filter_query, update_query, upsert=True)
        logger.info("Call uploaded for patient_id: %s, carehome_id: %s", patient_id, carehome_id)
        return True

    except Exception as e:
        logger.error("Error in upload_list_on_mongodb: %s", str(e))
        raise HTTPException(status_code=500, detail="Error on storing call history db")



async def upload_on_mongodb(patient_id: str, call_id: str, data_to_upload: dict) -> int:
    """
    Updates (or creates) a document for the given patient. The document will have:
      - _id: randomly generated ObjectId (by MongoDB)
      - patient_id: the given patient_id
      - carehome_id: the given carehome_id (from data_to_upload)
      - calls: an array in which each element is an object with:
            {
                "call_id": <call_id>,
                "human_messages": <messages>,
                "sentiment_analysis": <sentiment_analysis>
            }
    
    If a document for the given patient_id exists, the function pushes a new call object onto the calls array.
    Otherwise, it creates a new document with the provided fields.
    
    Args:
        patient_id (str): The patient’s identifier.
        call_id (str): The call identifier.
        data_to_upload (dict): Should contain:
            - "human_messages": the messages text,
            - "sentiment_analysis": the sentiment analysis,
            - "carehome_id": the care home identifier.
    
    Returns:
        int: The number of documents modified.
    """
    try:
        # Filter: find document by patient_id
        filter_query = {"patient_id": patient_id}
        
        # Build the call object to insert
        new_call = {
            "call_id": call_id,
            "human_messages": data_to_upload.get("human_messages"),
            "sentiment_analysis": data_to_upload.get("sentiment_analysis"),
            "call_time": datetime.utcnow()
        }
        
        # Update: push new call into the 'calls' array.
        # $setOnInsert sets patient_id and carehome_id if the document is created.
        update_query = {
            "$push": {"calls": new_call},
            "$setOnInsert": {
            "patient_id": patient_id,
            "carehome_id": data_to_upload.get("carehome_id")}}

    
        # Use upsert=True to create a new document if one does not exist.
        result = await db.chats.update_one(filter_query, update_query, upsert=True)
        logger.info("Document updated for patient_id: %s with call_id: %s", patient_id, call_id)
        return result.modified_count
    except Exception as e:
        print("Error in mongodb service is: ", str(e))
        logger.error("Error in upload_on_mongodb: %s", str(e))
        raise

