"""
Firebase Firestore API Examples
Примеры использования firebase_service в приложении
"""

from services.firebase_service import firebase_service
from routes.auth import get_password_hash
from datetime import datetime

# ========================== ПРИМЕР 1: РАБОТА С ПОЛЬЗОВАТЕЛЯМИ ==========================

def example_user_operations():
    """Примеры операций с пользователями"""
    
    print("=== USERS OPERATIONS ===\n")
    
    # Создание пользователя
    print("1. Создание пользователя...")
    user_data = firebase_service.create_user(
        username="john_doe",
        email="john@example.com",
        hashed_password=get_password_hash("securepass123"),
        full_name="John Doe",
        group="ИВБО-01-21",
        subgroup=1
    )
    print(f"✅ Пользователь создан: {user_data}\n")
    
    # Получение пользователя по username
    print("2. Получение пользователя по username...")
    user = firebase_service.get_user("john_doe")
    print(f"✅ Найден: {user['email']}\n")
    
    # Получение пользователя по email
    print("3. Получение пользователя по email...")
    user = firebase_service.get_user_by_email("john@example.com")
    print(f"✅ Найден: {user['username']}\n")
    
    # Проверка существования пользователя
    print("4. Проверка существования пользователя...")
    exists = firebase_service.user_exists("john_doe")
    print(f"✅ john_doe существует: {exists}\n")
    
    # Обновление пользователя
    print("5. Обновление профиля пользователя...")
    firebase_service.update_user("john_doe", {
        "full_name": "John Updated Doe",
        "group": "ИВБО-02-21"
    })
    updated_user = firebase_service.get_user("john_doe")
    print(f"✅ Обновлено: {updated_user['full_name']}\n")
    
    # Удаление пользователя
    print("6. Удаление пользователя...")
    firebase_service.delete_user("john_doe")
    user = firebase_service.get_user("john_doe")
    print(f"✅ Пользователь удален: {user is None}\n")


# ========================== ПРИМЕР 2: РАБОТА С ДОКУМЕНТАМИ ==========================

def example_document_operations():
    """Примеры операций с документами"""
    
    print("=== DOCUMENTS OPERATIONS ===\n")
    
    # Сначала создаем пользователя
    user_id = "alice_smith"
    firebase_service.create_user(
        username=user_id,
        email="alice@example.com",
        hashed_password="hash",
        full_name="Alice Smith"
    )
    
    # Создание документа
    print("1. Создание документа...")
    doc = firebase_service.create_document(
        user_id=user_id,
        title="My First Document",
        content="This is the content of my document...",
        original_filename="document.pdf",
        file_type="parsed",
        metadata={"pages": 10, "language": "en"}
    )
    doc_id = doc["id"]
    print(f"✅ Документ создан: ID={doc_id}\n")
    
    # Получение документа
    print("2. Получение документа...")
    doc = firebase_service.get_document(doc_id, user_id)
    print(f"✅ Документ: {doc['title']}\n")
    
    # Получение всех документов пользователя
    print("3. Получение всех документов пользователя...")
    docs = firebase_service.get_user_documents(user_id)
    print(f"✅ Всего документов: {len(docs)}\n")
    
    # Создание еще несколько документов для примера
    for i in range(2, 4):
        firebase_service.create_document(
            user_id=user_id,
            title=f"Document #{i}",
            content=f"Content of document {i}...",
            file_type="parsed"
        )
    
    # Получение документов с лимитом
    print("4. Получение последних 2 документов...")
    recent_docs = firebase_service.get_user_documents(user_id, limit=2)
    print(f"✅ Последних документов: {len(recent_docs)}\n")
    
    # Обновление документа
    print("5. Обновление документа...")
    firebase_service.update_document(doc_id, user_id, {
        "title": "Updated Document Title",
        "content": "Updated content..."
    })
    updated_doc = firebase_service.get_document(doc_id, user_id)
    print(f"✅ Обновлено: {updated_doc['title']}\n")
    
    # Поиск документов
    print("6. Поиск документов...")
    search_results = firebase_service.search_documents(user_id, "Document")
    print(f"✅ Найдено документов: {len(search_results)}\n")
    
    # Удаление документа
    print("7. Удаление документа...")
    firebase_service.delete_document(doc_id, user_id)
    doc = firebase_service.get_document(doc_id, user_id)
    print(f"✅ Документ удален: {doc is None}\n")


# ========================== ПРИМЕР 3: БЕЗОПАСНОСТЬ (ПРОВЕРКА ПРАВ) ==========================

def example_security_checks():
    """Примеры проверок безопасности"""
    
    print("=== SECURITY EXAMPLES ===\n")
    
    # Создание двух пользователей
    user1 = "user_alice"
    user2 = "user_bob"
    
    firebase_service.create_user(
        username=user1,
        email="alice@example.com",
        hashed_password="hash"
    )
    firebase_service.create_user(
        username=user2,
        email="bob@example.com",
        hashed_password="hash"
    )
    
    # Alice создает документ
    print("1. Alice создает документ...")
    doc = firebase_service.create_document(
        user_id=user1,
        title="Alice's Secret Document",
        content="This is private..."
    )
    doc_id = doc["id"]
    print(f"✅ Документ создан: {doc_id}\n")
    
    # Alice может получить свой документ
    print("2. Alice получает свой документ...")
    doc = firebase_service.get_document(doc_id, user1)
    print(f"✅ Успешно: {doc is not None}\n")
    
    # Bob НЕ может получить чужой документ
    print("3. Bob пытается получить документ Alice...")
    doc = firebase_service.get_document(doc_id, user2)
    print(f"✅ Доступ запрещен: {doc is None}\n")
    
    # Bob НЕ может удалить чужой документ
    print("4. Bob пытается удалить документ Alice...")
    success = firebase_service.delete_document(doc_id, user2)
    print(f"✅ Удаление не удалось: {not success}\n")
    
    # Alice может удалить свой документ
    print("5. Alice удаляет свой документ...")
    success = firebase_service.delete_document(doc_id, user1)
    print(f"✅ Удаление успешно: {success}\n")


# ========================== ПРИМЕР 4: ЭКСПОРТ ДАННЫХ ==========================

def example_export_import():
    """Примеры экспорта и импорта данных"""
    
    print("=== EXPORT/IMPORT EXAMPLES ===\n")
    
    # Подготовка тестовых данных
    print("1. Подготовка тестовых данных...")
    firebase_service.clear_all_data()
    
    # Создание пользователей
    for i in range(1, 3):
        firebase_service.create_user(
            username=f"user{i}",
            email=f"user{i}@example.com",
            hashed_password="hash",
            full_name=f"User {i}"
        )
        
        # Создание документов для каждого пользователя
        for j in range(1, 3):
            firebase_service.create_document(
                user_id=f"user{i}",
                title=f"Doc {j} from User {i}",
                content=f"Content {j}..."
            )
    
    print("✅ Тестовые данные созданы\n")
    
    # Экспорт всех данных
    print("2. Экспорт всех данных...")
    exported_data = firebase_service.export_all_data()
    
    print(f"✅ Экспортировано:")
    print(f"   - Пользователей: {len(exported_data['users'])}")
    print(f"   - Документов: {len(exported_data['documents'])}")
    print(f"   - Дата экспорта: {exported_data['exported_at']}\n")
    
    # Сохранение в JSON файл
    print("3. Сохранение в JSON файл...")
    import json
    with open("firebase_backup.json", "w", encoding="utf-8") as f:
        json.dump(exported_data, f, indent=2, ensure_ascii=False)
    print("✅ Данные сохранены в firebase_backup.json\n")


# ========================== ПРИМЕР 5: BATCH ОПЕРАЦИИ ==========================

def example_batch_operations():
    """Примеры пакетных операций"""
    
    print("=== BATCH OPERATIONS ===\n")
    
    # Создание нескольких пользователей
    print("1. Создание нескольких пользователей...")
    users_to_create = [
        {"username": "batch_user1", "email": "batch1@example.com"},
        {"username": "batch_user2", "email": "batch2@example.com"},
        {"username": "batch_user3", "email": "batch3@example.com"},
    ]
    
    for user in users_to_create:
        firebase_service.create_user(
            username=user["username"],
            email=user["email"],
            hashed_password="hash"
        )
        print(f"✅ Создан: {user['username']}")
    
    print()
    
    # Создание документов для пользователя
    print("2. Создание нескольких документов для одного пользователя...")
    docs_to_create = [
        {"title": "Document 1", "content": "Content 1"},
        {"title": "Document 2", "content": "Content 2"},
        {"title": "Document 3", "content": "Content 3"},
    ]
    
    for doc_info in docs_to_create:
        firebase_service.create_document(
            user_id="batch_user1",
            **doc_info
        )
        print(f"✅ Создан: {doc_info['title']}")
    
    print()
    
    # Получение всех документов
    print("3. Получение всех документов пользователя...")
    user_docs = firebase_service.get_user_documents("batch_user1")
    print(f"✅ Всего документов: {len(user_docs)}\n")


# ========================== ЗАПУСК ВСЕХ ПРИМЕРОВ ==========================

if __name__ == "__main__":
    print("=" * 60)
    print("FIREBASE FIRESTORE API EXAMPLES")
    print("=" * 60 + "\n")
    
    try:
        example_user_operations()
        example_document_operations()
        example_security_checks()
        example_batch_operations()
        example_export_import()
        
        print("=" * 60)
        print("✅ ВСЕ ПРИМЕРЫ ВЫПОЛНЕНЫ УСПЕШНО!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
