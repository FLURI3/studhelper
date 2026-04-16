# 🔥 Firebase Firestore Integration for Studeti

![Firebase](https://img.shields.io/badge/Firebase-Firestore-FFA500)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

**Полная интеграция Firebase Firestore** в проект Studeti - миграция с PostgreSQL на облачную NoSQL базу данных.

---

## 🎯 Что это дает

✅ **Без операционных затрат** - Google управляет инфраструктурой  
✅ **Автоматическое масштабирование** - растет с вашим приложением  
✅ **Встроенная безопасность** - Security Rules вместо SQL permissions  
✅ **Real-time базовая функциональность** - готово к расширению  
✅ **Дешево для стартапов** - pay-as-you-go модель ($5-10/месяц)  

---

## 🚀 Быстрый старт (5 минут)

### 1️⃣ Получить Firebase Credentials

```bash
# Перейти на https://console.firebase.google.com/
# 1. Создать проект "studeti"
# 2. Firestore Database → Create → Production mode
# 3. Project Settings → Service Accounts → Python → Create Key
# 4. Скопировать JSON в:

mkdir -p backend/config
# Скопируйте скачанный файл сюда ↓
cp ~/Downloads/studeti-firebase-adminsdk-*.json backend/config/firebase-credentials.json
```

### 2️⃣ Установить зависимости

```bash
pip install firebase-admin==6.2.0
```

### 3️⃣ Запустить приложение

```bash
python backend/main.py
```

**Готово! 🎉**

---

## 📖 Полная документация

| Документ | Время | Описание |
|----------|-------|---------|
| **FIREBASE_QUICKSTART.md** | 5 мин | Быстрый старт и API reference |
| **FIREBASE_SETUP.md** | 30 мин | Детальная инструкция по настройке |
| **DATABASE_COMPARISON.md** | 10 мин | PostgreSQL vs Firebase анализ |
| **examples_firebase_api.py** | 15 мин | Примеры кода с объяснениями |
| **FIREBASE_INTEGRATION_SUMMARY.md** | 10 мин | Обзор интеграции |

---

## 📦 Что было создано

### Сервисы
```python
backend/services/firebase_service.py
├── Singleton паттерн для Firebase подключения
├── CRUD операции для users и documents
├── Поиск и фильтрация данных
└── Экспорт/импорт функциональность
```

### API маршруты
```
backend/routes/auth_firebase.py       # Аутентификация
backend/routes/documents_firebase.py  # Работа с документами
```

### Инструменты
```
migrate_to_firebase.py                # Миграция данных из JSON
examples_firebase_api.py              # Примеры использования
setup_firebase.sh                     # Автоматизированная настройка
```

### Конфигурация
```
docker-compose.firebase.yml           # Docker без PostgreSQL
.env.firebase.example                 # Пример переменных
FIREBASE_*.md                         # Документация
```

---

## 🔐 API Endpoints (Без изменений)

Все endpoints остались совместимы:

### Аутентификация
```bash
POST   /api/auth/register      # Регистрация
POST   /api/auth/login         # Вход
GET    /api/auth/me            # Мой профиль
PUT    /api/auth/profile       # Обновить профиль
```

### Документы
```bash
POST   /api/documents/save         # Сохранить
GET    /api/documents/my           # Мои документы
GET    /api/documents/{id}         # Получить
PUT    /api/documents/{id}         # Обновить
DELETE /api/documents/{id}         # Удалить
GET    /api/documents/search/{q}   # Поиск
```

---

## 💻 Примеры использования

### Создание пользователя
```python
from services.firebase_service import firebase_service

firebase_service.create_user(
    username="johndoe",
    email="john@example.com",
    hashed_password="bcrypt_hash",
    full_name="John Doe",
    group="ИВБО-01-21"
)
```

### Работа с документами
```python
# Создание
doc = firebase_service.create_document(
    user_id="johndoe",
    title="My Document",
    content="...",
    file_type="parsed"
)

# Получение
documents = firebase_service.get_user_documents("johndoe")

# Поиск
results = firebase_service.search_documents("johndoe", "keyword")

# Удаление
firebase_service.delete_document(doc["id"], "johndoe")
```

---

## 🗂️ Структура Firestore

```
Firestore/
│
├── users/
│   ├── john_doe/
│   │   ├── email
│   │   ├── username
│   │   ├── full_name
│   │   ├── group
│   │   └── created_at
│   └── ...
│
├── documents/
│   ├── doc_id_123/
│   │   ├── user_id (reference)
│   │   ├── title
│   │   ├── content
│   │   ├── file_type
│   │   └── created_at
│   └── ...
│
└── user_documents_index/
    ├── john_doe/
    │   └── document_ids: [...]
    └── ...
```

---

## 🔐 Безопасность

### Security Rules для production

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    // Пользователь может читать/писать только свои данные
    match /users/{username} {
      allow read, write: if request.auth.uid == username;
    }
    
    // Пользователь может работать только со своими документами
    match /documents/{documentId} {
      allow read, write: if request.auth.uid == resource.data.user_id;
      allow create: if request.auth.uid == request.resource.data.user_id;
    }
  }
}
```

---

## 📊 Производительность

| Операция | Время |
|----------|-------|
| Get by ID | 10-50ms |
| Filter by user_id | 20-100ms |
| Search | 200-1000ms* |
| Create | 30-100ms |

*Зависит от размера коллекции и наличия индексов

---

## 💰 Стоимость

### Бесплатный уровень (всегда)
- 50,000 reads/день
- 20,000 writes/день
- 20,000 deletes/день
- 1 GB storage

### Pay-as-you-go (при превышении)
- $0.06 за 100K reads
- $0.18 за 100K writes
- $0.18 за 100K deletes
- $0.18 за GB storage

**Примерная стоимость для стартапа: $5-10/месяц**

---

## 🔄 Миграция из PostgreSQL

### Если у вас есть существующие данные JSON:

```bash
# 1. Убедитесь, что файлы в backend/data/
ls backend/data/users.json
ls backend/data/documents.json

# 2. Запустите миграцию
python migrate_to_firebase.py

# 3. Результат: Все данные в Firebase Firestore
```

---

## ✅ Checklist для production

- [ ] Firebase проект создан
- [ ] Firestore Database включена
- [ ] Service Account создан и JSON скачан
- [ ] JSON скопирован в `backend/config/`
- [ ] Security Rules установлены
- [ ] Зависимости установлены
- [ ] Приложение запущено и протестировано
- [ ] API endpoints работают
- [ ] Данные мигрированы (если требуется)
- [ ] Резервное копирование настроено

---

## 🐛 Troubleshooting

### Firebase credentials not found
```bash
# Проверьте путь
ls -la backend/config/firebase-credentials.json

# Или переменную окружения
echo $FIREBASE_CREDENTIALS_PATH
```

### Permission denied
1. Проверьте Security Rules в Firebase Console
2. Убедитесь, что сервисный аккаунт активен

### Протестировать подключение
```python
from services.firebase_service import firebase_service
print(firebase_service.db)  # Если ошибок нет - OK
```

---

## 📚 Дополнительные ресурсы

### Официальные docs:
- [Firebase Admin SDK Python](https://firebase.google.com/docs/reference/admin/python)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Security Rules Guide](https://firebase.google.com/docs/firestore/security/get-started)

### Локальные docs:
- `FIREBASE_SETUP.md` - Полная инструкция
- `examples_firebase_api.py` - Примеры кода
- `DATABASE_COMPARISON.md` - Анализ PostgreSQL vs Firebase

---

## 🤝 Поддержка

Если возникают вопросы:
1. Прочитайте документацию выше
2. Проверьте примеры в `examples_firebase_api.py`
3. Посмотрите исходный код в `backend/services/firebase_service.py`
4. Проверьте Firebase Console для логов и ошибок

---

## 📈 Следующие шаги

### Добавить Firebase Storage (для файлов)
```python
from firebase_admin import storage
bucket = storage.bucket()
bucket.blob('documents/file.pdf').upload_from_filename('file.pdf')
```

### Добавить Real-time Sync (для фронтенда)
```javascript
const db = firebase.firestore();
db.collection("documents")
  .where("user_id", "==", userId)
  .onSnapshot(snapshot => { /* Real-time updates */ });
```

### Добавить Firebase Authentication
```python
from firebase_admin import auth
user = auth.create_user(email=email, password=password)
```

---

## 📝 Лицензия

MIT

---

## 🎉 Готово!

Firebase Firestore интегрирован и готов к использованию.

**Для начала работы:**
```bash
python backend/main.py
```

**Для Docker:**
```bash
docker-compose -f docker-compose.firebase.yml up
```

---

**Вопросы?** Читайте `FIREBASE_SETUP.md` 📖
