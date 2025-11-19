from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import os
import json
import subprocess
import threading
from typing import List, Dict, Optional
from datetime import datetime

router = APIRouter()

# Глобальное состояние обучения
training_status = {
    "is_training": False,
    "progress": 0,
    "stage": "",
    "log": [],
    "started_at": None,
    "model_name": None,
    "error": None
}

class TrainingStatsResponse(BaseModel):
    total_examples: int
    auto_collected: int
    manual_examples: int
    auto_train_enabled: bool
    auto_train_threshold: int
    current_progress: int
    progress_percentage: float
    trained_models: List[str]
    latest_model: Optional[str] = None
    next_training_in: int

class TrainingStatusResponse(BaseModel):
    is_training: bool
    progress: int
    stage: str
    log: List[str]
    started_at: Optional[str] = None
    model_name: Optional[str] = None
    error: Optional[str] = None

class StartTrainingRequest(BaseModel):
    examples: List[Dict]

@router.get("/stats", response_model=TrainingStatsResponse)
async def get_training_stats():
    """Получить статистику обучения и доступные модели"""
    
    # Подсчитываем примеры
    jsonl_path = "training_data.jsonl"
    auto_collected = 0
    if os.path.exists(jsonl_path):
        with open(jsonl_path, "r", encoding="utf-8") as f:
            auto_collected = sum(1 for _ in f)
    
    manual_examples = 0
    json_path = "../training_examples.json"
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                manual_examples = len(json.load(f))
        except:
            pass
    
    # Получаем настройки автообучения
    auto_train_enabled = os.getenv("AUTO_TRAIN", "false").lower() == "true"
    threshold = int(os.getenv("AUTO_TRAIN_THRESHOLD", "20"))
    
    # Читаем последний счетчик обучения
    last_train_count = 0
    collector_state = "training_state.json"
    if os.path.exists(collector_state):
        try:
            with open(collector_state, "r") as f:
                state = json.load(f)
                last_train_count = state.get("last_train_count", 0)
        except:
            pass
    
    current_progress = auto_collected - last_train_count
    progress_pct = min((current_progress / threshold * 100) if threshold > 0 else 0, 100)
    next_training_in = max(0, threshold - current_progress)
    
    # Получаем список обученных моделей через Ollama API
    trained_models = []
    latest_model = None
    
    try:
        import httpx
        ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{ollama_url}/api/tags")
            
            if response.status_code == 200:
                data = response.json()
                for model in data.get("models", []):
                    model_name = model.get("name", "")
                    if "summarizer" in model_name.lower():
                        trained_models.append(model_name)
                
                # Находим последнюю версию
                if trained_models:
                    versions = []
                    for model in trained_models:
                        if ":v" in model:
                            try:
                                version = int(model.split(":v")[1])
                                versions.append((version, model))
                            except:
                                pass
                    
                    if versions:
                        latest_model = max(versions, key=lambda x: x[0])[1]
    except:
        pass
    
    return TrainingStatsResponse(
        total_examples=auto_collected + manual_examples,
        auto_collected=auto_collected,
        manual_examples=manual_examples,
        auto_train_enabled=auto_train_enabled,
        auto_train_threshold=threshold,
        current_progress=current_progress,
        progress_percentage=round(progress_pct, 1),
        trained_models=trained_models,
        latest_model=latest_model,
        next_training_in=next_training_in
    )

@router.get("/status", response_model=TrainingStatusResponse)
async def get_training_status():
    """Получить текущий статус обучения"""
    return TrainingStatusResponse(**training_status)

def run_training_process(examples: List[Dict]):
    """Запуск процесса обучения в фоновом потоке"""
    global training_status
    
    try:
        import httpx
        
        training_status["is_training"] = True
        training_status["progress"] = 0
        training_status["log"] = []
        training_status["error"] = None
        training_status["started_at"] = datetime.now().isoformat()
        
        # Сохраняем примеры в файл
        training_status["stage"] = "Сохранение примеров"
        training_status["log"].append("📝 Сохранение примеров для обучения...")
        
        examples_file = "training_examples_web.json"
        with open(examples_file, "w", encoding="utf-8") as f:
            json.dump(examples, f, ensure_ascii=False, indent=2)
        
        training_status["progress"] = 10
        training_status["log"].append(f"✅ Сохранено {len(examples)} примеров")
        
        # Определяем следующую версию модели через Ollama API
        training_status["stage"] = "Определение версии модели"
        training_status["log"].append("🔍 Поиск существующих моделей...")
        
        ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        
        max_version = 0
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(f"{ollama_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("models", []):
                        model_name_tag = model.get("name", "")
                        if "summarizer:v" in model_name_tag:
                            try:
                                version = int(model_name_tag.split(":v")[1])
                                max_version = max(max_version, version)
                            except:
                                pass
        except Exception as e:
            training_status["log"].append(f"⚠️ Не удалось получить список моделей: {e}")
        
        new_version = max_version + 1
        model_name = f"summarizer:v{new_version}"
        training_status["model_name"] = model_name
        training_status["progress"] = 20
        training_status["log"].append(f"🎯 Будет создана модель: {model_name}")
        
        # Генерация Modelfile
        training_status["stage"] = "Генерация Modelfile"
        training_status["log"].append("🔨 Генерация конфигурации модели...")
        
        # Создаём Modelfile по спецификации Ollama
        # ВАЖНО: Используем полное имя модели с тегом :latest
        modelfile_lines = [
            "FROM mistral:latest",
            "",
            "# Параметры оптимизации",
            "PARAMETER temperature 0.3",
            "PARAMETER top_p 0.9",
            "PARAMETER top_k 40",
            "PARAMETER repeat_penalty 1.15",
            "PARAMETER num_predict 4096",
            "",
            'SYSTEM """Ты - профессиональный редактор текстов. Твоя задача - сокращать русские тексты, точно следуя заданному проценту сокращения. Сохраняй все команды, цифры и технические термины. Пиши ТОЛЬКО сокращённый текст без пояснений."""',
            ""
        ]
        
        # Добавляем примеры обучения
        for i, example in enumerate(examples[:20], 1):  # Максимум 20 примеров
            original = example.get("original", "").strip()
            summary = example.get("summary", "").strip()
            ratio = example.get("ratio", 50)
            
            if original and summary and len(original) > 20 and len(summary) > 10:
                # Убираем переносы строк и лишние пробелы
                original_clean = ' '.join(original.split())
                summary_clean = ' '.join(summary.split())
                
                prompt = f"Сократи текст до {ratio}% от оригинала: {original_clean}"
                
                modelfile_lines.append(f'MESSAGE user """{prompt}"""')
                modelfile_lines.append(f'MESSAGE assistant """{summary_clean}"""')
                modelfile_lines.append("")
        
        modelfile_content = "\n".join(modelfile_lines)
        
        modelfile_path = "Modelfile.web"
        with open(modelfile_path, "w", encoding="utf-8") as f:
            f.write(modelfile_content)
        
        training_status["progress"] = 40
        training_status["log"].append(f"✅ Создан Modelfile с {min(len(examples), 30)} примерами")
        
        # Создание модели через Ollama API
        training_status["stage"] = "Обучение модели"
        training_status["log"].append(f"🚀 Запуск обучения модели {model_name}...")
        training_status["log"].append("⏳ Это займёт 5-10 минут, ожидайте...")
        
        training_status["progress"] = 50
        
        # Логируем Modelfile для отладки
        training_status["log"].append(f"📄 Размер Modelfile: {len(modelfile_content)} символов")
        training_status["log"].append(f"📄 Начало: {modelfile_content[:100]}")
        
        # ВАЖНО: Ollama API требует указать путь к файлу ИЛИ содержимое
        # Попробуем загрузить как path (файл должен быть доступен Ollama)
        # Так как мы в разных контейнерах, используем modelfile напрямую
        
        with httpx.Client(timeout=600.0) as client:
            # Проверяем, что базовая модель существует
            tags_response = client.get(f"{ollama_url}/api/tags")
            if tags_response.status_code == 200:
                available_models = [m.get("name", "") for m in tags_response.json().get("models", [])]
                training_status["log"].append(f"📦 Доступные модели: {', '.join(available_models[:3])}...")
                
                # Проверяем наличие mistral
                if not any("mistral" in m for m in available_models):
                    raise Exception("Базовая модель 'mistral' не найдена в Ollama")
            
            # ВАЖНО: Новая версия Ollama API использует структурированный JSON
            # вместо текстового Modelfile. Формируем правильный payload
            
            # Парсим примеры для messages
            messages = []
            for i, example in enumerate(examples[:20], 1):
                original = example.get("original", "").strip()
                summary = example.get("summary", "").strip()
                ratio = example.get("ratio", 50)
                
                if original and summary and len(original) > 20 and len(summary) > 10:
                    original_clean = ' '.join(original.split())
                    summary_clean = ' '.join(summary.split())
                    
                    messages.append({
                        "role": "user",
                        "content": f"Сократи текст до {ratio}% от оригинала: {original_clean}"
                    })
                    messages.append({
                        "role": "assistant", 
                        "content": summary_clean
                    })
            
            training_status["log"].append(f"📦 Подготовлено {len(messages)//2} пар обучающих примеров")
            
            payload = {
                "name": model_name,
                "from": "mistral:latest",
                "system": "Ты - профессиональный редактор текстов. Твоя задача - сокращать русские тексты, точно следуя заданному проценту сокращения. Сохраняй все команды, цифры и технические термины. Пиши ТОЛЬКО сокращённый текст без пояснений.",
                "parameters": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "top_k": 40,
                    "repeat_penalty": 1.15,
                    "num_predict": 4096
                },
                "messages": messages,
                "stream": False
            }
            
            training_status["log"].append(f"📡 Отправка запроса к Ollama API (новый формат)...")
            
            create_response = client.post(
                f"{ollama_url}/api/create",
                json=payload,
                timeout=600.0
            )
            
            training_status["log"].append(f"📨 Получен ответ: {create_response.status_code}")
            
            if create_response.status_code == 200:
                training_status["progress"] = 90
                training_status["log"].append(f"✅ Модель {model_name} успешно создана!")
                
                # Проверяем модель
                training_status["stage"] = "Проверка модели"
                training_status["log"].append("🧪 Тестирование новой модели...")
                
                check_response = client.get(f"{ollama_url}/api/tags")
                if check_response.status_code == 200:
                    models = check_response.json().get("models", [])
                    model_exists = any(m.get("name") == model_name for m in models)
                    
                    if model_exists:
                        training_status["progress"] = 100
                        training_status["stage"] = "Завершено"
                        training_status["log"].append(f"🎉 Обучение завершено! Модель {model_name} готова к использованию!")
                        training_status["log"].append("💡 Выберите новую модель в разделе 'Сокращалка'")
                    else:
                        raise Exception("Модель не найдена в списке")
                else:
                    raise Exception(f"Ошибка проверки модели: {check_response.status_code}")
            else:
                error_msg = create_response.text
                training_status["log"].append(f"❌ Ответ сервера: {error_msg}")
                training_status["log"].append(f"❌ Код ответа: {create_response.status_code}")
                raise Exception(f"Ошибка создания модели: {error_msg}")
            
    except subprocess.TimeoutExpired:
        training_status["error"] = "Превышено время ожидания (10 минут)"
        training_status["log"].append("❌ Ошибка: превышено время ожидания")
    except Exception as e:
        training_status["error"] = str(e)
        training_status["log"].append(f"❌ Ошибка: {e}")
    finally:
        training_status["is_training"] = False
        
        # Очистка временных файлов
        try:
            if os.path.exists("training_examples_web.json"):
                os.remove("training_examples_web.json")
            if os.path.exists("Modelfile.web"):
                os.remove("Modelfile.web")
        except:
            pass

@router.post("/start")
async def start_training(request: StartTrainingRequest, background_tasks: BackgroundTasks):
    """Запустить обучение модели с примерами"""
    
    if training_status["is_training"]:
        return {"error": "Обучение уже запущено"}
    
    if not request.examples or len(request.examples) < 5:
        return {"error": "Необходимо минимум 5 примеров для обучения"}
    
    # Запускаем обучение в отдельном потоке
    thread = threading.Thread(target=run_training_process, args=(request.examples,), daemon=True)
    thread.start()
    
    return {
        "message": "Обучение запущено",
        "status": "started"
    }
