from fastapi import APIRouter
from pydantic import BaseModel
from services.analyzer_service import AnalyzerService

router = APIRouter()
analyzer_service = AnalyzerService()

class AnalyzeRequest(BaseModel):
    text: str

@router.post("/stats")
async def analyze_text(request: AnalyzeRequest):
    """
    Анализ текста: статистика, ключевые термины
    """
    stats = analyzer_service.get_statistics(request.text)
    key_terms = analyzer_service.extract_key_terms(request.text)
    
    return {
        **stats,
        "key_terms": key_terms
    }
