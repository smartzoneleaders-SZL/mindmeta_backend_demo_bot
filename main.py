from fastapi import FastAPI


# For middleware
from fastapi.middleware.cors import CORSMiddleware

import logging
import uvicorn

# For routes
from routes import call, demo_bot, analytics, auth, allow_access, cold_call









# For azure logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()  # For stdout, which Azure captures
    ]
)


logger = logging.getLogger(__name__)





app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)









@app.get("/")
def check_me():
    return {"message":"Done"}




app.include_router(call.router, prefix="/api/call", tags=["Talk to Bot"])
app.include_router(demo_bot.router, prefix="/api/demo-bot-call", tags=["Talk to Demo Bot"])



app.include_router(auth.router, prefix="/api/auth", tags=["AUTH"])
app.include_router(allow_access.router, prefix="/api/allow-access", tags=["Allow Access"])

app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(cold_call.router, prefix="/api/cold-call", tags=["Cold Call Script"])




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

