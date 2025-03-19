from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4, UUID
from typing import List
from datetime import datetime, timedelta
from sqlalchemy.sql import select, func

from app.database import get_db
from app.models import User, Contact
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.schemas import (
    UserCreate, UserResponse, UserRegisterResponse, LoginRequest, LoginResponse, 
    ContactCreate, ContactResponse, ContactSearchResponse, UpcomingBirthdayResponse
)

router = APIRouter()

def parse_date(date_str: str) -> datetime:
    formats = ["%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Неверный формат даты: {date_str}")


@router.post("/register/", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED, response_model_exclude_unset=True)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where((User.email == user.email) | (User.username == user.username)))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This User already exists. Go to Login page.")

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
    await db.commit()
    await db.refresh(new_user)

    return UserRegisterResponse(
        message="User registered successfully.",
        user=UserResponse.model_validate(new_user)
    )


@router.post("/login/", response_model=LoginResponse)
async def login(user_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == user_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token({"sub": str(user.id)})
    return LoginResponse(access_token=access_token)


@router.post("/contacts/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, response_model_exclude_unset=True)
async def create_contact(
    contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_contact = Contact(
        id=uuid4(),
        user_id=current_user.id,
        first_name=contact.first_name,
        last_name=contact.last_name,
        email=contact.email,
        phone=contact.phone,
        birthdate=parse_date(contact.birthdate),
        description=contact.description
    )

    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact)

    return ContactResponse.model_validate(new_contact)


@router.get("/users/me/", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.get("/contacts/", response_model=List[ContactResponse])
async def get_contacts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Contact).where(Contact.user_id == current_user.id))
    contacts = result.scalars().all()
    return [ContactResponse.model_validate(contact) for contact in contacts]


@router.get("/contacts/search", response_model=List[ContactSearchResponse])
async def search_contacts(query: str, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Contact).where(
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.phone.ilike(f"%{query}%"))
        )
    )
    contacts = result.scalars().all()
    return [ContactSearchResponse.model_validate(contact) for contact in contacts]


@router.get("/contacts/birthdays", response_model=List[UpcomingBirthdayResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = datetime.today().date()
    next_week = today + timedelta(days=7)

    result = await db.execute(
        select(Contact).where(
            func.date(Contact.birthdate) >= today,
            func.date(Contact.birthdate) <= next_week
        )
    )
    contacts = result.scalars().all()
    return [UpcomingBirthdayResponse.model_validate(contact) for contact in contacts]


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Contact).where(Contact.id == contact_id, Contact.user_id == current_user.id))
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    return ContactResponse.model_validate(contact)


@router.put("/contacts/{contact_id}", response_model=ContactResponse, response_model_exclude_unset=True)
async def update_contact(
    contact_id: UUID,
    updated_contact: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Contact).where(Contact.id == contact_id, Contact.user_id == current_user.id))
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    contact.first_name = updated_contact.first_name
    contact.last_name = updated_contact.last_name
    contact.phone = updated_contact.phone
    contact.birthdate = updated_contact.birthdate
    contact.description = updated_contact.description

    await db.commit()
    await db.refresh(contact)

    return ContactResponse.model_validate(contact)


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Contact).where(Contact.id == contact_id, Contact.user_id == current_user.id))
    contact = result.scalar_one_or_none()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    await db.delete(contact)
    await db.commit()
