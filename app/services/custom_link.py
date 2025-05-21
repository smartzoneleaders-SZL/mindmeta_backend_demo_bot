from cryptography.fernet import Fernet
from fastapi import HTTPException
import json
import base64
import os

cipher = Fernet(os.getenv('SECRET_KEY'))

def generate_token(name: str, email: str, phone_number: str):
    data = json.dumps({"name": name, "email": email, "phone_number": phone_number, "allow_access": True})
    encrypted = cipher.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()

# Function to decrypt data
def decode_token(token: str):
    try:
        encrypted = base64.urlsafe_b64decode(token)
        decrypted_data = cipher.decrypt(encrypted).decode()
        return json.loads(decrypted_data)
    except (ValueError, TypeError, json.JSONDecodeError) as e:
        print(f"Decoding failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid token: {e}")

