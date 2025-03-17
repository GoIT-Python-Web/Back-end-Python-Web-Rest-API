from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from fastapi.responses import JSONResponse

# 🔥 Загружаем .env и проверяем, есть ли SECRET_KEY
load_dotenv(dotenv_path=".env")
SECRET_KEY = os.getenv("SECRET_KEY") or "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 360

# 🔐 Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 📌 Поддержка OAuth2 Bearer Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

def verify_password(plain_password, hashed_password):
    """ Проверяет, совпадает ли пароль с хешем """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """ Хеширует пароль """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """ Создает JWT-токен """
    try:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return token
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Failed to generate token", "details": str(e)})

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """ Декодирует JWT и получает текущего пользователя """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return JSONResponse(status_code=401, content={"error": "Invalid token", "message": "Token missing or incorrect"})
    
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            return JSONResponse(status_code=401, content={"error": "User not found", "message": "Token is valid but user does not exist"})
        
        return user
    except JWTError as e:
        return JSONResponse(status_code=401, content={"error": "Could not validate credentials", "details": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": "Unexpected error", "details": str(e)})


