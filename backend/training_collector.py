"""
Автоматический сборщик обучающих данных для fine-tuning
Сохраняет удачные примеры сокращения текста и автоматически запускает обучение
"""

import json
import os
import subprocess
import threading
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class TrainingDataCollector:
    def __init__(self, file_path: str = "training_data.jsonl"):
        self.file_path = file_path
        self.enabled = os.getenv("COLLECT_TRAINING_DATA", "false").lower() == "true"
        self.auto_train_enabled = os.getenv("AUTO_TRAIN", "false").lower() == "true"
        self.auto_train_threshold = int(os.getenv("AUTO_TRAIN_THRESHOLD", "20"))
        self.is_training = False
        self.last_train_count = 0
    
    def add_example(
        self, 
        original_text: str, 
        summary: str, 
        ratio: int,
        model: str,
        custom_prompt: Optional[str] = None
    ):
        """
        Сохранить пример удачного сокращения для последующего обучения
        
        Критерии "удачного" сокращения:
        - Отклонение от целевого процента < 5%
        - Нет артефактов в тексте
        - Сохранён язык оригинала
        """
        if not self.enabled:
            return
        
        actual_ratio = round(len(summary) / len(original_text) * 100, 1)
        deviation = abs(actual_ratio - ratio)
        
        # Проверяем качество
        if deviation > 5:
            return  # Слишком большое отклонение
        
        # Проверяем на артефакты
        bad_phrases = ['Резюме:', 'Summary:', '[РЕЗЮМЕ]', 'Важно:', 'Отвечай']
        if any(phrase in summary for phrase in bad_phrases):
            return  # Есть артефакты
        
        # Формируем пример в формате для обучения
        prompt_text = f"Сократи текст до {ratio}%"
        if custom_prompt:
            prompt_text += f". {custom_prompt}"
        prompt_text += f":\n\n{original_text}"
        
        example = {
            "prompt": prompt_text,
            "response": summary,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "ratio_target": ratio,
                "ratio_actual": actual_ratio,
                "deviation": round(deviation, 1),
                "original_length": len(original_text),
                "summary_length": len(summary),
                "model_used": model,
                "custom_prompt": custom_prompt
            }
        }
        
        # Сохраняем в файл
        try:
            with open(self.file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(example, ensure_ascii=False) + "\n")
            
            count = self._count_examples()
            logger.info(f"✅ Сохранён обучающий пример #{count} (отклонение {deviation:.1f}%)")
            
            # Сохраняем состояние для API
            self._save_state()
            
            # Автоматическое обучение при достижении порога
            if self.auto_train_enabled:
                self._check_auto_train(count)
            elif count in [10, 50, 100, 200]:
                logger.info(f"🎓 Собрано {count} примеров! Можно начать fine-tuning модели.")
        
        except Exception as e:
            logger.error(f"⚠️ Ошибка сохранения примера: {e}")
    
    def _check_auto_train(self, count: int):
        """Проверить, нужно ли запустить автоматическое обучение"""
        if self.is_training:
            logger.info("🔄 Обучение уже запущено, пропускаем")
            return
        
        # Запускаем обучение каждые N примеров
        if count >= self.last_train_count + self.auto_train_threshold:
            logger.info(f"🎓 Достигнут порог {self.auto_train_threshold} новых примеров. Запуск автообучения...")
            self.last_train_count = count
            
            # Запускаем обучение в отдельном потоке, чтобы не блокировать API
            thread = threading.Thread(target=self._run_auto_train, daemon=True)
            thread.start()
    
    def _run_auto_train(self):
        """Запустить процесс автоматического обучения"""
        if self.is_training:
            return
        
        self.is_training = True
        logger.info("🚀 Начало автоматического обучения модели...")
        
        try:
            # Запускаем скрипт обучения с флагом --auto
            result = subprocess.run(
                ["python", "auto_train.py", "--auto", "--model-name", "summarizer"],
                cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                capture_output=True,
                text=True,
                timeout=1800  # 30 минут максимум
            )
            
            if result.returncode == 0:
                logger.info("✅ Автоматическое обучение завершено успешно!")
                logger.info(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            else:
                logger.error(f"❌ Ошибка автоматического обучения: {result.stderr}")
        
        except subprocess.TimeoutExpired:
            logger.error("⏰ Превышено время ожидания обучения (30 минут)")
        except Exception as e:
            logger.error(f"❌ Ошибка запуска автообучения: {e}")
        finally:
            self.is_training = False
            self._save_state()
    
    def _save_state(self):
        """Сохранить состояние для API"""
        try:
            state = {
                "last_train_count": self.last_train_count,
                "is_training": self.is_training,
                "total_examples": self._count_examples()
            }
            
            with open("training_state.json", "w", encoding="utf-8") as f:
                json.dump(state, f)
        except:
            pass
    
    def _count_examples(self) -> int:
        """Подсчитать количество сохранённых примеров"""
        if not os.path.exists(self.file_path):
            return 0
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def get_stats(self) -> dict:
        """Получить статистику собранных данных"""
        if not os.path.exists(self.file_path):
            return {"total": 0}
        
        total = 0
        avg_deviation = 0
        ratios = {}
        
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    example = json.loads(line)
                    total += 1
                    
                    meta = example.get("metadata", {})
                    avg_deviation += meta.get("deviation", 0)
                    
                    ratio = meta.get("ratio_target", 50)
                    ratios[ratio] = ratios.get(ratio, 0) + 1
            
            return {
                "total": total,
                "average_deviation": round(avg_deviation / total, 2) if total > 0 else 0,
                "ratios_distribution": ratios,
                "ready_for_training": total >= 50
            }
        except:
            return {"total": 0, "error": "Failed to read stats"}

# Глобальный экземпляр
collector = TrainingDataCollector()
