from pydantic import BaseModel

class SonarrData(BaseModel):
    class Config:
        extra = 'allow'
        
class JellyseerrData(BaseModel):
    notification_type: str
    event: str
    subject: str
    message: str
    media: dict | None = None
    request: dict | None = None
    issue: dict | None = None
    comment: dict | None = None
    
class RadarrData(BaseModel):
    movie: dict
    remoteMovie: dict
    release: dict
    eventType: str
    
    class Config:
        extra = 'allow'
        
class ProwlarrData(BaseModel):
    level: str
    message: str
    type: str
    wikiUrl: str
    eventType: str
    instanceName: str
    applicationUrl: str | None = None