#!/usr/bin/env python3
"""
Автоматизированный скрипт для fine-tuning модели Ollama
Создаёт Modelfile из примеров и обучает модель с подтверждением на каждом этапе
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

class ModelTrainer:
    def __init__(
        self, 
        examples_file="training_examples.json",
        base_model="mistral",
        model_name="summarizer"
    ):
        self.examples_file = examples_file
        self.base_model = base_model
        self.model_name = model_name
        self.version = 1
        self.modelfile_path = "Modelfile.generated"
        self.training_interrupted = False
    
    def load_examples(self):
        """Загрузить примеры из JSON"""
        print(f"📂 Загрузка примеров из {self.examples_file}...")
        
        if not os.path.exists(self.examples_file):
            print(f"❌ Файл {self.examples_file} не найден!")
            return []
        
        try:
            with open(self.examples_file, 'r', encoding='utf-8') as f:
                examples = json.load(f)
            
            print(f"✅ Загружено {len(examples)} примеров")
            return examples
        except Exception as e:
            print(f"❌ Ошибка чтения файла: {e}")
            return []
    
    def load_auto_collected_examples(self, limit=50):
        """Загрузить автоматически собранные примеры"""
        jsonl_file = "backend/training_data.jsonl"
        
        if not os.path.exists(jsonl_file):
            return []
        
        print(f"📂 Загрузка автособранных примеров из {jsonl_file}...")
        examples = []
        
        try:
            with open(jsonl_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if len(examples) >= limit:
                        break
                    
                    data = json.loads(line)
                    meta = data.get("metadata", {})
                    
                    # Берём только качественные примеры
                    if meta.get("deviation", 100) <= 3:
                        examples.append({
                            "original": data["prompt"].split(":\\n\\n", 1)[1] if ":\\n\\n" in data["prompt"] else "",
                            "summary": data["response"],
                            "ratio": meta.get("ratio_target", 50)
                        })
            
            print(f"✅ Загружено {len(examples)} автособранных примеров")
            return examples
        except Exception as e:
            print(f"⚠️ Не удалось загрузить автособранные примеры: {e}")
            return []
    
    def generate_modelfile(self, examples):
        """Сгенерировать Modelfile из примеров"""
        print("\n🔨 Генерация Modelfile...")
        
        modelfile_content = f"""FROM {self.base_model}

# Параметры оптимизации для русского текста
PARAMETER temperature 0.3
PARAMETER top_p 0.9
PARAMETER top_k 40
PARAMETER repeat_penalty 1.15
PARAMETER num_predict 4096

# Системный промпт
SYSTEM \"\"\"Ты - профессиональный редактор текстов. Твоя задача - сокращать русские тексты, точно следуя заданному проценту сокращения.

ПРАВИЛА:
- Сохраняй все команды, цифры и технические термины
- Пиши ТОЛЬКО сокращённый текст без пояснений
- Отвечай на том же языке, что и оригинал
- Точно следуй заданному проценту сокращения
\"\"\"

"""
        
        # Добавляем примеры
        for i, ex in enumerate(examples, 1):
            ratio = ex.get('ratio', 50)
            original = ex.get('original', '').strip()
            summary = ex.get('summary', '').strip()
            
            if not original or not summary:
                continue
            
            modelfile_content += f"""# Пример {i} (сокращение до {ratio}%)
MESSAGE user \"\"\"Сократи текст до {ratio}%:

{original}\"\"\"
MESSAGE assistant \"\"\"{summary}\"\"\"

"""
        
        # Сохраняем Modelfile
        with open(self.modelfile_path, 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
        
        print(f"✅ Modelfile сохранён: {self.modelfile_path}")
        print(f"📊 Добавлено {len([ex for ex in examples if ex.get('original')])} примеров")
        
        return self.modelfile_path
    
    def find_next_version(self):
        """Найти следующую доступную версию модели"""
        result = subprocess.run(
            ["docker", "exec", "studeti-ollama-1", "ollama", "list"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return 1
        
        version = 1
        while f"{self.model_name}:v{version}" in result.stdout:
            version += 1
        
        return version
    
    def create_model(self):
        """Создать модель в Ollama"""
        self.version = self.find_next_version()
        model_tag = f"{self.model_name}:v{self.version}"
        
        print(f"\n🚀 Создание модели {model_tag}...")
        print("⏳ Это может занять несколько минут...")
        
        # Копируем Modelfile в контейнер
        subprocess.run([
            "docker", "cp", 
            self.modelfile_path,
            f"studeti-ollama-1:/tmp/Modelfile"
        ])
        
        # Создаём модель
        result = subprocess.run([
            "docker", "exec", "studeti-ollama-1",
            "ollama", "create", model_tag, "-f", "/tmp/Modelfile"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Модель {model_tag} успешно создана!")
            return model_tag
        else:
            print(f"❌ Ошибка создания модели:")
            print(result.stderr)
            return None
    
    def test_model(self, model_tag):
        """Протестировать созданную модель"""
        print(f"\n🧪 Тест модели {model_tag}...")
        
        test_text = "Этот текст нужно сократить для проверки работы модели. Мы проверяем, что модель правильно обучена и может сокращать русские тексты."
        
        result = subprocess.run([
            "docker", "exec", "studeti-ollama-1",
            "ollama", "run", model_tag,
            f"Сократи текст до 50%:\n\n{test_text}"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"\n📝 Результат теста:")
            print("=" * 60)
            print(result.stdout)
            print("=" * 60)
            return True
        else:
            print("❌ Ошибка теста модели")
            return False
    
    def show_summary(self, model_tag, examples_count):
        """Показать итоговую информацию"""
        print("\n" + "=" * 60)
        print("🎉 ОБУЧЕНИЕ ЗАВЕРШЕНО!")
        print("=" * 60)
        print(f"✅ Модель: {model_tag}")
        print(f"📊 Примеров использовано: {examples_count}")
        print(f"🧠 Базовая модель: {self.base_model}")
        print(f"📁 Modelfile: {self.modelfile_path}")
        print("\n🚀 Как использовать:")
        print(f"   1. В веб-интерфейсе выберите модель: {model_tag}")
        print(f"   2. Или в командной строке: ollama run {model_tag}")
        print(f"   3. Или через API: model='{model_tag}'")
        print("\n💡 Для продолжения обучения:")
        print("   - Добавьте примеры в training_examples.json")
        print("   - Запустите: python auto_train.py")
        print("   - Будет создана следующая версия (v{})".format(self.version + 1))
        print("=" * 60)
    
    def confirm_action(self, message, auto_mode=False):
        """Запросить подтверждение пользователя"""
        if auto_mode:
            print(f"\n{message} → ✅ Да (авторежим)")
            return True
        
        while True:
            response = input(f"\n{message} (y/n): ").lower().strip()
            if response in ['y', 'yes', 'д', 'да']:
                return True
            elif response in ['n', 'no', 'н', 'нет']:
                return False
            print("Пожалуйста, введите 'y' или 'n'")
    
    def can_stop(self, stage, auto_mode=False):
        """Проверить, хочет ли пользователь остановить обучение"""
        if auto_mode:
            print(f"\n⏸️  Этап: {stage} → ✅ Продолжаем (авторежим)")
            return False
        
        print(f"\n⏸️  Этап: {stage}")
        if self.confirm_action("❓ Продолжить обучение?"):
            return False
        else:
            print("\n⏹️  Обучение остановлено пользователем")
            self.training_interrupted = True
            return True
    
    def train(self, auto_mode=False):
        """Основной процесс обучения"""
        mode_label = "АВТОМАТИЧЕСКОЕ" if auto_mode else "ИНТЕРАКТИВНОЕ"
        print("=" * 60)
        print(f"🎓 {mode_label} ОБУЧЕНИЕ МОДЕЛИ")
        print("=" * 60)
        
        if auto_mode:
            print("🤖 Режим: автоматический (без подтверждений)")
        else:
            print("👤 Режим: интерактивный (с подтверждениями)")
        
        # Этап 1: Загрузка примеров
        print("\n📚 ЭТАП 1: Загрузка обучающих примеров")
        
        manual_examples = self.load_examples()
        auto_examples = self.load_auto_collected_examples()
        
        all_examples = manual_examples + auto_examples
        
        if not all_examples:
            print("\n❌ Нет примеров для обучения!")
            print("💡 Добавьте примеры в training_examples.json")
            return
        
        print(f"\n📊 Всего примеров: {len(all_examples)}")
        print(f"   - Ручных: {len(manual_examples)}")
        print(f"   - Автособранных: {len(auto_examples)}")
        
        if self.can_stop("Загрузка примеров завершена", auto_mode):
            return
        
        # Этап 2: Генерация Modelfile
        print("\n🔨 ЭТАП 2: Генерация Modelfile")
        
        modelfile = self.generate_modelfile(all_examples)
        
        if not auto_mode:
            print(f"\n📄 Просмотр Modelfile:")
            if self.confirm_action("Хотите посмотреть содержимое Modelfile?"):
                with open(modelfile, 'r', encoding='utf-8') as f:
                    print("\n" + "-" * 60)
                    print(f.read()[:1000] + "..." if os.path.getsize(modelfile) > 1000 else f.read())
                    print("-" * 60)
        
        if self.can_stop("Modelfile сгенерирован", auto_mode):
            return
        
        # Этап 3: Создание модели
        print("\n🚀 ЭТАП 3: Создание модели в Ollama")
        print("⚠️  Это может занять 5-10 минут в зависимости от количества примеров")
        
        if not self.confirm_action("Начать создание модели?", auto_mode):
            print("\n⏹️  Обучение отменено")
            return
        
        model_tag = self.create_model()
        
        if not model_tag:
            print("\n❌ Не удалось создать модель")
            return
        
        if self.can_stop("Модель создана", auto_mode):
            return
        
        # Этап 4: Тестирование
        print("\n🧪 ЭТАП 4: Тестирование модели")
        
        if self.confirm_action("Протестировать модель?", auto_mode):
            self.test_model(model_tag)
        
        # Финал
        self.show_summary(model_tag, len(all_examples))
        
        # Очистка
        if self.confirm_action("\n🗑️  Удалить временный Modelfile?", auto_mode):
            if os.path.exists(self.modelfile_path):
                os.remove(self.modelfile_path)
                print("✅ Временные файлы удалены")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Автоматическое обучение модели для сокращения текста')
    parser.add_argument('--examples', default='training_examples.json',
                        help='Путь к файлу с примерами (по умолчанию: training_examples.json)')
    parser.add_argument('--base-model', default='mistral',
                        help='Базовая модель Ollama (по умолчанию: mistral)')
    parser.add_argument('--model-name', default='summarizer',
                        help='Имя новой модели (по умолчанию: summarizer)')
    parser.add_argument('--auto-only', action='store_true',
                        help='Использовать только автособранные примеры')
    parser.add_argument('--auto', action='store_true',
                        help='Автоматический режим без подтверждений (для фонового обучения)')
    
    args = parser.parse_args()
    
    trainer = ModelTrainer(
        examples_file=args.examples,
        base_model=args.base_model,
        model_name=args.model_name
    )
    
    try:
        trainer.train(auto_mode=args.auto)
    except KeyboardInterrupt:
        print("\n\n⏹️  Обучение прервано пользователем (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
