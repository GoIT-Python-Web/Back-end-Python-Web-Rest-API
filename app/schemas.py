from pydantic import BaseModel
from uuid import UUID

class UserResponse(BaseModel):
    id: str 
    username: str
    email: str
    first_name: str | None
    last_name: str | None

    class Config:
        from_attributes = True
