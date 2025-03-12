import uuid

def append_sentiment_analysis_value(chats, sentiment_analysis_value):
    chats.append({"sentiment_analysis_value": sentiment_analysis_value})
    return chats



def generate_uuid():
    return str(uuid.uuid4())