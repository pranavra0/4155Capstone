from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Node(BaseModel):
    id: str
    ip: str
    port: int
    cpu: int
    memory: int
    status: str = Field(default="unknown", description="online/offline/unknown")
    last_seen: Optional[datetime] = None
    cpu_percent: Optional[float] = None
    memory_percent: Optional[float] = None

class Container(BaseModel):
    id: str
    image: str
    status: str

class Job(BaseModel):
    id: str
    image: str
    status: str