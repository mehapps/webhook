from pydantic import BaseModel

class Handle(BaseModel):
    originalROWID: int
    address: str
    service: str
    uncanonicalizedId: str
    country: str
    class Config:
        extra = 'allow'
    
class Data(BaseModel):
    guid: str
    text: str | None = None
    dateCreated: int | None = None
    dateEdited: int | None = None
    isFromMe: bool
    handle: Handle
    class Config:
        extra = 'allow'

class BluebubblesData(BaseModel):
    type: str
    data: Data
    class Config:
        extra = 'allow'