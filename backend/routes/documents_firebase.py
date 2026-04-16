from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from jose import JWTError, jwt
import os

from services.firebase_service import firebase_service

router = APIRouter()

# Настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-123456789")
ALGORITHM = "HS256"

# ========================== MODELS ==========================

class DocumentSave(BaseModel):
    title: str
    content: str
    original_filename: Optional[str] = None
    file_type: Optional[str] = None  # 'parsed', 'shortened', 'analyzed'
    metadata: Optional[dict] = None
    
class Document(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    original_filename: Optional[str] = None
    file_type: Optional[str] = None
    metadata: Optional[dict] = None
    created_at: str

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    metadata: Optional[dict] = None

# ========================== UTILITIES ==========================

async def get_current_user_id(authorization: Optional[str] = Header(None)) -> str:
    """Получение текущего пользователя из токена"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# ========================== ROUTES ==========================

@router.post("/save")
async def save_document(doc: DocumentSave, user_id: str = Depends(get_current_user_id)):
    """
    Сохранить документ в Firebase
    """
    document = firebase_service.create_document(
        user_id=user_id,
        title=doc.title,
        content=doc.content,
        original_filename=doc.original_filename,
        file_type=doc.file_type,
        metadata=doc.metadata
    )
    
    return {"status": "saved", "document": document}

@router.get("/my")
async def get_my_documents(user_id: str = Depends(get_current_user_id)):
    """
    Получить все документы текущего пользователя
    """
    documents = firebase_service.get_user_documents(user_id)
    
    return {
        "count": len(documents),
        "documents": documents
    }

@router.get("/{document_id}")
async def get_document(document_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Получить конкретный документ
    """
    document = firebase_service.get_document(document_id, user_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found or access denied")
    
    return {"document": document}

@router.put("/{document_id}")
async def update_document(
    document_id: str,
    update_data: DocumentUpdate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Обновить документ
    """
    # Подготовка данных для обновления
    data_to_update = {}
    if update_data.title is not None:
        data_to_update["title"] = update_data.title
    if update_data.content is not None:
        data_to_update["content"] = update_data.content
    if update_data.metadata is not None:
        data_to_update["metadata"] = update_data.metadata
    
    success = firebase_service.update_document(document_id, user_id, data_to_update)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found or access denied")
    
    # Получить обновленный документ
    document = firebase_service.get_document(document_id, user_id)
    
    return {
        "status": "updated",
        "document": document
    }

@router.delete("/{document_id}")
async def delete_document(document_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Удалить документ из Firebase
    """
    success = firebase_service.delete_document(document_id, user_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Document not found or access denied")
    
    return {"status": "deleted"}

@router.get("/search/{query}")
async def search_documents(query: str, user_id: str = Depends(get_current_user_id)):
    """
    Поиск документов по названию или содержимому
    """
    documents = firebase_service.search_documents(user_id, query)
    
    return {
        "query": query,
        "count": len(documents),
        "documents": documents
    }
