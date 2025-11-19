import httpx
import logging
import asyncio
import os

logger = logging.getLogger(__name__)

REQUIRED_MODELS = [
    "llama3.2:1b",  # Быстрая модель
    "phi3:mini",    # Альтернативная быстрая модель
    "mistral",      # Основная модель
    "summarizer:v4",
    "summarizer:v3"
]

async def check_and_pull_models():
    """Проверить и загрузить необходимые модели при старте"""
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    logger.info(f"Checking Ollama models at {ollama_url}")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Проверяем доступность Ollama
            try:
                response = await client.get(f"{ollama_url}/api/tags")
                if response.status_code != 200:
                    logger.warning("Ollama is not available yet, will retry later")
                    return
            except Exception as e:
                logger.warning(f"Ollama not ready: {e}")
                return
            
            # Получаем список установленных моделей
            installed_models = []
            models_data = response.json().get("models", [])
            for model in models_data:
                installed_models.append(model["name"])
            
            logger.info(f"Installed models: {installed_models}")
            
            # Проверяем каждую требуемую модель
            for model in REQUIRED_MODELS:
                model_installed = any(model in installed for installed in installed_models)
                
                if not model_installed:
                    logger.info(f"Model {model} not found, pulling...")
                    try:
                        # Запускаем загрузку модели
                        pull_response = await client.post(
                            f"{ollama_url}/api/pull",
                            json={"name": model, "stream": False},
                            timeout=600.0  # 10 минут на загрузку
                        )
                        
                        if pull_response.status_code == 200:
                            logger.info(f"✓ Model {model} pulled successfully")
                        else:
                            logger.error(f"✗ Failed to pull model {model}: {pull_response.text}")
                    except Exception as e:
                        logger.error(f"✗ Error pulling model {model}: {e}")
                else:
                    logger.info(f"✓ Model {model} already installed")
    
    except Exception as e:
        logger.error(f"Error checking models: {e}")

async def wait_for_ollama_and_pull_models(max_retries=10, delay=5):
    """Ждём запуска Ollama и загружаем модели"""
    for attempt in range(max_retries):
        logger.info(f"Attempt {attempt + 1}/{max_retries} to check Ollama and models")
        await check_and_pull_models()
        
        # Проверяем, все ли модели загружены
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{ollama_url}/api/tags")
                if response.status_code == 200:
                    installed = [m["name"] for m in response.json().get("models", [])]
                    all_installed = all(
                        any(req in inst for inst in installed) 
                        for req in REQUIRED_MODELS
                    )
                    
                    if all_installed:
                        logger.info("✓ All required models are installed")
                        return
        except:
            pass
        
        if attempt < max_retries - 1:
            logger.info(f"Waiting {delay} seconds before next attempt...")
            await asyncio.sleep(delay)
    
    logger.warning("Could not verify all models after maximum retries")
