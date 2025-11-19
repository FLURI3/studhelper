from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.ollama_service import OllamaService
from training_collector import collector
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
ollama_service = OllamaService()

class SummarizeRequest(BaseModel):
    text: str
    ratio: int = 50
    model: str = "mistral"
    custom_prompt: str = ""

class QuestionRequest(BaseModel):
    text: str
    count: int = 5
    model: str = "mistral"

@router.post("/summarize")
async def summarize_text(request: SummarizeRequest):
    """
    Сократить текст с помощью LLM
    """
    logger.info(f"Summarize request: {len(request.text)} chars, ratio: {request.ratio}%, model: {request.model}")
    
    # Проверка здоровья Ollama
    is_healthy = await ollama_service.check_health()
    if not is_healthy:
        raise HTTPException(
            status_code=503, 
            detail="Ollama недоступен. Убедитесь, что контейнер ollama запущен."
        )
    
    # Проверка доступности модели
    models = await ollama_service.list_models()
    if not models:
        raise HTTPException(
            status_code=503,
            detail=f"Модели не загружены в Ollama. Выполните: docker exec studeti-ollama-1 ollama pull {request.model}"
        )
    
    logger.info(f"Available models: {models}")
    
    try:
        result = await ollama_service.summarize(
            text=request.text,
            ratio=request.ratio,
            model=request.model,
            custom_prompt=request.custom_prompt
        )
        
        summary = result["summary"]
        reasoning = result["reasoning"]
        
        logger.info(f"Summarization successful. Result length: {len(summary)} chars")
        
        actual_ratio = round(len(summary) / len(request.text) * 100, 1)
        
        # Сохраняем удачный пример для обучения
        if abs(actual_ratio - request.ratio) <= 5:
            collector.add_example(
                original_text=request.text,
                summary=summary,
                ratio=request.ratio,
                model=request.model,
                custom_prompt=request.custom_prompt
            )
        
        return {
            "summary": summary,
            "reasoning": reasoning,
            "original_length": len(request.text),
            "summary_length": len(summary),
            "compression_ratio": actual_ratio
        }
    except Exception as e:
        logger.error(f"Error summarizing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/questions")
async def generate_questions(request: QuestionRequest):
    """
    Генерировать вопросы из текста
    """
    logger.info(f"Questions request: {request.count} questions from {len(request.text)} chars")
    
    try:
        questions = await ollama_service.generate_questions(
            text=request.text,
            count=request.count,
            model=request.model
        )
        
        logger.info(f"Generated {len(questions)} questions successfully")
        return {"questions": questions}
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")
