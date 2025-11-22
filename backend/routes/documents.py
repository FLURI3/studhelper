from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from jose import JWTError, jwt
import json
import os
from pathlib import Path
import uuid

router = APIRouter()

# Настройки JWT
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-123456789")
ALGORITHM = "HS256"

# Файл для сохранения документов
DOCUMENTS_FILE = Path("/app/data/documents.json")
DOCUMENTS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Загрузка документов из файла
def load_documents():
    if DOCUMENTS_FILE.exists():
        try:
            with open(DOCUMENTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

# Сохранение документов в файл
def save_documents(documents):
    with open(DOCUMENTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)

# Хранилище документов
documents_db = load_documents()

# Модели
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
    
# Получение текущего пользователя из токена
async def get_current_user_id(authorization: Optional[str] = Header(None)):
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

@router.post("/save")
async def save_document(doc: DocumentSave, user_id: str = Depends(get_current_user_id)):
    """
    Сохранить документ в облако пользователя
    """
    document = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": doc.title,
        "content": doc.content,
        "original_filename": doc.original_filename,
        "file_type": doc.file_type,
        "metadata": doc.metadata or {},
        "created_at": datetime.now().isoformat()
    }
    
    documents_db.append(document)
    save_documents(documents_db)
    
    return {"status": "saved", "document": document}

@router.get("/my")
async def get_my_documents(user_id: str = Depends(get_current_user_id)):
    """
    Получить все документы текущего пользователя
    """
    user_documents = [doc for doc in documents_db if doc.get("user_id") == user_id]
    # Сортируем по дате создания (новые первыми)
    user_documents.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"documents": user_documents}

@router.delete("/{document_id}")
async def delete_document(document_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Удалить документ из облака
    """
    global documents_db
    
    # Найти документ
    doc_index = None
    for i, doc in enumerate(documents_db):
        if doc.get("id") == document_id:
            if doc.get("user_id") != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to delete this document")
            doc_index = i
            break
    
    if doc_index is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Удалить документ
    deleted_doc = documents_db.pop(doc_index)
    save_documents(documents_db)
    
    return {"status": "deleted", "document": deleted_doc}

@router.get("/{document_id}")
async def get_document(document_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Получить конкретный документ
    """
    for doc in documents_db:
        if doc.get("id") == document_id:
            if doc.get("user_id") != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to access this document")
            return {"document": doc}
    
    raise HTTPException(status_code=404, detail="Document not found")
