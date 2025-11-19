from fastapi import APIRouter, UploadFile, File, HTTPException
from services.parser_service import ParserService
import os

router = APIRouter()
parser_service = ParserService()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Загрузить и распарсить документ
    """
    # Validate file type
    allowed_extensions = ['.pdf', '.pptx', '.docx', '.doc', '.txt', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Parse based on file type
    try:
        if file_ext == '.pdf':
            text = await parser_service.parse_pdf(content)
        elif file_ext in ['.pptx']:
            text = await parser_service.parse_pptx(content)
        elif file_ext in ['.docx', '.doc']:
            text = await parser_service.parse_docx(content)
        elif file_ext == '.txt':
            text = content.decode('utf-8', errors='ignore')
        elif file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            text = await parser_service.parse_image(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        return {
            "filename": file.filename,
            "text": text,
            "length": len(text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing file: {str(e)}")
