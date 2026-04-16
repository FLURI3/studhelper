# Firebase Firestore Migration - Quick Start Guide

## 📋 Краткое описание

Проект мигрирован с JSON и PostgreSQL на **Firebase Firestore** — облачную NoSQL базу данных от Google.

### Что изменилось:
- ✅ **JSON файлы** → **Firestore коллекции** (users, documents)
- ✅ **PostgreSQL** → **Firebase Firestore** (облачная база)
- ✅ **Файловая система** → **Облачное хранилище** (можно добавить Firebase Storage)
- ✅ Сохранены все API endpoints (совместимость)

---

## 🚀 Быстрый старт

### 1. Получить Firebase Credentials

#### Способ A: Локальная разработка (через файл)
```bash
# 1. Перейти на https://console.firebase.google.com/
# 2. Создать проект "studeti"
# 3. Firestore Database → Создать → Production mode
# 4. Параметры проекта → Служебные аккаунты → Python → Создать ключ
# 5. Скопировать загруженный JSON файл:

mkdir -p backend/config
cp ~/Downloads/studeti-firebase-adminsdk-*.json backend/config/firebase-credentials.json
```

#### Способ B: Production (через переменную окружения)
```bash
# Содержимое JSON файла преобразуйте в одну строку и добавьте в .env:
FIREBASE_CREDENTIALS_JSON='{"type":"service_account","project_id":"studeti",...}'
```

### 2. Установить зависимости
```bash
pip install firebase-admin==6.2.0
```

### 3. Запустить приложение

#### Локально:
```bash
# Убедитесь, что файл credentials есть в backend/config/
python backend/main.py
```

#### Docker (Compose):
```bash
# Используйте новый compose файл с Firebase конфигурацией
docker-compose -f docker-compose.firebase.yml up
```

### 4. Миграция существующих данных (опционально)
```bash
python migrate_to_firebase.py
```

---

## 📊 Структура Firestore

### Коллекция: `users`
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "group": "ИВБО-01-21",
  "subgroup": 1,
  "hashed_password": "bcrypt_hash",
  "created_at": "2025-01-29T10:00:00Z",
  "updated_at": "2025-01-29T10:00:00Z"
}
```

### Коллекция: `documents`
```json
{
  "user_id": "johndoe",
  "title": "My Document",
  "content": "...",
  "original_filename": "document.pdf",
  "file_type": "parsed",
  "metadata": { "pages": 10 },
  "created_at": "2025-01-29T10:00:00Z",
  "updated_at": "2025-01-29T10:00:00Z"
}
```

---

## 🔐 Правила безопасности Firestore

### Для разработки (ANY ACCESS):
```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;
    }
  }
}
```

### Для production (RESTRICTED):
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

## 📚 API Reference

Все endpoints остались совместимы:

### Аутентификация
```bash
# Регистрация
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "secure123",
    "full_name": "Test User"
  }'

# Вход
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "secure123"
  }'

# Мой профиль
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <token>"

# Обновить профиль
curl -X PUT http://localhost:8000/api/auth/profile \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"group": "ИВБО-02-21"}'
```

### Документы
```bash
# Сохранить документ
curl -X POST http://localhost:8000/api/documents/save \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Doc",
    "content": "Content here...",
    "file_type": "parsed"
  }'

# Мои документы
curl -X GET http://localhost:8000/api/documents/my \
  -H "Authorization: Bearer <token>"

# Получить документ
curl -X GET http://localhost:8000/api/documents/{documentId} \
  -H "Authorization: Bearer <token>"

# Обновить документ
curl -X PUT http://localhost:8000/api/documents/{documentId} \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'

# Удалить документ
curl -X DELETE http://localhost:8000/api/documents/{documentId} \
  -H "Authorization: Bearer <token>"

# Поиск документов
curl -X GET http://localhost:8000/api/documents/search/keyword \
  -H "Authorization: Bearer <token>"
```

---

## 🔧 Файлы конфигурации

### Основные файлы миграции:
- `backend/services/firebase_service.py` — Сервис работы с Firestore
- `backend/routes/auth_firebase.py` — Аутентификация (обновлена)
- `backend/routes/documents_firebase.py` — Документы (обновлена)
- `docker-compose.firebase.yml` — Docker Compose с Firebase
- `migrate_to_firebase.py` — Скрипт миграции данных

### Примеры конфигурации:
- `.env.firebase.example` — Переменные окружения

### Документация:
- `FIREBASE_SETUP.md` — Полная инструкция по настройке

---

## 🐛 Troubleshooting

### Ошибка: "Firebase credentials not found"
```bash
# Убедитесь, что файл существует:
ls -la backend/config/firebase-credentials.json

# Проверьте переменную окружения:
echo $FIREBASE_CREDENTIALS_PATH
```

### Ошибка: "Permission denied"
1. Проверьте правила безопасности Firestore (консоль Firebase)
2. Убедитесь, что сервисный аккаунт активен

### Тестирование подключения:
```python
from services.firebase_service import firebase_service

# Проверить подключение
try:
    firebase_service.create_user(
        username="test_connection",
        email="test@example.com",
        hashed_password="test"
    )
    print("✅ Firebase работает!")
except Exception as e:
    print(f"❌ Ошибка: {e}")
```

---

## 📈 Мониторинг

### Просмотр использования Firestore:
1. Firebase Console → Firestore Database → Usage
2. Отслеживание:
   - Reads/Writes/Deletes
   - Stored data size
   - Network usage

### Резервное копирование:
```bash
# В Firebase Console: Firestore → ⋮ → Schedule exports
# или через gcloud CLI:
gcloud firestore export gs://your-bucket/backup-2025-01-29
```

---

## 🚦 Миграция с JSON на Firebase

Если у вас есть существующие JSON данные:

```bash
# 1. Убедитесь, что файлы находятся в backend/data/:
ls -la backend/data/

# 2. Запустите скрипт миграции:
python migrate_to_firebase.py

# 3. Проверьте Firebase Console:
# Firestore Database → Collections → users, documents
```

---

## ✅ Checklist для production

- [ ] Создан Firebase проект
- [ ] Firestore Database в режиме Production
- [ ] Сервисный аккаунт создан и ключ скачан
- [ ] Правила безопасности установлены (restricted mode)
- [ ] Индексы созданы
- [ ] Переменные окружения настроены
- [ ] Данные мигрированы (если требуется)
- [ ] API endpoints протестированы
- [ ] Backup configured
- [ ] Мониторинг включен

---

## 📞 Поддержка

### Полная документация:
- [Firebase Admin SDK Python](https://firebase.google.com/docs/reference/admin/python)
- [Firestore Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Firestore Best Practices](https://firebase.google.com/docs/firestore/best-practices)

### Локальная документация:
- `FIREBASE_SETUP.md` — Пошаговая инструкция
- `backend/services/firebase_service.py` — Код сервиса (с комментариями)

---

**✅ Готово! Firebase Firestore полностью интегрирован в проект.**
