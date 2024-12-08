from pydantic import BaseModel

class BluebubblesData(BaseModel):
    type: str
    data: dict