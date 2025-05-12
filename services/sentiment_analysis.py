# For textBlob
from textblob import TextBlob

# For logging
import logging
logger = logging.getLogger(__name__)

def check_sentiment_using_textblob(text):
    """ Function checks the sentiment of the text given using textblob library"""
    try:
        blob = TextBlob(text)
        return blob.sentiment.polarity
    except Exception as e:
        logger.exception(f"In services sentiment_analysis.py check_sentiment_using_textblob fucntion -> Error: {str(e)}")
        raise