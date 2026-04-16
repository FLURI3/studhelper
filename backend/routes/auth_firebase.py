from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import os

from services.firebase_service import firebase_service

router = APIRouter()

# Настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-123456789")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней

# ========================== MODELS ==========================

class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    group: Optional[str] = None
    subgroup: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "securepass123",
                "full_name": "John Doe",
                "group": "ИВБО-01-21",
                "subgroup": 1
            }
        }

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class User(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None
    group: Optional[str] = None
    subgroup: Optional[int] = None

# ========================== UTILITIES ==========================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Хеширование пароля с использованием bcrypt"""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Получить текущего пользователя из токена"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ========================== ROUTES ==========================

@router.post("/auth/register", response_model=Token)
def register(user_data: UserRegister):
    """
    Регистрация нового пользователя
    """
    # Проверка существования username
    if firebase_service.user_exists(user_data.username):
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    
    # Проверка существования email
    if firebase_service.get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    # Хеширование пароля
    hashed_password = get_password_hash(user_data.password)
    
    # Сохранение пользователя в Firebase
    firebase_service.create_user(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        group=user_data.group,
        subgroup=user_data.subgroup
    )
    
    # Создание токена
    access_token = create_access_token(data={"sub": user_data.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user_data.email,
            "username": user_data.username,
            "full_name": user_data.full_name,
            "group": user_data.group,
            "subgroup": user_data.subgroup
        }
    }

@router.post("/auth/login", response_model=Token)
def login(user_data: UserLogin):
    """
    Вход в систему
    """
    # Получение пользователя из Firebase
    user = firebase_service.get_user(user_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    
    # Проверка пароля
    if not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Неверное имя пользователя или пароль")
    
    # Создание токена
    access_token = create_access_token(data={"sub": user_data.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user["email"],
            "username": user["username"],
            "full_name": user.get("full_name"),
            "group": user.get("group"),
            "subgroup": user.get("subgroup")
        }
    }

@router.get("/auth/me")
def get_current_user(username: str = Depends(get_current_user_id)):
    """
    Получить текущего пользователя по токену
    """
    user = firebase_service.get_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    return {
        "email": user["email"],
        "username": username,
        "full_name": user.get("full_name"),
        "group": user.get("group"),
        "subgroup": user.get("subgroup")
    }

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    group: Optional[str] = None
    subgroup: Optional[int] = None

@router.put("/auth/profile")
def update_profile(user_update: UserUpdate, username: str = Depends(get_current_user_id)):
    """
    Обновить профиль пользователя
    """
    user = firebase_service.get_user(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    # Подготовка данных для обновления
    update_data = {}
    if user_update.full_name is not None:
        update_data["full_name"] = user_update.full_name
    if user_update.group is not None:
        update_data["group"] = user_update.group
    if user_update.subgroup is not None:
        update_data["subgroup"] = user_update.subgroup
    
    # Обновление в Firebase
    if update_data:
        firebase_service.update_user(username, update_data)
    
    # Получение обновленного пользователя
    updated_user = firebase_service.get_user(username)
    
    return {
        "email": updated_user["email"],
        "username": username,
        "full_name": updated_user.get("full_name"),
        "group": updated_user.get("group"),
        "subgroup": updated_user.get("subgroup")
    }
