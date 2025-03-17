from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4, UUID
from typing import List

from app.database import get_db
from app.models import User, Contact
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.schemas import (
    UserCreate, UserResponse, UserRegisterResponse, LoginRequest, LoginResponse, 
    ContactCreate, ContactResponse
)

router = APIRouter()


@router.post("/register/", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED, response_model_exclude_unset=True)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This User already exists. Go to Login page.")

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
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token({"user_id": str(new_user.id)})

    return UserRegisterResponse(
        message="User registered successfully.",
        user=UserResponse.model_validate(new_user),
        access_token=access_token
    )


@router.post("/login/", response_model=LoginResponse)
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token({"sub": str(user.id)})
    return LoginResponse(access_token=access_token)


@router.get("/users/me/", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post("/contacts/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED, response_model_exclude_unset=True)
def create_contact(
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
    db.commit()
    db.refresh(new_contact)

    return ContactResponse.model_validate(new_contact)


@router.get("/contacts/", response_model=List[ContactResponse])
def get_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contacts = db.query(Contact).filter(Contact.user_id == current_user.id).all()
    return [ContactResponse.model_validate(contact) for contact in contacts]


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    
    return ContactResponse.model_validate(contact)


@router.put("/contacts/{contact_id}", response_model=ContactResponse, response_model_exclude_unset=True)
def update_contact(
    contact_id: UUID,
    updated_contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    contact.first_name = updated_contact.first_name
    contact.last_name = updated_contact.last_name
    contact.phone = updated_contact.phone
    contact.birthdate = updated_contact.birthdate
    contact.description = updated_contact.description

    db.commit()
    db.refresh(contact)

    return ContactResponse.model_validate(contact)


@router.delete("/contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()

    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    db.delete(contact)
    db.commit()
