

from services.mongodb_service import upload_on_mongodb

# For sentiment analysis
from services.sentiment_analysis import check_sentiment_using_textblob

# For append_sentiment_analysis_value 
from utils.utils import append_sentiment_analysis_value


async def get_chat_hisory(patient_id ,chat_with_model,call_id):

    """ This function get the chat history of patient from langchain whose call just ended. 
    So all the chat done in that particular call.
    
    INPUT:
        - langchain history object
        - chat id of langchain
    
    OUTPUT:
        - history in langhchain object which contains role, token amount, message etc 
    """
    try:
        config = {"configurable": {"thread_id": call_id}}
        state_snapshot = chat_with_model.get_state(config)
        chat_history = parse_chat_history(state_snapshot.values["messages"])
        human_messages = get_human_messages_out_of_call_chat(chat_history)
        sentiment_analysis = check_sentiment_using_textblob(human_messages)
        sentiment_analysis_apended = append_sentiment_analysis_value(chat_history,sentiment_analysis)
        did_upload = await upload_chats_on_mongodb(patient_id, call_id, sentiment_analysis_apended)
        # print("History is: ",state_snapshot.values["messages"])
        if did_upload:
            return True
        else:
            return False
    except Exception as e:
        print("Error in get_chat_history function: ",str(e))
        return False
    


def parse_chat_history(messages):
    """
    Parses raw chat history into structured format with human/AI messages and token counts
    Returns list of dictionaries in chronological order

    INPUT:
        - Langchain message object.

    OUTPUT:
        - List in which every index is a dictionary and the dictionary contain:
                * human_message
                * ai_message": msg.content,
                * total_tokens
                * prompt_tokens
                * completion_tokens

    """
    parsed_chats = []
    current_human = None


    for msg in messages:
        # Check if it's a HumanMessage
        if type(msg).__name__ == "HumanMessage":
            current_human = msg.content
        
        # Check if it's an AIMessage
        elif type(msg).__name__ == "AIMessage":
            if current_human:
                # Extract token usage
                token_usage = msg.response_metadata.get("token_usage", {})
                
                parsed_chats.append({
                    "human_message": current_human,
                    "ai_message": msg.content,
                    "total_tokens": token_usage.get("total_tokens", 0),
                    "prompt_tokens": token_usage.get("prompt_tokens", 0),
                    "completion_tokens": token_usage.get("completion_tokens", 0)
                })
                current_human = None  
    print(parsed_chats)
    return parsed_chats


async def upload_chats_on_mongodb(patient_id, call_id, chats):
    print("Entered upload_chats_on_mongodb in after call ends.py")
    try:
        did_upload = await upload_on_mongodb(patient_id,call_id, chats)
        if(did_upload):
            print("Returned value: ",did_upload)
        else:
            return False
    except Exception as e:
        print("Error on after_call_ends.py : ",str(e))



def get_human_messages_out_of_call_chat(messages):
    return " ".join(message["human_message"] for message in messages)

    

