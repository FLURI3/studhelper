from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import parser, llm, analyzer, documents, training, schedule, auth
import logging
import asyncio
from contextlib import asynccontextmanager
from check_models import wait_for_ollama_and_pull_models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: проверяем и загружаем модели
    logger.info("Starting up - checking Ollama models...")
    asyncio.create_task(wait_for_ollama_and_pull_models())
    yield
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Student Helper API",
    description="API для помощи студентам в обучении",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Routes
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(parser.router, prefix="/api/parser", tags=["parser"])
app.include_router(llm.router, prefix="/api/llm", tags=["llm"])
app.include_router(analyzer.router, prefix="/api/analyzer", tags=["analyzer"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])
app.include_router(training.router, prefix="/api/training", tags=["training"])
app.include_router(schedule.router, prefix="/api", tags=["schedule"])

@app.get("/")
async def root():
    return {
        "message": "Student Helper API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/ollama/status")
async def ollama_status():
    """Проверить статус Ollama и список моделей"""
    from services.ollama_service import OllamaService
    ollama = OllamaService()
    
    is_healthy = await ollama.check_health()
    models = await ollama.list_models()
    
    return {
        "status": "healthy" if is_healthy else "unavailable",
        "models": models,
        "message": "Ollama работает" if is_healthy else "Ollama недоступен. Запустите: docker-compose up ollama"
    }
