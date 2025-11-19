# Student Helper - Инструкция по запуску

## Быстрый старт с Docker

1. Убедитесь, что Docker Desktop запущен

2. Запустите все сервисы:
```powershell
docker-compose up -d
```

3. Загрузите модель Ollama (выполните после запуска контейнеров):
```powershell
docker exec -it studeti-ollama-1 ollama pull mistral
```

4. Откройте приложение:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Локальная разработка

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Примечание:** Для работы OCR нужен Tesseract:
- Скачайте: https://github.com/UB-Mannheim/tesseract/wiki
- Добавьте в PATH

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Полезные команды

### Docker

```powershell
# Остановить все сервисы
docker-compose down

# Перезапустить конкретный сервис
docker-compose restart backend

# Посмотреть логи
docker-compose logs -f backend

# Очистить всё (volumes тоже)
docker-compose down -v
```

### Ollama

```powershell
# Список загруженных моделей
docker exec studeti-ollama-1 ollama list

# Загрузить другую модель
docker exec studeti-ollama-1 ollama pull llama2

# Тест генерации
docker exec studeti-ollama-1 ollama run mistral "Привет!"
```

## Возможные проблемы

### Порты заняты

Если порты 5173, 8000, 11434 заняты, измените их в `docker-compose.yml`

### Ollama не отвечает

```powershell
docker-compose restart ollama
docker-compose logs ollama
```

### Frontend не видит Backend

Проверьте переменную окружения `VITE_API_URL` в `frontend/.env`

## Структура проекта

```
studeti/
├── frontend/              # React приложение
│   ├── src/
│   │   ├── components/   # UI компоненты
│   │   ├── pages/        # Страницы
│   │   └── App.jsx
│   └── package.json
│
├── backend/              # FastAPI приложение
│   ├── routes/          # API маршруты
│   ├── services/        # Бизнес-логика
│   └── main.py
│
└── docker-compose.yml
```

## API Endpoints

- `POST /api/parser/upload` - Загрузить документ
- `POST /api/llm/summarize` - Сократить текст
- `POST /api/llm/questions` - Генерация вопросов
- `POST /api/analyzer/stats` - Анализ текста

Документация: http://localhost:8000/docs
