# For textBlob
from textblob import TextBlob

# For logging
import logging
logger = logging.getLogger(__name__)

def check_sentiment_using_textblob(chat_history):
    """ Function checks the sentiment of the text given using textblob library"""
    try:
        text = " "
        for chat in chat_history:
            text=text + " "+ chat['user_query']

        # now lets do sentiment analysis
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except Exception as e:
        logger.exception(f"In services sentiment_analysis.py check_sentiment_using_textblob fucntion -> Error: {str(e)}")
        raise