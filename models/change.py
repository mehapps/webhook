from pydantic import BaseModel

class ChangeData(BaseModel):
    message: str