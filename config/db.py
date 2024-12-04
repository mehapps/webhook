from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

print(getenv("ATLAS_URI"))
client = AsyncIOMotorClient(getenv("ATLAS_URI"))
db = client["Webhook"]
messages_collection = db["Messages"]
