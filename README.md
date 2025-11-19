# 📚 Student Helper - AI-платформа для студентов

> Современное веб-приложение для студентов с интеграцией искусственного интеллекта, автоматическим парсингом документов, умным сокращением текста и расписанием занятий СГТУ.

[![Version](https://img.shields.io/badge/version-2.0-blue.svg)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/react-18.2-blue.svg)](https://react.dev)

## 📋 Содержание

- [Обзор проекта](#обзор-проекта)
- [Основные возможности](#основные-возможности)
- [Архитектура](#архитектура)
- [Быстрый старт](#быстрый-старт)
- [Документация сервисов](#документация-сервисов)
- [Технологический стек](#технологический-стек)
- [Разработка](#разработка)
- [Развёртывание](#развёртывание)

## 🎯 Обзор проекта

**Student Helper** — это комплексная платформа для автоматизации рутинных задач студентов:
- Обработка учебных материалов (PDF, DOCX, PPTX)
- Интеллектуальное сокращение текста с помощью локальных LLM моделей
- Парсинг и отображение расписания занятий СГТУ
- Анализ текста и генерация тестовых вопросов
- Система обучения и дообучения моделей на кастомных данных

### Ключевые преимущества
- ✅ **Полная автономность** — все модели работают локально через Ollama
- ✅ **Адаптивный интерфейс** — мобильная версия с burger-меню
- ✅ **Модульная архитектура** — легко добавлять новые функции
- ✅ **Контейнеризация** — простое развёртывание через Docker Compose
- ✅ **Автоматическое обучение** — система fine-tuning для улучшения качества

## ✨ Основные возможности

### 🛠️ Инструменты

#### 📄 Парсер документов
- Поддержка форматов: PDF, DOCX, PPTX, изображения
- OCR для сканированных документов (Tesseract)
- Извлечение текста, таблиц, метаданных
- Экспорт в Markdown, JSON, TXT

#### ✂️ Сокращалка текста
- Интеграция с Ollama (Mistral, LLaMA 2, Gemma)
- Настройка длины результата (10-90% от оригинала)
- Сохранение ключевых идей и структуры
- Автоматическое обучение на примерах пользователя

#### 📊 Анализатор текста
- Статистика: слова, символы, предложения
- Оценка сложности текста (Flesch Reading Ease)
- Извлечение ключевых терминов
- Определение языка и тональности

#### ❓ Генератор вопросов
- Автоматическое создание тестовых вопросов по тексту
- Различные типы: открытые, закрытые, множественный выбор
- Экспорт в Markdown для использования в тестах

### 🎓 Для учёбы

#### 📅 Расписание занятий
- Парсинг расписания СГТУ с официального сайта
- Группировка по специальностям (ИСП, МТО, ТОА, СВ, ТМ, ЭК)
- Поиск по группам
- Отображение текущего дня
- Поддержка подгрупп и нескольких преподавателей
- Мобильная адаптация

#### 📁 Документы
- Хранение обработанных документов
- История операций
- Быстрый поиск по контенту
- Организация по категориям

#### 🧠 Обучение модели
- Fine-tuning моделей на пользовательских данных
- Сбор обучающих примеров в фоновом режиме
- Автоматический запуск обучения при накоплении данных
- Метрики качества и прогресс обучения

## 🏗️ Архитектура системы

### Общая схема

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Browser)                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Frontend (React + Vite)                    │
│  • React 18.2 • Tailwind CSS • Axios • Lucide Icons     │
│  • Pages: Home, Parser, Shortener, Schedule, etc.       │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST API
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Backend (FastAPI)                          │
│  Routes:                                                │
│  • /api/parser    - Парсинг документов                  │
│  • /api/llm       - Работа с LLM                        │
│  • /api/analyzer  - Анализ текста                       │
│  • /api/schedule  - Расписание СГТУ                     │
│  • /api/documents - Управление документами              │
│  • /api/training  - Обучение моделей                    │
└────┬────────────────┬──────────────┬────────────────────┘
     │                │              │
     ▼                ▼              ▼
┌─────────┐   ┌──────────────┐  ┌──────────────┐
│ Ollama  │   │  PostgreSQL  │  │    Redis     │
│  LLM    │   │   Database   │  │    Cache     │
│ Mistral │   │   Documents  │  │   Sessions   │
└─────────┘   └──────────────┘  └──────────────┘
```

### Структура проекта

```
studeti/
├── 📁 frontend/                    # React приложение
│   ├── src/
│   │   ├── components/            # Переиспользуемые компоненты
│   │   │   ├── Layout/           # Основной макет с навигацией
│   │   │   ├── FileUpload.jsx    # Загрузка файлов
│   │   │   └── LoadingSpinner.jsx
│   │   ├── pages/                # Страницы приложения
│   │   │   ├── Home.jsx          # Главная
│   │   │   ├── Parser.jsx        # Парсер документов
│   │   │   ├── TextShortener.jsx # Сокращалка
│   │   │   ├── Analyzer.jsx      # Анализатор
│   │   │   ├── Schedule.jsx      # Расписание
│   │   │   ├── Documents.jsx     # Документы
│   │   │   ├── Training.jsx      # Обучение
│   │   │   └── QuestionGenerator.jsx
│   │   ├── App.jsx               # Роутинг
│   │   ├── main.jsx              # Точка входа
│   │   └── index.css             # Стили
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
│
├── 📁 backend/                    # FastAPI сервер
│   ├── routes/                   # API эндпоинты
│   │   ├── parser.py             # Парсинг PDF/DOCX/PPTX
│   │   ├── llm.py                # Работа с Ollama
│   │   ├── analyzer.py           # Анализ текста
│   │   ├── schedule.py           # Парсинг расписания СГТУ
│   │   ├── documents.py          # CRUD документов
│   │   └── training.py           # Fine-tuning моделей
│   ├── services/                 # Бизнес-логика
│   │   ├── parser_service.py
│   │   ├── ollama_service.py
│   │   └── analyzer_service.py
│   ├── config.py                 # Конфигурация
│   ├── main.py                   # Точка входа FastAPI
│   ├── training_collector.py     # Сбор данных для обучения
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📁 docs/                       # Документация
│   ├── FRONTEND.md               # Документация frontend
│   ├── BACKEND.md                # Документация backend
│   ├── API.md                    # API Reference
│   ├── DEPLOYMENT.md             # Развёртывание
│   └── SCHEDULE_PARSER.md        # Модуль расписания
│
├── 📄 docker-compose.yml         # Оркестрация контейнеров
├── 📄 README.md                  # Основная документация
├── 📄 .env.example               # Пример конфигурации
├── 📄 start.bat                  # Запуск на Windows
├── 📄 stop.bat                   # Остановка
└── 📄 train_model.bat            # Обучение модели
```

## 🚀 Быстрый старт

### Предварительные требования

- **Docker Desktop** 4.0+ (для Windows/Mac) или Docker Engine + Docker Compose (Linux)
- **Git** для клонирования репозитория
- **8GB RAM** минимум (рекомендуется 16GB для Ollama)
- **20GB свободного места** на диске

### Установка за 3 шага

#### 1️⃣ Клонирование и настройка

```bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/studeti.git
cd studeti

# Создайте .env файл (или используйте значения по умолчанию)
# Для Windows:
copy .env.example .env
# Для Linux/Mac:
cp .env.example .env
```

#### 2️⃣ Запуск сервисов

```bash
# Запустите все контейнеры
docker-compose up -d

# Проверьте статус
docker-compose ps
```

#### 3️⃣ Загрузка LLM модели

```bash
# Загрузите Mistral (рекомендуется, ~4GB)
docker exec -it studeti-ollama-1 ollama pull mistral

# Или меньшую модель Gemma (~2GB)
docker exec -it studeti-ollama-1 ollama pull gemma:2b

# Проверьте список моделей
docker exec -it studeti-ollama-1 ollama list
```

### 🎉 Готово! Откройте приложение

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **Ollama**: http://localhost:11434

### Полезные команды

```bash
# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down

# Остановка с удалением данных
docker-compose down -v

# Перезапуск сервиса
docker-compose restart backend

# Вход в контейнер
docker exec -it studeti-backend-1 bash
```

## 📚 Документация сервисов

Подробная документация по каждому модулю:

- **[Frontend Documentation](docs/FRONTEND.md)** — архитектура React приложения, компоненты, стилизация
- **[Backend Documentation](docs/BACKEND.md)** — API эндпоинты, сервисы, модели данных
- **[API Reference](docs/API.md)** — полное описание REST API с примерами
- **[Schedule Parser](docs/SCHEDULE_PARSER.md)** — парсер расписания СГТУ, структура данных
- **[Deployment Guide](docs/DEPLOYMENT.md)** — развёртывание на production сервере

## 💻 Технологический стек

### Frontend

| Технология | Версия | Назначение |
|------------|--------|------------|
| **React** | 18.2.0 | UI фреймворк |
| **Vite** | 5.0.8 | Сборщик и dev-сервер |
| **Tailwind CSS** | 3.4.1 | CSS фреймворк |
| **React Router** | 6.21.3 | Клиентский роутинг |
| **Axios** | 1.6.5 | HTTP клиент |
| **Lucide React** | 0.314.0 | Иконки |

### Backend

| Технология | Версия | Назначение |
|------------|--------|------------|
| **FastAPI** | 0.109.0 | Web фреймворк |
| **Uvicorn** | 0.27.0 | ASGI сервер |
| **Python** | 3.11 | Язык программирования |
| **Pydantic** | 2.5.3 | Валидация данных |
| **HTTPX** | 0.26.0 | Async HTTP клиент |
| **BeautifulSoup4** | 4.12.2 | HTML парсинг |
| **PDFPlumber** | 0.10.3 | PDF обработка |

### AI/ML

| Технология | Назначение |
|------------|------------|
| **Ollama** | Локальный inference для LLM |
| **Mistral 7B** | Основная модель для сокращения |
| **Gemma 2B** | Легковесная альтернатива |
| **Fine-tuning** | Дообучение на пользовательских данных |

### Infrastructure

| Сервис | Образ | Порт | Назначение |
|--------|-------|------|------------|
| Frontend | custom | 5173 | React приложение |
| Backend | custom | 8000 | FastAPI сервер |
| Ollama | ollama/ollama | 11434 | LLM inference |
| PostgreSQL | postgres:15-alpine | 5432 | Реляционная БД |
| Redis | redis:7-alpine | 6379 | Кэш и очереди |

## 🔧 Локальная разработка

### Требования для разработки

- **Python 3.11+**
- **Node.js 18+**
- **npm 9+**
- **Git**

### Backend разработка

```bash
# Переход в директорию
cd backend

# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate
# Активация (Linux/Mac)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск dev сервера с hot-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Проверка работы
curl http://localhost:8000/health
```

### Frontend разработка

```bash
# Переход в директорию
cd frontend

# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev

# Сборка production
npm run build

# Preview production сборки
npm run preview
```

### Переменные окружения

Создайте `.env` файл в корне проекта:

```env
# Backend
OLLAMA_URL=http://localhost:11434
DATABASE_URL=postgresql://user:password@localhost:5432/studentdb
REDIS_URL=redis://localhost:6379

# Frontend (VITE_* префикс обязателен)
VITE_API_URL=http://localhost:8000
```

## 📖 Основные API эндпоинты

### Парсер документов

```http
POST /api/parser/upload
Content-Type: multipart/form-data

file: document.pdf
```

### Сокращение текста

```http
POST /api/llm/summarize
Content-Type: application/json

{
  "text": "Длинный текст для сокращения...",
  "ratio": 0.3,
  "model": "mistral"
}
```

### Расписание СГТУ

```http
GET /api/schedule/groups
GET /api/schedule/{group_code}
```

**Полная документация**: http://localhost:8000/docs

## 🎨 Дизайн система

### Цветовая палитра

```css
/* Основные цвета */
--primary: #0a0a0a;           /* Фон */
--secondary: #1a1a1a;         /* Карточки */
--tertiary: #2a2a2a;          /* Элементы */

/* Акценты */
--accent-cyan: #00d9ff;       /* Основной акцент */
--accent-purple: #a855f7;     /* Вторичный */
--accent-pink: #ec4899;       /* Градиенты */

/* Текст */
--text-primary: #ffffff;      /* Основной */
--text-secondary: #a0a0a0;    /* Вторичный */
--text-muted: #6b7280;        /* Приглушённый */

/* Границы */
--border: #2d2d2d;            /* Borders */
```

### Компоненты UI

- **Glass Card** — полупрозрачные карточки с backdrop-blur
- **Gradient Buttons** — кнопки с градиентами
- **Animated Icons** — анимированные иконки Lucide
- **Mobile Burger Menu** — адаптивная навигация

### Адаптивность

```css
/* Breakpoints */
sm: 640px   /* Мобильные устройства */
md: 768px   /* Планшеты */
lg: 1024px  /* Ноутбуки */
xl: 1280px  /* Десктопы */
2xl: 1536px /* Широкие экраны */
```

## 📝 Roadmap развития

### ✅ Версия 1.0 (Выпущена)
- [x] Парсер PDF документов
- [x] Интеграция с Ollama
- [x] Сокращение текста через LLM
- [x] Базовый UI с тёмной темой
- [x] Docker Compose setup

### ✅ Версия 2.0 (Текущая)
- [x] Парсинг расписания СГТУ
- [x] Группировка по специальностям
- [x] Мобильная адаптация
- [x] Система обучения моделей
- [x] Анализатор текста
- [x] Генератор вопросов

### 🚧 Версия 2.1 (В разработке)
- [ ] Уведомления о парах через Telegram Bot
- [ ] Экспорт расписания в календарь (ICS)
- [ ] Поддержка других университетов
- [ ] Темы оформления (светлая/тёмная)

### 🔮 Версия 3.0 (Планируется)
- [ ] Мобильное приложение (React Native)
- [ ] Система заметок и конспектов
- [ ] Коллаборация между студентами
- [ ] Интеграция с облачными LLM (GPT-4, Claude)
- [ ] Mind Map генератор
- [ ] Режим Pomodoro для обучения

## 🤝 Участие в разработке

### Как внести вклад

1. **Fork** репозиторий
2. Создайте **feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit** изменения (`git commit -m 'Add some AmazingFeature'`)
4. **Push** в branch (`git push origin feature/AmazingFeature`)
5. Откройте **Pull Request**

### Стандарты кода

- **Python**: PEP 8, type hints, docstrings
- **JavaScript**: ESLint, Prettier
- **Commits**: Conventional Commits (feat:, fix:, docs:, etc.)

### Отчёты об ошибках

Используйте GitHub Issues с метками:
- `bug` — ошибки
- `enhancement` — улучшения
- `documentation` — документация
- `question` — вопросы

## 📄 Лицензия

Проект распространяется под лицензией **MIT License**.

```
MIT License

Copyright (c) 2024 Student Helper

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

## 📞 Контакты и поддержка

- **GitHub**: [github.com/yourusername/studeti](https://github.com)
- **Issues**: [github.com/yourusername/studeti/issues](https://github.com)
- **Email**: support@studenthelper.dev

---

<div align="center">
  <strong>Сделано с ❤️ для студентов</strong>
  <br>
  <sub>Student Helper © 2024</sub>
</div>
