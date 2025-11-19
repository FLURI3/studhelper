# 🚀 Развертывание проекта Student Helper

## Простой запуск (рекомендуется)

### Windows

Дважды кликните на `start.bat` или выполните в PowerShell:

```powershell
.\start.bat
```

Это автоматически:
1. Проверит наличие Docker
2. Запустит все контейнеры
3. Загрузит модель Ollama (mistral)
4. Откроет приложение в браузере

### Остановка

Дважды кликните `stop.bat` или:

```powershell
.\stop.bat
```

---

## Ручной запуск

### 1. Запустить Docker контейнеры

```powershell
docker-compose up -d
```

### 2. Дождаться запуска (проверка логов)

```powershell
docker-compose logs -f
```

Нажмите `Ctrl+C` для выхода из логов

### 3. Загрузить модель Ollama

```powershell
docker exec studeti-ollama-1 ollama pull mistral
```

Опционально - другие модели:
```powershell
docker exec studeti-ollama-1 ollama pull llama2
docker exec studeti-ollama-1 ollama pull neural-chat
```

### 4. Открыть приложение

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434

---

## Локальная разработка (без Docker)

### Backend

1. Установить Python 3.10+
2. Установить Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
3. Добавить Tesseract в PATH

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Запуск:
```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Ollama (локально)

Скачать: https://ollama.ai/download

Установить модели:
```powershell
ollama pull mistral
ollama pull llama2
```

---

## Проверка работоспособности

### 1. Проверить контейнеры

```powershell
docker-compose ps
```

Все сервисы должны быть в статусе "Up"

### 2. Проверить Backend

```powershell
curl http://localhost:8000/health
```

Ответ: `{"status":"healthy"}`

### 3. Проверить Ollama

```powershell
curl http://localhost:11434/api/tags
```

Должен вернуть список установленных моделей

### 4. Тест генерации

```powershell
curl -X POST http://localhost:11434/api/generate -d '{
  "model": "mistral",
  "prompt": "Hello",
  "stream": false
}'
```

---

## Решение проблем

### Порты заняты

Если порты 5173, 8000, 11434, 5432, 6379 заняты:

Измените в `docker-compose.yml`:
```yaml
services:
  frontend:
    ports:
      - "3000:5173"  # Внешний порт: Внутренний порт
```

### Контейнер не запускается

```powershell
# Посмотреть логи конкретного сервиса
docker-compose logs backend

# Перезапустить сервис
docker-compose restart backend

# Полная пересборка
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Ollama не отвечает

```powershell
docker-compose restart ollama
docker exec studeti-ollama-1 ollama list
```

### Frontend не видит Backend

Проверьте `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

После изменения перезапустите frontend:
```powershell
docker-compose restart frontend
```

### Очистить всё и начать заново

```powershell
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## Разработка

### Горячая перезагрузка

- **Frontend**: Автоматически при изменении файлов в `src/`
- **Backend**: Автоматически (uvicorn --reload)

### Структура проекта

```
studeti/
├── frontend/
│   ├── src/
│   │   ├── components/     # Переиспользуемые компоненты
│   │   ├── pages/          # Страницы приложения
│   │   ├── App.jsx         # Главный компонент
│   │   └── main.jsx        # Точка входа
│   ├── index.html
│   └── package.json
│
├── backend/
│   ├── routes/             # API endpoints
│   ├── services/           # Бизнес-логика
│   ├── main.py             # FastAPI app
│   └── requirements.txt
│
└── docker-compose.yml
```

### Добавление нового API endpoint

1. Создать маршрут в `backend/routes/`
2. Создать сервис в `backend/services/`
3. Зарегистрировать в `backend/main.py`

Пример:
```python
# routes/new_feature.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/test")
async def test():
    return {"message": "Hello"}

# main.py
from routes import new_feature
app.include_router(new_feature.router, prefix="/api/feature", tags=["feature"])
```

### Добавление новой страницы

1. Создать компонент в `frontend/src/pages/`
2. Добавить маршрут в `frontend/src/App.jsx`
3. Добавить в навигацию в `frontend/src/components/Layout/Layout.jsx`

---

## Deployment (Production)

### Изменения для продакшена

1. **Environment variables**:
```env
BACKEND_PORT=8000
OLLAMA_URL=http://ollama:11434
DATABASE_URL=postgresql://user:strong_password@postgres:5432/studentdb
JWT_SECRET=your-very-strong-secret-key
```

2. **Docker Compose**:
- Удалить `volumes` для hot reload
- Изменить `command` на production режим
- Добавить `restart: always`

3. **Frontend**:
```powershell
cd frontend
npm run build
```

Использовать Nginx для раздачи статики

4. **Backend**:
```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Полезные команды

```powershell
# Просмотр логов всех сервисов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend

# Войти в контейнер
docker exec -it studeti-backend-1 bash

# Список контейнеров
docker ps

# Использование ресурсов
docker stats

# Очистить неиспользуемые образы
docker system prune -a
```

---

## Мониторинг

### Backend API Docs
http://localhost:8000/docs - Swagger UI
http://localhost:8000/redoc - ReDoc

### Database
```powershell
docker exec -it studeti-postgres-1 psql -U user -d studentdb
```

### Redis
```powershell
docker exec -it studeti-redis-1 redis-cli
```

---

Больше информации в `README.md` и `QUICKSTART.md`
