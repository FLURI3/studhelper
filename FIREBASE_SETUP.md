# Firebase Firestore Setup Guide

## 1. Создание проекта Firebase

### Шаг 1: Перейти на Firebase Console
- Откройте https://console.firebase.google.com/
- Нажмите "Создать проект" (Create project)
- Введите имя проекта: `studeti`
- Пропустите Google Analytics (optional)
- Нажмите "Создать проект"

### Шаг 2: Включить Firestore Database
- В левом меню выберите "Firestore Database"
- Нажмите "Создать базу данных"
- Выберите режим: **Production mode** (не development)
- Выберите регион: `europe-west1` (Frankfurt) или `us-central1` (Iowa)
- Нажмите "Создать"

### Шаг 3: Создание Service Account для приложения
- В левом меню: Параметры проекта (⚙️) → Вкладка "Служебные аккаунты"
- Выберите "Python"
- Нажмите "Создать новый приватный ключ"
- Загруженный файл `[your-project-id]-firebase-adminsdk-[hash].json` сохраните

---

## 2. Подготовка приложения

### Вариант A: Использование файла учетных данных (разработка)

```bash
# Сохраните JSON файл сервисного аккаунта в проект
mkdir -p backend/config
cp path/to/firebase-adminsdk-XXXX.json backend/config/firebase-credentials.json
```

### Вариант B: Использование переменной окружения (production)

Содержимое JSON файла преобразуйте в одну строку и добавьте в `.env`:

```bash
# Если файл:
cat backend/config/firebase-adminsdk-XXXX.json

# Скопируйте весь JSON и добавьте в .env:
FIREBASE_CREDENTIALS_JSON='{"type": "service_account", "project_id": "...", ...}'
```

Или через `.env`:
```
FIREBASE_CREDENTIALS_PATH=/app/config/firebase-credentials.json
```

---

## 3. Обновление docker-compose.yml

Добавьте переменные окружения для backend:

```yaml
backend:
  environment:
    - FIREBASE_CREDENTIALS_PATH=/app/config/firebase-credentials.json
    # или используйте FIREBASE_CREDENTIALS_JSON в .env
```

Если используете файл, добавьте volume:

```yaml
backend:
  volumes:
    - ./backend/config:/app/config:ro
```

---

## 4. Структура коллекций Firestore

Выполните следующие команды или используйте Firestore Console для создания индексов:

### Коллекция: `users`
```
users/
├── {username}
│   ├── email: string
│   ├── username: string
│   ├── full_name: string
│   ├── group: string
│   ├── subgroup: number
│   ├── hashed_password: string
│   ├── created_at: timestamp
│   └── updated_at: timestamp
```

**Правила безопасности Firestore (в консоли):**
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Только собственные данные пользователя
    match /users/{username} {
      allow read, write: if request.auth.uid == username;
    }
    
    // Только собственные документы
    match /documents/{document} {
      allow read, write: if request.auth.uid == resource.data.user_id;
      allow create: if request.auth.uid == request.resource.data.user_id;
    }
    
    // Индекс для быстрого поиска
    match /user_documents_index/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
  }
}
```

### Коллекция: `documents`
```
documents/
├── {documentId}
│   ├── user_id: string (reference to username)
│   ├── title: string
│   ├── content: string
│   ├── original_filename: string
│   ├── file_type: string
│   ├── metadata: map
│   ├── created_at: timestamp
│   └── updated_at: timestamp
```

### Коллекция: `user_documents_index`
```
user_documents_index/
├── {username}
│   └── document_ids: array
```

---

## 5. Создание индексов Firestore

### В консоли Firebase:
1. Перейдите в "Firestore Database" → "Индексы"
2. Создайте индекс для поиска документов пользователя:
   - Коллекция: `documents`
   - Поля: `user_id` (Ascending), `created_at` (Descending)

3. Создайте индекс для поиска по пользователю:
   - Коллекция: `users`
   - Поля: `email` (Ascending)

---

## 6. Миграция данных из JSON

### Скрипт миграции:

```python
# backend/scripts/migrate_to_firebase.py
import json
from pathlib import Path
from services.firebase_service import firebase_service
from routes.auth import get_password_hash

def migrate_users():
    """Миграция пользователей из JSON в Firebase"""
    users_file = Path("/app/data/users.json")
    
    if not users_file.exists():
        print("users.json не найден")
        return
    
    with open(users_file, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    for username, user_data in users.items():
        try:
            firebase_service.create_user(
                username=username,
                email=user_data.get("email"),
                hashed_password=user_data.get("hashed_password"),
                full_name=user_data.get("full_name"),
                group=user_data.get("group"),
                subgroup=user_data.get("subgroup")
            )
            print(f"✓ Пользователь {username} мигрирован")
        except Exception as e:
            print(f"✗ Ошибка при миграции {username}: {e}")

def migrate_documents():
    """Миграция документов из JSON в Firebase"""
    docs_file = Path("/app/data/documents.json")
    
    if not docs_file.exists():
        print("documents.json не найден")
        return
    
    with open(docs_file, 'r', encoding='utf-8') as f:
        documents = json.load(f)
    
    for doc_data in documents:
        try:
            firebase_service.create_document(
                user_id=doc_data.get("user_id"),
                title=doc_data.get("title"),
                content=doc_data.get("content"),
                original_filename=doc_data.get("original_filename"),
                file_type=doc_data.get("file_type"),
                metadata=doc_data.get("metadata")
            )
            print(f"✓ Документ {doc_data.get('title')} мигрирован")
        except Exception as e:
            print(f"✗ Ошибка при миграции документа: {e}")

if __name__ == "__main__":
    print("Начало миграции...")
    migrate_users()
    migrate_documents()
    print("Миграция завершена!")
```

Запуск:
```bash
python backend/scripts/migrate_to_firebase.py
```

---

## 7. Обновление main.py

Замените импорты маршрутов:

```python
# Было:
from routes.auth import router as auth_router
from routes.documents import router as documents_router

# Стало:
from routes.auth_firebase import router as auth_router
from routes.documents_firebase import router as documents_router
```

---

## 8. Переменные окружения

Добавьте в `.env.example`:

```env
# Firebase
FIREBASE_CREDENTIALS_PATH=/app/config/firebase-credentials.json
# или FIREBASE_CREDENTIALS_JSON={"type": "service_account", ...}
```

Добавьте в `.env.production.example`:

```env
# Firebase (использует переменную FIREBASE_CREDENTIALS_JSON)
FIREBASE_CREDENTIALS_JSON=${FIREBASE_JSON}
```

---

## 9. Безопасность Firestore

### Правила для разработки:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;  // ТОЛЬКО ДЛЯ РАЗРАБОТКИ!
    }
  }
}
```

### Правила для production:
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{username} {
      allow read, write: if request.auth.uid == username;
    }
    match /documents/{documentId} {
      allow read, write: if request.auth.uid == resource.data.user_id;
      allow create: if request.auth.uid == request.resource.data.user_id;
    }
  }
}
```

---

## 10. Резервное копирование Firestore

### Экспорт всех данных:
```bash
# В консоли Firebase -> Firestore -> ⋮ -> Экспорт
# или через CLI:

gcloud firestore export gs://your-bucket/backup-2025-01-29
```

### Импорт данных:
```bash
gcloud firestore import gs://your-bucket/backup-2025-01-29
```

---

## 11. Котесты и troubleshooting

### Ошибка: "Не удалось инициализировать Firebase"
- Проверьте путь к файлу учетных данных
- Убедитесь, что файл скопирован в контейнер

### Ошибка: "Permission denied"
- Проверьте правила безопасности Firestore
- Убедитесь, что сервисный аккаунт имеет необходимые разрешения

### Проверка подключения:
```python
from services.firebase_service import firebase_service

# Попробуйте создать тестовый документ
firebase_service.create_user(
    username="test_user",
    email="test@example.com",
    hashed_password="hashed",
    full_name="Test"
)
print("✓ Firebase работает!")
```

---

## 12. API Endpoints

После миграции доступны следующие endpoints:

### Аутентификация
- `POST /api/auth/register` — Регистрация
- `POST /api/auth/login` — Вход
- `GET /api/auth/me` — Текущий пользователь
- `PUT /api/auth/profile` — Обновление профиля

### Документы
- `POST /api/documents/save` — Сохранить документ
- `GET /api/documents/my` — Мои документы
- `GET /api/documents/{id}` — Получить документ
- `PUT /api/documents/{id}` — Обновить документ
- `DELETE /api/documents/{id}` — Удалить документ
- `GET /api/documents/search/{query}` — Поиск документов

---

## 13. Финальная проверка

```bash
# Установите зависимости
pip install firebase-admin==6.2.0

# Запустите backend
python backend/main.py

# Протестируйте API
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "securepass123",
    "full_name": "Test User"
  }'
```

---

✅ **Firebase Firestore полностью готов к использованию!**
