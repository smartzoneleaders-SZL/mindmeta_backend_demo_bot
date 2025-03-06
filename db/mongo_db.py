import os
from urllib.parse import quote_plus
import motor.motor_asyncio
from dotenv import load_dotenv


load_dotenv()
username = "mindmeta"
password = "pakistan@1947"
encoded_password = quote_plus(password) 


db_name = os.getenv("DB_NAME")

# Now construct the URI with the encoded password:
MONGO_URI = f"mongodb+srv://{username}:{encoded_password}@mindmeta-mongo-db.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"

print(MONGO_URI)
print(db_name)

# Create the Motor client
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client[db_name]