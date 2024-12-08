from pydantic import BaseModel

class MessageData(BaseModel):
    guid: str
    text: str | None = None
    dateCreated: int | None = None
    dateEdited: int | None = None
    isFromMe: bool
    handle: dict

class BluebubblesData(BaseModel):
    type: str
    data: MessageData