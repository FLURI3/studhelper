from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
import os
import json
from pathlib import Path

router = APIRouter()

# Настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-123456789")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней

# Файл для сохранения пользователей
USERS_FILE = Path("/app/data/users.json")
USERS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Загрузка пользователей из файла
def load_users():
    if USERS_FILE.exists():
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

# Сохранение пользователей в файл
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# Хранилище пользователей с persistence
users_db = load_users()

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

def verify_password(plain_password, hashed_password):
    """Проверка пароля"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password):
    """Хеширование пароля с использованием bcrypt"""
    # Bcrypt имеет ограничение в 72 байта
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/auth/register", response_model=Token)
def register(user_data: UserRegister):
    """
    Регистрация нового пользователя
    """
    # Проверка существования email
    if user_data.email in [u.get("email") for u in users_db.values()]:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")
    
    # Проверка существования username
    if user_data.username in users_db:
        raise HTTPException(status_code=400, detail="Имя пользователя уже занято")
    
    # Хеширование пароля
    hashed_password = get_password_hash(user_data.password)
    
    # Сохранение пользователя
    user = {
        "email": user_data.email,
        "username": user_data.username,
        "full_name": user_data.full_name,
        "group": user_data.group,
        "subgroup": user_data.subgroup,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow().isoformat()
    }
    users_db[user_data.username] = user
    save_users(users_db)  # Сохраняем в файл
    
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
    # Проверка существования пользователя
    user = users_db.get(user_data.username)
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
def get_current_user(token: str):
    """
    Получить текущего пользователя по токену
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Недействительный токен")
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    
    user = users_db.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    return {
        "email": user["email"],
        "username": user["username"],
        "full_name": user.get("full_name"),
        "group": user.get("group"),
        "subgroup": user.get("subgroup")
    }

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    group: Optional[str] = None
    subgroup: Optional[int] = None

@router.put("/auth/profile")
def update_profile(user_update: UserUpdate, token: str):
    """
    Обновить профиль пользователя (группа и подгруппа)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Недействительный токен")
    except JWTError:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    
    user = users_db.get(username)
    if user is None:
        raise HTTPException(status_code=401, detail="Пользователь не найден")
    
    # Обновление полей
    if user_update.full_name is not None:
        user["full_name"] = user_update.full_name
    if user_update.group is not None:
        user["group"] = user_update.group
    if user_update.subgroup is not None:
        user["subgroup"] = user_update.subgroup
    
    users_db[username] = user
    save_users(users_db)  # Сохраняем в файл
    
    return {
        "email": user["email"],
        "username": user["username"],
        "full_name": user.get("full_name"),
        "group": user.get("group"),
        "subgroup": user.get("subgroup")
    }
