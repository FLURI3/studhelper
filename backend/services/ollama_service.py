import httpx
import os
import logging
from typing import List

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        logger.info(f"OllamaService initialized with URL: {self.base_url}")
    
    async def check_health(self) -> bool:
        """Проверить доступность Ollama"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    async def list_models(self) -> list:
        """Получить список доступных моделей"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return [m["name"] for m in models]
                return []
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    async def _generate(self, prompt: str, model: str = "mistral", max_tokens: int = 4000) -> str:
        """Общий метод для генерации текста через Ollama"""
        logger.info(f"Generating text with model: {model}")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                logger.info(f"Sending request to {self.base_url}/api/generate")
                
                # Параметры для контроля генерации
                request_data = {
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_predict": max_tokens,  # Максимум токенов
                        "temperature": 0.3,  # Меньше креативности = точнее следует инструкциям
                        "top_p": 0.9,
                        "top_k": 40,
                        "repeat_penalty": 1.1,  # Избегаем повторений
                        "num_gpu": 99,  # Используем всю доступную GPU
                        "num_thread": 8  # Многопоточность CPU
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=request_data
                )
                response.raise_for_status()
                result = response.json()["response"]
                
                logger.info(f"Generated text length: {len(result)} characters")
                logger.debug(f"Generated text preview: {result[:100]}...")
                
                return result
        except httpx.ConnectError as e:
            logger.error(f"Connection error to Ollama: {e}")
            raise Exception(f"Не удалось подключиться к Ollama. Убедитесь, что Ollama запущен и модель {model} загружена.")
        except httpx.TimeoutException as e:
            logger.error(f"Timeout error: {e}")
            raise Exception(f"Превышено время ожидания ответа от Ollama. Возможно модель {model} не загружена. Выполните: docker exec studeti-ollama-1 ollama pull {model}")
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    async def summarize(self, text: str, ratio: int, model: str, custom_prompt: str = "") -> dict:
        """Сократить текст с итеративной корректировкой"""
        logger.info(f"Summarizing text: {len(text)} chars -> {ratio}%")
        
        # Вычисляем целевую длину
        target_length = int(len(text) * ratio / 100)
        
        # Определяем язык текста (проверяем на кириллицу)
        has_cyrillic = any(ord(c) >= 0x0400 and ord(c) <= 0x04FF for c in text)
        language_instruction = "ОБЯЗАТЕЛЬНО пиши НА РУССКОМ ЯЗЫКЕ" if has_cyrillic else "Keep the same language as original"
        
        custom_instruction = f"\n- {custom_prompt}" if custom_prompt else ""
        
        # Попытка 1: Первичное сокращение
        attempts = []
        max_attempts = 3
        
        for attempt in range(max_attempts):
            if attempt == 0:
                # Первая попытка
                max_tokens = int(target_length * 1.3 / 4)
                prompt = f"""Сократи текст РОВНО до {target_length} символов (сейчас {len(text)}).

ПРАВИЛА:
- {language_instruction}
- СТРОГО {target_length} символов (допустимо ±5%)
- Сохрани команды, цифры, термины{custom_instruction}
- Отвечай ТОЛЬКО текстом, БЕЗ пояснений

{text}"""
            else:
                # Корректирующие попытки
                prev_summary = attempts[-1]
                prev_length = len(prev_summary)
                
                if prev_length > target_length * 1.1:
                    # Слишком длинный - сократить сильнее
                    max_tokens = int(target_length * 0.9 / 4)
                    action = f"СОКРАТИ ЕЩЁ сильнее до {target_length} символов (сейчас {prev_length})"
                elif prev_length < target_length * 0.9:
                    # Слишком короткий - добавить деталей
                    max_tokens = int(target_length * 1.2 / 4)
                    action = f"ДОБАВЬ больше деталей, целевая длина {target_length} символов (сейчас {prev_length})"
                else:
                    # В пределах нормы - выходим
                    logger.info(f"Achieved target on attempt {attempt + 1}")
                    break
                
                prompt = f"""{action}. {language_instruction}.

ИСХОДНЫЙ ТЕКСТ:
{text}

ПРЕДЫДУЩАЯ ПОПЫТКА ({prev_length} символов):
{prev_summary}

ИСПРАВЛЕННАЯ ВЕРСИЯ (~{target_length} символов):"""
            
            logger.info(f"Attempt {attempt + 1}/{max_attempts}, target: {target_length}, max_tokens: {max_tokens}")
            summary = await self._generate(prompt, model, max_tokens=max_tokens)
            summary = self._cleanup_summary(summary)
            
            attempts.append(summary)
            
            # Проверяем, попали ли в цель (±10%)
            current_ratio = len(summary) / len(text) * 100
            if abs(current_ratio - ratio) <= 10:
                logger.info(f"Target achieved: {current_ratio:.1f}% (goal: {ratio}%)")
                break
        
        # Берём лучший результат (ближайший к цели)
        best_summary = min(attempts, key=lambda s: abs(len(s) - target_length))
        summary = best_summary
        
        logger.info(f"Summarization complete after {len(attempts)} attempts. Original: {len(text)}, Final: {len(summary)}")
        
        reasoning = f"Попыток: {len(attempts)}, Цель: {target_length} символов ({ratio}%), Результат: {len(summary)} символов"
        
        return {
            "reasoning": reasoning,
            "summary": summary
        }
    
    def _cleanup_summary(self, summary: str) -> str:
        """Очистка текста от артефактов"""
        summary = summary.strip()
        
        # Агрессивная очистка от артефактов
        cleanup_phrases = [
            "Сокращённый текст:",
            "Сокращенный текст:",
            "Краткое резюме:",
            "Резюме:",
            "Summary:",
            "[РЕЗЮМЕ]",
            "[ПЛАН]",
            "План сокращения:",
            "Важно:",
            "Текст для сокращения:",
            "ИСПРАВЛЕННАЯ ВЕРСИЯ",
            "СОКРАЩЁННАЯ ВЕРСИЯ",
        ]
        
        for phrase in cleanup_phrases:
            if phrase in summary:
                parts = summary.split(phrase)
                summary = max(parts, key=len).strip()
        
        # Убираем строки с инструкциями
        lines = summary.split('\n')
        clean_lines = []
        skip_keywords = ['отвечай', 'не добавляй', 'не повторяй', 'просто выдай', 'важно:', 'instruction', 'note:', 'правила:']
        
        for line in lines:
            line_lower = line.lower()
            if not any(keyword in line_lower for keyword in skip_keywords):
                clean_lines.append(line)
        
        return '\n'.join(clean_lines).strip()
    
    async def generate_questions(self, text: str, count: int, model: str) -> List[str]:
        """Сгенерировать вопросы из текста"""
        logger.info(f"Generating {count} questions from text")
        
        prompt = f"""На основе следующего текста создай {count} тестовых вопросов с вариантами ответов.
Каждый вопрос должен быть в формате:
Вопрос: [текст вопроса]
а) [вариант 1]
б) [вариант 2]
в) [вариант 3]
г) [вариант 4]
Правильный ответ: [буква]

Текст:
{text}

Вопросы:"""
        
        response = await self._generate(prompt, model)
        # Простое разделение по вопросам (можно улучшить парсинг)
        questions = response.split("\n\n")
        
        logger.info(f"Generated {len(questions)} questions")
        return [q.strip() for q in questions if q.strip()]
