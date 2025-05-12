import re
import logging

import uuid

def parse_boolean_from_response(response):
    """
    Converts string 'True' or 'False' from model response to actual boolean.
    """
    match = re.fullmatch(r"True|False", response.strip())
    if match:
        return response.strip() == "True"
    else:
        raise ValueError(f"Unexpected response format: {response}")
    
    
    
async def send_interruption(websocket):
    logging.info("Intruption done")
    await websocket.send_text("intruption")
    
    
    
def append_sentiment_analysis_value(chats, sentiment_analysis_value):
    chats.append({"sentiment_analysis_value": sentiment_analysis_value})
    return chats



def generate_uuid():
    return str(uuid.uuid4())
