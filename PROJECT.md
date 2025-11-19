# 📦 Student Helper - Содержимое проекта

## ✅ Что уже реализовано (MVP v1.0)

### Frontend (React + Vite + Tailwind CSS)
- ✅ Главная страница с навигацией
- ✅ Тёмная тема с glassmorphism эффектами
- ✅ Адаптивный дизайн
- ✅ 6 основных страниц:
  - **Главная** - обзор возможностей
  - **Парсер документов** - загрузка и извлечение текста
  - **Умное сокращение** - интеграция с Ollama
  - **Анализ текста** - статистика и ключевые термины
  - **Генератор вопросов** - (заглушка)
  - **Документы** - (заглушка)

### Backend (FastAPI + Python)
- ✅ Парсинг документов:
  - PDF (pdfplumber)
  - PPTX (python-pptx)
  - DOCX (python-docx)
  - Изображения с OCR (pytesseract)
- ✅ Интеграция с Ollama:
  - Сокращение текста
  - Генерация вопросов
- ✅ Анализ текста:
  - Подсчёт слов, предложений, символов
  - Время чтения
  - Сложность текста
  - Ключевые термины

### Инфраструктура
- ✅ Docker Compose для всех сервисов
- ✅ PostgreSQL (готов к использованию)
- ✅ Redis (готов к кэшированию)
- ✅ Ollama контейнер
- ✅ Скрипты для быстрого запуска (start.bat, stop.bat)

### Документация
- ✅ README.md - общее описание
- ✅ QUICKSTART.md - быстрый старт
- ✅ DEPLOYMENT.md - развёртывание и разработка
- ✅ .env.example - пример конфигурации

---

## 🔧 Следующие шаги (v1.1)

### Frontend
- [ ] Улучшенный UI для генератора вопросов
- [ ] История документов с сохранением в БД
- [ ] Экспорт результатов (PDF, DOCX)
- [ ] Сравнение текстов side-by-side
- [ ] Копирование в буфер обмена
- [ ] Drag & Drop для файлов (уже частично есть)

### Backend
- [ ] Полноценная работа с БД (SQLAlchemy модели)
- [ ] Кэширование результатов в Redis
- [ ] Улучшенный парсинг вопросов из LLM
- [ ] Конвертер Markdown ↔ HTML
- [ ] Word Cloud генерация

### Дополнительно
- [ ] Аутентификация (JWT)
- [ ] Личный кабинет пользователя
- [ ] Теги и категории для документов
- [ ] Поиск по документам

---

## 🎯 Будущие возможности (v2.0)

- [ ] Генератор Mind Maps
- [ ] Режим чтения с таймером Pomodoro
- [ ] Интеграция с облачными LLM (OpenAI, Anthropic)
- [ ] Экспорт в Anki карточки
- [ ] QR-коды для шаринга
- [ ] Офлайн режим (PWA)
- [ ] Мобильное приложение

---

## 📂 Файловая структура

```
studeti/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   └── Layout.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── Parser.jsx
│   │   │   ├── TextShortener.jsx
│   │   │   ├── Analyzer.jsx
│   │   │   ├── QuestionGenerator.jsx
│   │   │   └── Documents.jsx
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── .eslintrc.cjs
│   ├── Dockerfile
│   └── .env
│
├── backend/
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── parser.py
│   │   ├── llm.py
│   │   ├── analyzer.py
│   │   └── documents.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── parser_service.py
│   │   ├── ollama_service.py
│   │   └── analyzer_service.py
│   ├── main.py
│   ├── config.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── QUICKSTART.md
├── DEPLOYMENT.md
├── PROJECT.md (этот файл)
├── start.bat
└── stop.bat
```

---

## 🛠️ Технологический стек

### Frontend
| Технология | Версия | Назначение |
|------------|--------|------------|
| React | 18.2 | UI фреймворк |
| Vite | 5.0 | Build tool |
| Tailwind CSS | 3.3 | Стилизация |
| React Router | 6.20 | Роутинг |
| Axios | 1.6 | HTTP клиент |
| Framer Motion | 10.16 | Анимации |
| Lucide React | 0.294 | Иконки |
| pdfjs-dist | 3.11 | PDF парсинг (клиент) |
| mammoth | 1.6 | DOCX парсинг |
| tesseract.js | 5.0 | OCR (клиент) |

### Backend
| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.11 | Язык |
| FastAPI | 0.104 | Web фреймворк |
| Uvicorn | 0.24 | ASGI сервер |
| SQLAlchemy | 2.0 | ORM |
| PostgreSQL | 15 | База данных |
| Redis | 7 | Кэш |
| pdfplumber | 0.10 | PDF парсинг |
| python-pptx | 0.6 | PPTX парсинг |
| python-docx | 1.1 | DOCX парсинг |
| pytesseract | 0.3 | OCR |
| httpx | 0.25 | HTTP клиент (для Ollama) |

### AI/ML
| Технология | Версия | Назначение |
|------------|--------|------------|
| Ollama | latest | Локальный LLM хостинг |
| Mistral | latest | Основная модель |
| LLaMA 2 | latest | Альтернативная модель |

### DevOps
| Технология | Версия | Назначение |
|------------|--------|------------|
| Docker | latest | Контейнеризация |
| Docker Compose | latest | Оркестрация |

---

## 🚀 Как запустить

### Простой способ (рекомендуется)

```powershell
.\start.bat
```

### Ручной способ

```powershell
docker-compose up -d
docker exec studeti-ollama-1 ollama pull mistral
```

Откройте http://localhost:5173

Подробнее в `QUICKSTART.md` и `DEPLOYMENT.md`

---

## 📊 API Endpoints

### Parser
- `POST /api/parser/upload` - Загрузить и распарсить файл

### LLM
- `POST /api/llm/summarize` - Сократить текст
- `POST /api/llm/questions` - Сгенерировать вопросы

### Analyzer
- `POST /api/analyzer/stats` - Анализ текста

### Documents (заглушки)
- `GET /api/documents` - Список документов
- `POST /api/documents/save` - Сохранить документ

Документация: http://localhost:8000/docs

---

## 🎨 Дизайн система

### Цвета
- **Фон**: `#0f0f0f` (primary-bg)
- **Вторичный фон**: `#1e1e1e` (primary-secondary)
- **Третичный фон**: `#2d2d2d` (primary-tertiary)
- **Акцент голубой**: `#00d9ff` (accent-cyan)
- **Акцент фиолетовый**: `#7c3aed` (accent-purple)
- **Текст основной**: `#f0f0f0` (text-primary)
- **Текст вторичный**: `#a0a0a0` (text-secondary)
- **Границы**: `#333333` (border)

### Компоненты
- **glass-card** - карточки с glassmorphism
- **btn-primary** - основная кнопка (голубая)
- **btn-secondary** - вторичная кнопка (серая)
- **input-field** - поля ввода

---

## 🔐 Переменные окружения

```env
# Backend
BACKEND_PORT=8000
OLLAMA_URL=http://ollama:11434
REDIS_URL=redis://redis:6379
DATABASE_URL=postgresql://user:password@postgres:5432/studentdb
JWT_SECRET=your-secret-key

# Frontend
VITE_API_URL=http://localhost:8000

# Ollama
OLLAMA_MODEL=mistral
```

---

## 🤝 Разработка

### Добавить новую страницу

1. Создать `frontend/src/pages/NewPage.jsx`
2. Добавить роут в `App.jsx`
3. Добавить в навигацию `Layout.jsx`

### Добавить новый API endpoint

1. Создать `backend/routes/new_route.py`
2. Создать `backend/services/new_service.py`
3. Зарегистрировать в `main.py`

### Стилизация

Использовать Tailwind классы или кастомные классы из `index.css`

---

## 📝 Лицензия

MIT

---

## 👨‍💻 Автор

Создано с помощью GitHub Copilot для помощи студентам в обучении
