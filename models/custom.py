from pydantic import BaseModel

class CustomData(BaseModel):
    message: str
    room_id: str | None = None