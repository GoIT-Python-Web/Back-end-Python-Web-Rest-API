from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]

    class Config:
        from_attributes = True


class UserRegisterResponse(BaseModel):
    message: str
    user: UserResponse
    # access_token: str

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    birthdate: str
    description: Optional[str] = None


class ContactResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    phone: str
    birthdate: datetime
    description: Optional[str]

    class Config:
        from_attributes = True


class ContactSearchResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    phone: str
    email: str
    birthdate: datetime

    class Config:
        from_attributes = True


class UpcomingBirthdayResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    birthdate: datetime

    class Config:
        from_attributes = True


class PhotoUploadResponse(BaseModel):
    message: str
    photo_url: str
    public_id: str

    class Config:
        from_attributes = True
