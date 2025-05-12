import os
from openai import OpenAI
from fastapi import HTTPException

# Initialize OpenAI client
client_text = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), base_url="https://api.openai.com/v1")

# Function to check messages for self-harm or harm intent
def detect_harmful_line(message):
    try:
        print("API Key in use: ", os.getenv('OPENAI_API_KEY'))
        response = client_text.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": """You are a content moderation assistant. Your task is to analyze the given text 
                    and return the **entire sentence** (with context) that indicates self-harm or intent to harm others. 
                    If there is no concerning sentence, return 'None'."""},
                {"role": "user", "content": message}
            ]
        )

        extracted_line = response.choices[0].message.content.strip()

        if extracted_line.lower() != "none":
            return extracted_line  # Return the concerning sentence
        return False
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error using OpenAI for response")