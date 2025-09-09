from pydantic import BaseModel

class Node(BaseModel):
    id: str
    cpu: int
    memory: int

class Container(BaseModel):
    id: str
    image: str
    status: str

class Job(BaseModel):
    id: str
    image: str
    status: str