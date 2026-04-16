import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Optional
from datetime import datetime
import os
import json
from pathlib import Path

class FirebaseService:
    """Сервис для работы с Firebase Firestore"""
    
    _instance = None
    _db = None
    
    def __new__(cls):
        """Singleton паттерн"""
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Инициализация Firebase сервиса"""
        if self._db is not None:
            return
        
        # Инициализируем Firebase только если не был инициализирован
        if not firebase_admin._apps:
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "/app/config/firebase-credentials.json")
            
            # Если переменная окружения содержит JSON строку, сохраняем её в файл
            cred_json = os.getenv("FIREBASE_CREDENTIALS_JSON")
            if cred_json:
                cred_path = "/tmp/firebase-cred.json"
                with open(cred_path, 'w') as f:
                    f.write(cred_json)
            
            if not os.path.exists(cred_path):
                raise FileNotFoundError(f"Firebase credentials not found at {cred_path}")
            
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
        
        self._db = firestore.client()
    
    @property
    def db(self):
        """Получить клиент Firestore"""
        return self._db
    
    # ========================== USERS ==========================
    
    def create_user(self, username: str, email: str, hashed_password: str, 
                   full_name: Optional[str] = None, group: Optional[str] = None,
                   subgroup: Optional[int] = None) -> Dict:
        """Создать пользователя"""
        user_data = {
            "username": username,
            "email": email,
            "hashed_password": hashed_password,
            "full_name": full_name or "",
            "group": group or "",
            "subgroup": subgroup or 0,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Использу username как ID для быстрого поиска
        self._db.collection("users").document(username).set(user_data)
        return user_data
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Получить пользователя по username"""
        doc = self._db.collection("users").document(username).get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Получить пользователя по email"""
        docs = self._db.collection("users").where("email", "==", email).stream()
        for doc in docs:
            return doc.to_dict()
        return None
    
    def update_user(self, username: str, data: Dict) -> bool:
        """Обновить данные пользователя"""
        data["updated_at"] = datetime.now()
        self._db.collection("users").document(username).update(data)
        return True
    
    def delete_user(self, username: str) -> bool:
        """Удалить пользователя"""
        self._db.collection("users").document(username).delete()
        return True
    
    def user_exists(self, username: str) -> bool:
        """Проверить существование пользователя"""
        doc = self._db.collection("users").document(username).get()
        return doc.exists
    
    # ========================== DOCUMENTS ==========================
    
    def create_document(self, user_id: str, title: str, content: str,
                       original_filename: Optional[str] = None,
                       file_type: Optional[str] = None,
                       metadata: Optional[dict] = None) -> Dict:
        """Создать документ"""
        doc_data = {
            "user_id": user_id,
            "title": title,
            "content": content,
            "original_filename": original_filename or "",
            "file_type": file_type or "",
            "metadata": metadata or {},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Автоматический ID документа
        doc_ref = self._db.collection("documents").document()
        doc_ref.set(doc_data)
        
        # Добавить ID в массив документов пользователя (для быстрого поиска)
        self._add_document_to_user_index(user_id, doc_ref.id)
        
        return {"id": doc_ref.id, **doc_data}
    
    def get_document(self, document_id: str, user_id: str) -> Optional[Dict]:
        """Получить документ (с проверкой прав доступа)"""
        doc = self._db.collection("documents").document(document_id).get()
        if doc.exists:
            data = doc.to_dict()
            # Проверка: владелец ли пользователь
            if data.get("user_id") == user_id:
                return {"id": document_id, **data}
        return None
    
    def get_user_documents(self, user_id: str, limit: int = 100) -> List[Dict]:
        """Получить все документы пользователя (отсортированы по дате)"""
        docs = (self._db.collection("documents")
                .where("user_id", "==", user_id)
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .limit(limit)
                .stream())
        
        result = []
        for doc in docs:
            result.append({"id": doc.id, **doc.to_dict()})
        return result
    
    def update_document(self, document_id: str, user_id: str, data: Dict) -> bool:
        """Обновить документ"""
        # Проверка прав доступа
        doc = self._db.collection("documents").document(document_id).get()
        if not doc.exists or doc.to_dict().get("user_id") != user_id:
            return False
        
        data["updated_at"] = datetime.now()
        self._db.collection("documents").document(document_id).update(data)
        return True
    
    def delete_document(self, document_id: str, user_id: str) -> bool:
        """Удалить документ"""
        # Проверка прав доступа
        doc = self._db.collection("documents").document(document_id).get()
        if not doc.exists or doc.to_dict().get("user_id") != user_id:
            return False
        
        self._db.collection("documents").document(document_id).delete()
        self._remove_document_from_user_index(user_id, document_id)
        return True
    
    def search_documents(self, user_id: str, query: str) -> List[Dict]:
        """Поиск документов по названию или содержимому"""
        # Примечание: Full-text search требует индексов Firestore
        docs = (self._db.collection("documents")
                .where("user_id", "==", user_id)
                .stream())
        
        result = []
        query_lower = query.lower()
        for doc in docs:
            data = doc.to_dict()
            if (query_lower in data.get("title", "").lower() or 
                query_lower in data.get("content", "").lower()):
                result.append({"id": doc.id, **data})
        
        return result
    
    # ========================== UTILITY ==========================
    
    def _add_document_to_user_index(self, user_id: str, document_id: str):
        """Добавить документ в индекс пользователя"""
        index_ref = self._db.collection("user_documents_index").document(user_id)
        index_ref.set(
            {"document_ids": firestore.ArrayUnion([document_id])},
            merge=True
        )
    
    def _remove_document_from_user_index(self, user_id: str, document_id: str):
        """Удалить документ из индекса пользователя"""
        index_ref = self._db.collection("user_documents_index").document(user_id)
        index_ref.set(
            {"document_ids": firestore.ArrayRemove([document_id])},
            merge=True
        )
    
    def clear_all_data(self):
        """Очистить всю базу (только для разработки!)"""
        # Удалить все документы
        docs = self._db.collection("documents").stream()
        for doc in docs:
            doc.reference.delete()
        
        # Удалить всех пользователей
        users = self._db.collection("users").stream()
        for user in users:
            user.reference.delete()
        
        # Удалить индексы
        indexes = self._db.collection("user_documents_index").stream()
        for index in indexes:
            index.reference.delete()
    
    def export_all_data(self) -> Dict:
        """Экспортировать всю базу в JSON"""
        result = {
            "users": {},
            "documents": [],
            "exported_at": datetime.now().isoformat()
        }
        
        # Экспортировать пользователей
        users = self._db.collection("users").stream()
        for user in users:
            result["users"][user.id] = user.to_dict()
        
        # Экспортировать документы
        docs = self._db.collection("documents").stream()
        for doc in docs:
            data = doc.to_dict()
            data["created_at"] = data.get("created_at").isoformat() if data.get("created_at") else None
            data["updated_at"] = data.get("updated_at").isoformat() if data.get("updated_at") else None
            result["documents"].append({"id": doc.id, **data})
        
        return result


# Глобальный экземпляр
firebase_service = FirebaseService()
