from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv
from dotenv import load_dotenv

load_dotenv()

client = AsyncIOMotorClient(getenv("ATLAS_URI"))
db = client["Webhook"]
messages_collection = db["Messages"]
