from pydantic import BaseModel

class UptimeKuma(BaseModel):
    heartbeat: dict | None = None
    monitor: dict | None = None
    msg: str