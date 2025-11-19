# 🔧 Backend Documentation

> Документация по архитектуре, API эндпоинтам и разработке FastAPI приложения Student Helper

## 📋 Содержание

- [Обзор](#обзор)
- [Архитектура](#архитектура)
- [Структура проекта](#структура-проекта)
- [API Routes](#api-routes)
- [Services](#services)
- [База данных](#база-данных)
- [Интеграция с Ollama](#интеграция-с-ollama)
- [Разработка](#разработка)

## 🎯 Обзор

Backend приложение построено на FastAPI - современном асинхронном Python фреймворке.

### Технологический стек

| Технология | Версия | Назначение |
|------------|--------|------------|
| **Python** | 3.11 | Язык программирования |
| **FastAPI** | 0.109.0 | Web фреймворк |
| **Uvicorn** | 0.27.0 | ASGI сервер |
| **Pydantic** | 2.5.3 | Валидация данных |
| **HTTPX** | 0.26.0 | HTTP клиент |
| **BeautifulSoup4** | 4.12.2 | HTML парсинг |
| **PDFPlumber** | 0.10.3 | PDF обработка |

### Ключевые особенности

✅ **Async/Await** — асинхронная обработка запросов
✅ **Type Hints** — строгая типизация с Pydantic
✅ **OpenAPI Docs** — автоматическая документация API
✅ **CORS Support** — поддержка cross-origin запросов
✅ **Модульная структура** — разделение на routes и services

## 🏗️ Архитектура

### Layered Architecture

```
┌─────────────────────────────────────┐
│         FastAPI Application          │
│            (main.py)                 │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌─────────┐
│ Routes │ │ Routes │ │ Routes  │
│ Parser │ │  LLM   │ │Schedule │
└────┬───┘ └───┬────┘ └────┬────┘
     │         │           │
     ▼         ▼           ▼
┌─────────┐ ┌──────────┐ ┌──────────┐
│Services │ │ Services │ │ Services │
│ Parser  │ │  Ollama  │ │ Analyzer │
└────┬────┘ └────┬─────┘ └──────────┘
     │           │
     ▼           ▼
┌─────────────────────────┐
│   External Services      │
│  • Ollama (LLM)         │
│  • PostgreSQL           │
│  • Redis                │
│  • SSTU Website         │
└─────────────────────────┘
```

### Request Flow

```
1. Client Request
   ↓
2. FastAPI Router (routes/*.py)
   ↓
3. Request Validation (Pydantic)
   ↓
4. Service Layer (services/*.py)
   ↓
5. External Services / DB
   ↓
6. Response Serialization
   ↓
7. Client Response
```

## 📂 Структура проекта

```
backend/
├── routes/                      # API эндпоинты
│   ├── __init__.py
│   ├── parser.py               # Парсинг документов
│   ├── llm.py                  # Работа с LLM
│   ├── analyzer.py             # Анализ текста
│   ├── schedule.py             # Расписание СГТУ
│   ├── documents.py            # CRUD документов
│   └── training.py             # Fine-tuning моделей
│
├── services/                   # Бизнес-логика
│   ├── __init__.py
│   ├── parser_service.py       # Логика парсинга
│   ├── ollama_service.py       # Работа с Ollama
│   └── analyzer_service.py     # Логика анализа
│
├── models/                     # Pydantic модели (если есть)
│   └── schemas.py
│
├── utils/                      # Утилиты
│   ├── validators.py
│   └── helpers.py
│
├── config.py                   # Конфигурация
├── main.py                     # Точка входа FastAPI
├── training_collector.py       # Сбор обучающих данных
├── check_models.py             # Проверка моделей Ollama
│
├── requirements.txt            # Python зависимости
├── Dockerfile                  # Docker образ
└── .env                        # Переменные окружения
```

## 🛤️ API Routes

### Main Application

**Файл**: `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import parser, llm, analyzer, schedule, documents, training

app = FastAPI(
    title="Student Helper API",
    description="AI-платформа для студентов",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router registration
app.include_router(parser.router, prefix="/api", tags=["Parser"])
app.include_router(llm.router, prefix="/api", tags=["LLM"])
app.include_router(analyzer.router, prefix="/api", tags=["Analyzer"])
app.include_router(schedule.router, prefix="/api", tags=["Schedule"])
app.include_router(documents.router, prefix="/api", tags=["Documents"])
app.include_router(training.router, prefix="/api", tags=["Training"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "2.0.0"}
```

### Parser Routes

**Файл**: `routes/parser.py`

Парсинг документов (PDF, DOCX, PPTX).

**Эндпоинты:**

```python
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.parser_service import ParserService

router = APIRouter()
parser_service = ParserService()

@router.post("/parser/upload")
async def parse_document(file: UploadFile = File(...)):
    """
    Загрузка и парсинг документа
    
    Поддерживаемые форматы: PDF, DOCX, PPTX
    Максимальный размер: 10MB
    
    Returns:
        {
            "filename": str,
            "format": str,
            "text": str,
            "metadata": dict,
            "word_count": int
        }
    """
    if file.size > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large")
    
    allowed_formats = ['.pdf', '.docx', '.pptx']
    file_ext = file.filename.split('.')[-1].lower()
    
    if f'.{file_ext}' not in allowed_formats:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported format. Allowed: {allowed_formats}"
        )
    
    result = await parser_service.parse_file(file)
    return result
```

### LLM Routes

**Файл**: `routes/llm.py`

Работа с локальными LLM через Ollama.

**Эндпоинты:**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services.ollama_service import OllamaService
from training_collector import TrainingCollector

router = APIRouter()
ollama_service = OllamaService()
training_collector = TrainingCollector()

class SummarizeRequest(BaseModel):
    text: str = Field(..., min_length=10, description="Текст для сокращения")
    ratio: float = Field(0.3, ge=0.1, le=0.9, description="Коэффициент сокращения")
    model: str = Field("mistral", description="Модель LLM")

class SummarizeResponse(BaseModel):
    summary: str
    original_length: int
    summary_length: int
    compression_ratio: float
    model: str

@router.post("/llm/summarize", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    """
    Умное сокращение текста через LLM
    
    Args:
        text: Текст для сокращения (минимум 10 символов)
        ratio: Коэффициент сокращения 0.1-0.9 (по умолчанию 0.3)
        model: Модель LLM (mistral, gemma, llama2)
    
    Returns:
        Сокращённый текст с метриками
    """
    try:
        summary = await ollama_service.summarize(
            text=request.text,
            ratio=request.ratio,
            model=request.model
        )
        
        # Сохранение примера для обучения
        await training_collector.add_example(
            input_text=request.text,
            output_text=summary,
            task_type="summarization"
        )
        
        return SummarizeResponse(
            summary=summary,
            original_length=len(request.text),
            summary_length=len(summary),
            compression_ratio=len(summary) / len(request.text),
            model=request.model
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/llm/models")
async def list_models():
    """Список доступных LLM моделей"""
    models = await ollama_service.list_models()
    return {"models": models}
```

### Schedule Routes

**Файл**: `routes/schedule.py`

Парсинг расписания СГТУ.

**Эндпоинты:**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
import re
from datetime import datetime

router = APIRouter()

class Lesson(BaseModel):
    number: str
    time: str
    subject: Optional[str] = None
    teacher: Optional[str] = None
    room: Optional[str] = None
    type: Optional[str] = None

class DaySchedule(BaseModel):
    day: str                    # "Понедельник"
    date: str                   # "17.11.2025"
    day_of_week: int            # 0-6
    lessons: List[Lesson] = []

class GroupSchedule(BaseModel):
    group_code: str
    group_name: str
    schedule_days: List[DaySchedule] = []
    last_updated: Optional[str] = None

class GroupInfo(BaseModel):
    code: str
    name: str

class GroupsResponse(BaseModel):
    groups: List[GroupInfo]
    total: int

@router.get("/schedule/groups", response_model=GroupsResponse)
async def get_all_groups():
    """
    Получить список всех групп СГТУ
    
    Returns:
        {
            "groups": [
                {"code": "74", "name": "ИСП-12"},
                ...
            ],
            "total": 120
        }
    """
    base_url = "http://techn.sstu.ru/schedule/spo_2025"
    groups = []
    
    # Перебор всех возможных кодов групп (cg01.htm - cg99.htm)
    async with httpx.Client(timeout=10.0) as client:
        for code in range(1, 100):
            code_str = str(code).zfill(2)
            url = f"{base_url}/cg{code_str}.htm"
            
            try:
                response = await client.get(url)
                if response.status_code == 200:
                    # Парсинг названия группы из HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    title = soup.find('h2')
                    if title:
                        group_name = title.text.strip()
                        groups.append(GroupInfo(
                            code=code_str,
                            name=group_name
                        ))
            except:
                continue
    
    return GroupsResponse(groups=groups, total=len(groups))

@router.get("/schedule/{group_code}", response_model=GroupSchedule)
async def get_schedule(group_code: str):
    """
    Получить расписание конкретной группы
    
    Args:
        group_code: Код группы (например, "74" для ИСП-12)
    
    Returns:
        Полное расписание группы на все недели
    """
    base_url = "http://techn.sstu.ru/schedule/spo_2025"
    url = f"{base_url}/cg{group_code}.htm"
    
    try:
        # Синхронный запрос для стабильности
        client = httpx.Client(timeout=10.0)
        response = client.get(url)
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=404, 
                detail=f"Группа {group_code} не найдена"
            )
        
        # Парсинг HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Название группы
        title = soup.find('h2')
        group_name = title.text.strip() if title else f"Группа {group_code}"
        
        # Таблица расписания
        table = soup.find('table', class_='inf')
        if not table:
            return GroupSchedule(
                group_code=group_code,
                group_name=group_name,
                schedule_days=[],
                last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
        
        schedule_days = []
        current_day = None
        current_date = None
        current_day_of_week = None
        
        # Парсинг строк таблицы
        rows = table.find_all('tr')[1:]  # Пропуск заголовка
        
        for row in rows:
            cells = row.find_all('td')
            if not cells:
                continue
            
            # Проверка на новый день (rowspan ячейка)
            first_cell = cells[0]
            if first_cell.has_attr('rowspan'):
                # Новый день
                day_text = first_cell.get_text(strip=True)
                
                # Извлечение даты
                date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', day_text)
                if date_match:
                    current_date = date_match.group(1)
                    # Вычисление дня недели
                    date_obj = datetime.strptime(current_date, "%d.%m.%Y")
                    current_day_of_week = date_obj.weekday()
                
                # Извлечение названия дня
                day_name_match = re.search(r'([А-Яа-я]+)', day_text)
                current_day = day_name_match.group(1) if day_name_match else day_text
                
                # Создание нового дня
                day_schedule = DaySchedule(
                    day=current_day,
                    date=current_date,
                    day_of_week=current_day_of_week,
                    lessons=[]
                )
                schedule_days.append(day_schedule)
                
                # Первая пара этого дня
                time_cell_idx = 1
            else:
                # Продолжение текущего дня
                time_cell_idx = 0
            
            if len(cells) <= time_cell_idx:
                continue
            
            # Парсинг времени пары
            time_text = cells[time_cell_idx].get_text(strip=True)
            time_match = re.search(
                r'(\d{1,2}[\.:]\d{2}[-–]\d{1,2}[\.:]\d{2})', 
                time_text
            )
            if not time_match:
                continue
            
            lesson_time = time_match.group(1).replace('.', ':')
            
            # Номер пары
            number_match = re.search(r'(\d+)', time_text)
            lesson_number = number_match.group(1) if number_match else "0"
            
            # Предмет, кабинет, преподаватель
            lesson_cell = cells[time_cell_idx + 1] if len(cells) > time_cell_idx + 1 else None
            
            if lesson_cell:
                # Извлечение данных из <a> тегов с классами
                subject = None
                room = None
                teacher = None
                
                z1 = lesson_cell.find('a', class_='z1')
                if z1:
                    subject = z1.get_text(strip=True)
                
                z2 = lesson_cell.find('a', class_='z2')
                if z2:
                    room = z2.get_text(strip=True)
                
                z3 = lesson_cell.find('a', class_='z3')
                if z3:
                    teacher = z3.get_text(strip=True)
                
                # Добавление пары
                lesson = Lesson(
                    number=lesson_number,
                    time=lesson_time,
                    subject=subject,
                    teacher=teacher,
                    room=room,
                    type="Лекция"  # TODO: определение типа
                )
                
                if schedule_days:
                    schedule_days[-1].lessons.append(lesson)
        
        client.close()
        
        return GroupSchedule(
            group_code=group_code,
            group_name=group_name,
            schedule_days=schedule_days,
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, 
            detail="Таймаут при подключении к сайту СГТУ"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Ошибка парсинга: {str(e)}"
        )
```

### Analyzer Routes

**Файл**: `routes/analyzer.py`

Анализ текста (статистика, сложность, ключевые слова).

```python
from fastapi import APIRouter
from pydantic import BaseModel
from services.analyzer_service import AnalyzerService

router = APIRouter()
analyzer_service = AnalyzerService()

class AnalyzeRequest(BaseModel):
    text: str

class TextStats(BaseModel):
    characters: int
    words: int
    sentences: int
    paragraphs: int
    avg_word_length: float
    avg_sentence_length: float
    readability_score: float
    language: str

@router.post("/analyzer/stats", response_model=TextStats)
async def analyze_text(request: AnalyzeRequest):
    """Статистический анализ текста"""
    stats = analyzer_service.calculate_stats(request.text)
    return stats
```

### Training Routes

**Файл**: `routes/training.py`

Управление обучением моделей.

```python
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import json
import os

router = APIRouter()

class TrainingExample(BaseModel):
    input_text: str
    output_text: str
    task_type: str
    timestamp: str

class TrainingStats(BaseModel):
    total_examples: int
    examples_by_type: dict
    last_training: str

@router.get("/training/examples", response_model=List[TrainingExample])
async def get_training_examples():
    """Получить собранные обучающие примеры"""
    if not os.path.exists('training_examples.json'):
        return []
    
    with open('training_examples.json', 'r', encoding='utf-8') as f:
        examples = json.load(f)
    return examples

@router.post("/training/start")
async def start_training():
    """Запустить процесс обучения модели"""
    # TODO: Реализация fine-tuning
    return {"status": "started", "message": "Training job scheduled"}

@router.get("/training/stats", response_model=TrainingStats)
async def get_training_stats():
    """Статистика по обучению"""
    # TODO: Подсчёт метрик
    return TrainingStats(
        total_examples=0,
        examples_by_type={},
        last_training="Never"
    )
```

## 🔌 Services

### Ollama Service

**Файл**: `services/ollama_service.py`

```python
import httpx
from typing import Optional

class OllamaService:
    def __init__(self):
        self.base_url = "http://ollama:11434"
    
    async def summarize(
        self, 
        text: str, 
        ratio: float = 0.3, 
        model: str = "mistral"
    ) -> str:
        """
        Сокращение текста через Ollama
        
        Args:
            text: Исходный текст
            ratio: Коэффициент сокращения (0.1 - 0.9)
            model: Модель LLM
        
        Returns:
            Сокращённый текст
        """
        target_words = int(len(text.split()) * ratio)
        
        prompt = f"""Сократи следующий текст до примерно {target_words} слов, 
сохранив главные идеи и ключевую информацию:

{text}

Сокращённый текст:"""
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                }
            )
            
            result = response.json()
            return result.get("response", "")
    
    async def list_models(self) -> list:
        """Список доступных моделей"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/tags")
            data = response.json()
            return [m["name"] for m in data.get("models", [])]
```

### Parser Service

**Файл**: `services/parser_service.py`

```python
import pdfplumber
from docx import Document
from pptx import Presentation
from typing import Dict

class ParserService:
    async def parse_file(self, file) -> Dict:
        """Универсальный парсинг документов"""
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower()
        
        if file_ext == 'pdf':
            return self._parse_pdf(content)
        elif file_ext == 'docx':
            return self._parse_docx(content)
        elif file_ext == 'pptx':
            return self._parse_pptx(content)
        else:
            raise ValueError(f"Unsupported format: {file_ext}")
    
    def _parse_pdf(self, content: bytes) -> Dict:
        """Парсинг PDF"""
        import io
        pdf_file = io.BytesIO(content)
        text = ""
        
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n\n"
        
        return {
            "text": text.strip(),
            "format": "pdf",
            "word_count": len(text.split())
        }
    
    def _parse_docx(self, content: bytes) -> Dict:
        """Парсинг DOCX"""
        import io
        doc_file = io.BytesIO(content)
        doc = Document(doc_file)
        
        text = "\n".join([para.text for para in doc.paragraphs])
        
        return {
            "text": text.strip(),
            "format": "docx",
            "word_count": len(text.split())
        }
    
    def _parse_pptx(self, content: bytes) -> Dict:
        """Парсинг PPTX"""
        import io
        ppt_file = io.BytesIO(content)
        prs = Presentation(ppt_file)
        
        text = ""
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text"):
                    text += shape.text + "\n"
        
        return {
            "text": text.strip(),
            "format": "pptx",
            "word_count": len(text.split())
        }
```

### Analyzer Service

**Файл**: `services/analyzer_service.py`

```python
import re
from typing import Dict

class AnalyzerService:
    def calculate_stats(self, text: str) -> Dict:
        """Подсчёт статистики текста"""
        # Базовые метрики
        characters = len(text)
        words = len(text.split())
        sentences = len(re.split(r'[.!?]+', text))
        paragraphs = len(text.split('\n\n'))
        
        # Средние значения
        avg_word_length = characters / words if words > 0 else 0
        avg_sentence_length = words / sentences if sentences > 0 else 0
        
        # Индекс читаемости Flesch
        readability = self._calculate_flesch(words, sentences, characters)
        
        return {
            "characters": characters,
            "words": words,
            "sentences": sentences,
            "paragraphs": paragraphs,
            "avg_word_length": round(avg_word_length, 2),
            "avg_sentence_length": round(avg_sentence_length, 2),
            "readability_score": round(readability, 2),
            "language": "ru"
        }
    
    def _calculate_flesch(self, words: int, sentences: int, characters: int) -> float:
        """Индекс читаемости Flesch (адаптированный для русского)"""
        if words == 0 or sentences == 0:
            return 0
        
        syllables = characters / 3  # Приближённый подсчёт слогов
        
        score = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
        return max(0, min(100, score))
```

## 🗄️ База данных

### PostgreSQL Models

**Файл**: `models/schemas.py`

```python
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    format = Column(String(10), nullable=False)
    text = Column(Text, nullable=False)
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class TrainingData(Base):
    __tablename__ = "training_data"
    
    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    output_text = Column(Text, nullable=False)
    task_type = Column(String(50), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
```

### Database Connection

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://user:password@postgres:5432/studentdb"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 🤖 Интеграция с Ollama

### Настройка подключения

```python
# config.py
import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
OLLAMA_DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
OLLAMA_TIMEOUT = 60  # seconds
```

### Проверка моделей

**Файл**: `check_models.py`

```python
import httpx
import sys

async def check_ollama_models():
    """Проверка доступности Ollama и списка моделей"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                
                print(f"✅ Ollama доступен")
                print(f"📦 Установлено моделей: {len(models)}")
                
                for model in models:
                    name = model.get("name")
                    size = model.get("size", 0) / (1024**3)  # GB
                    print(f"   - {name} ({size:.2f} GB)")
                
                return True
            else:
                print("❌ Ollama недоступен")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка подключения к Ollama: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(check_ollama_models())
```

### Training Collector

**Файл**: `training_collector.py`

```python
import json
import os
from datetime import datetime
from typing import Dict

class TrainingCollector:
    def __init__(self, file_path: str = "training_examples.json"):
        self.file_path = file_path
    
    async def add_example(
        self, 
        input_text: str, 
        output_text: str, 
        task_type: str = "summarization"
    ):
        """Добавить пример для обучения"""
        example = {
            "input_text": input_text,
            "output_text": output_text,
            "task_type": task_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Загрузка существующих примеров
        examples = []
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                examples = json.load(f)
        
        # Добавление нового
        examples.append(example)
        
        # Сохранение
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(examples, f, ensure_ascii=False, indent=2)
        
        # Автозапуск обучения при накоплении 100 примеров
        if len(examples) >= 100 and len(examples) % 100 == 0:
            await self._trigger_training()
    
    async def _trigger_training(self):
        """Запуск процесса обучения"""
        # TODO: Интеграция с Ollama fine-tuning
        print("🎓 Накоплено 100 примеров. Запуск обучения...")
```

## 🛠️ Разработка

### Локальный запуск

```bash
cd backend

# Создание venv
python -m venv venv
venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск dev сервера
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Requirements.txt

```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
httpx==0.26.0
beautifulsoup4==4.12.2
pdfplumber==0.10.3
python-docx==1.1.0
python-pptx==0.6.23
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
redis==5.0.1
```

### Environment Variables

```env
# .env
OLLAMA_URL=http://localhost:11434
DATABASE_URL=postgresql://user:password@localhost:5432/studentdb
REDIS_URL=redis://localhost:6379
```

### Testing

```bash
# Ручное тестирование эндпоинтов
curl http://localhost:8000/health

# Swagger UI
# http://localhost:8000/docs

# ReDoc
# http://localhost:8000/redoc
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Использование
logger.info("Запрос обработан успешно")
logger.error("Ошибка при парсинге", exc_info=True)
```

---

**Автор**: Student Helper Team  
**Последнее обновление**: 19.11.2025
