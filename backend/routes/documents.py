from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_documents():
    """
    Получить список всех документов
    """
    return {"documents": []}

@router.post("/save")
async def save_document():
    """
    Сохранить документ
    """
    return {"status": "saved"}
