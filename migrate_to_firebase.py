#!/usr/bin/env python3
"""
Скрипт миграции данных из JSON в Firebase Firestore
Использование: python migrate_to_firebase.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Добавляем backend в path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.firebase_service import firebase_service

def migrate_users(users_file: Path = None) -> int:
    """
    Миграция пользователей из JSON в Firebase
    
    Args:
        users_file: Путь к файлу users.json
        
    Returns:
        Количество успешно мигрированных пользователей
    """
    if users_file is None:
        users_file = Path(__file__).parent / "backend" / "data" / "users.json"
    
    if not users_file.exists():
        print(f"❌ Файл users.json не найден: {users_file}")
        return 0
    
    try:
        with open(users_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка при чтении JSON: {e}")
        return 0
    
    migrated_count = 0
    
    print(f"\n📦 Начало миграции пользователей ({len(users)} пользователей)...")
    
    for username, user_data in users.items():
        try:
            # Проверка существования
            if firebase_service.user_exists(username):
                print(f"⚠️  Пользователь '{username}' уже существует в Firebase, пропускаю")
                continue
            
            firebase_service.create_user(
                username=username,
                email=user_data.get("email", f"{username}@example.com"),
                hashed_password=user_data.get("hashed_password", ""),
                full_name=user_data.get("full_name", ""),
                group=user_data.get("group", ""),
                subgroup=user_data.get("subgroup", 0)
            )
            print(f"✅ Пользователь '{username}' успешно мигрирован")
            migrated_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка при миграции пользователя '{username}': {e}")
    
    return migrated_count

def migrate_documents(docs_file: Path = None) -> int:
    """
    Миграция документов из JSON в Firebase
    
    Args:
        docs_file: Путь к файлу documents.json
        
    Returns:
        Количество успешно мигрированных документов
    """
    if docs_file is None:
        docs_file = Path(__file__).parent / "backend" / "data" / "documents.json"
    
    if not docs_file.exists():
        print(f"❌ Файл documents.json не найден: {docs_file}")
        return 0
    
    try:
        with open(docs_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка при чтении JSON: {e}")
        return 0
    
    migrated_count = 0
    
    print(f"\n📄 Начало миграции документов ({len(documents)} документов)...")
    
    for doc_data in documents:
        try:
            # Проверка обязательных полей
            if not doc_data.get("user_id"):
                print(f"⚠️  Документ без user_id пропущен: {doc_data.get('title', 'Unknown')}")
                continue
            
            # Проверка существования пользователя в Firebase
            if not firebase_service.user_exists(doc_data.get("user_id")):
                print(f"⚠️  Документ пропущен (пользователь не найден): {doc_data.get('title', 'Unknown')}")
                continue
            
            doc = firebase_service.create_document(
                user_id=doc_data.get("user_id"),
                title=doc_data.get("title", "Untitled"),
                content=doc_data.get("content", ""),
                original_filename=doc_data.get("original_filename"),
                file_type=doc_data.get("file_type"),
                metadata=doc_data.get("metadata", {})
            )
            
            print(f"✅ Документ '{doc.get('title')}' успешно мигрирован (ID: {doc.get('id')})")
            migrated_count += 1
            
        except Exception as e:
            print(f"❌ Ошибка при миграции документа: {e}")
    
    return migrated_count

def main():
    """Главная функция"""
    print("=" * 60)
    print("🚀 Миграция данных в Firebase Firestore")
    print("=" * 60)
    
    try:
        # Миграция пользователей
        users_migrated = migrate_users()
        
        # Миграция документов
        docs_migrated = migrate_documents()
        
        # Итоги
        print("\n" + "=" * 60)
        print("📊 Результаты миграции:")
        print(f"   ✅ Пользователи: {users_migrated}")
        print(f"   ✅ Документы: {docs_migrated}")
        print("=" * 60)
        
        if users_migrated > 0 or docs_migrated > 0:
            print("\n✅ Миграция успешно завершена!")
            return 0
        else:
            print("\n⚠️  Не было мигрировано ни одного записей. Проверьте исходные файлы.")
            return 1
    
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
