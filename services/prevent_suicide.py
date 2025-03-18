import openai
import os


client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
# Function to check messages for self-harm or harm intent
def detect_harmful_line(message):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": """You are a content moderation assistant. Your task is to analyze the given text "
                    "and return the **entire sentence** (with context) that indicates self-harm or intent to harm others. "
                    "If there is no concerning sentence, return 'None'."""},
            {"role": "user", "content": message}
        ]
    )

    extracted_line = response.choices[0].message.content.strip()

    if extracted_line.lower() != "none":
        return extracted_line  # Return only the concerning line
    return False


