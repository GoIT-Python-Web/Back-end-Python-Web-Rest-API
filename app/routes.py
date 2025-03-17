import asyncio
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
from app.database import get_db
from app.models import User, Contact
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.schemas import (
    UserCreate, UserResponse, UserRegisterResponse, LoginRequest, LoginResponse, 
    ContactCreate, ContactResponse
)
from typing import List

router = APIRouter()

async def run_in_threadpool(func, *args, **kwargs):
    return await asyncio.to_thread(func, *args, **kwargs)


@router.post("/register/", response_model=UserRegisterResponse, status_code=201)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = await run_in_threadpool(lambda: db.query(User).filter(User.email == user.email).first())
    if existing_user:
        raise HTTPException(status_code=400, detail="This User already exists. Go to Login page.")

    hashed_password = get_password_hash(user.password)

    new_user = User(
        id=uuid4(),
        username=user.username,
        email=user.email,
        password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name
    )

    db.add(new_user)
    await run_in_threadpool(db.commit)
    await run_in_threadpool(db.refresh, new_user)

    access_token = create_access_token({"user_id": str(new_user.id)})

    return UserRegisterResponse(
        message="User registered successfully.",
        user=new_user,
        access_token=access_token
    )


@router.post("/login/", response_model=LoginResponse)
async def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    user = await run_in_threadpool(lambda: db.query(User).filter(User.email == user_data.email).first())

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    access_token = create_access_token({"sub": str(user.id)})
    return LoginResponse(access_token=access_token)


@router.get("/users/me/", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/contacts/", response_model=ContactResponse)
async def create_contact(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_contact = Contact(
        id=uuid4(),
        user_id=current_user.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        phone=contact.phone,
        birthdate=contact.birthdate,
        description=contact.description
    )

    db.add(new_contact)
    await run_in_threadpool(db.commit)
    await run_in_threadpool(db.refresh, new_contact)
    return new_contact


@router.get("/contacts/", response_model=List[ContactResponse])
async def get_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contacts = await run_in_threadpool(lambda: db.query(Contact).filter(Contact.user_id == current_user.id).all())
    return contacts


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = await run_in_threadpool(lambda: db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first())

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    return contact


@router.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    updated_contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = await run_in_threadpool(lambda: db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first())

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    contact.first_name = updated_contact.first_name
    contact.last_name = updated_contact.last_name
    contact.phone = updated_contact.phone
    contact.birthdate = updated_contact.birthdate
    contact.description = updated_contact.description

    await run_in_threadpool(db.commit)
    await run_in_threadpool(db.refresh, contact)
    return contact


@router.delete("/contacts/{contact_id}")
async def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = await run_in_threadpool(lambda: db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first())

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    await run_in_threadpool(db.delete, contact)
    await run_in_threadpool(db.commit)
    return {"message": "Contact deleted successfully"}
