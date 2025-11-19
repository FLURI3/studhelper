import re
from collections import Counter
from typing import List, Dict

class AnalyzerService:
    def get_statistics(self, text: str) -> Dict:
        """Получить статистику по тексту"""
        # Подсчёт слов
        words = re.findall(r'\b\w+\b', text.lower())
        word_count = len(words)
        
        # Подсчёт предложений
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Подсчёт символов
        char_count = len(text)
        
        # Время чтения (среднее 200 слов в минуту)
        read_time = max(1, round(word_count / 200))
        
        # Сложность (простая оценка на основе средней длины предложения)
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        if avg_sentence_length < 15:
            complexity = "Простая"
        elif avg_sentence_length < 25:
            complexity = "Средняя"
        else:
            complexity = "Сложная"
        
        return {
            "word_count": word_count,
            "sentence_count": sentence_count,
            "char_count": char_count,
            "read_time": read_time,
            "complexity": complexity
        }
    
    def extract_key_terms(self, text: str, top_n: int = 10) -> List[str]:
        """Извлечь ключевые термины"""
        # Простое извлечение - самые частотные слова (без стоп-слов)
        stop_words = {
            'и', 'в', 'не', 'на', 'с', 'что', 'как', 'по', 'из', 'к',
            'а', 'то', 'это', 'для', 'за', 'от', 'о', 'у', 'до', 'при',
            'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would'
        }
        
        words = re.findall(r'\b\w+\b', text.lower())
        # Фильтруем короткие слова и стоп-слова
        filtered_words = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Подсчитываем частоту
        word_freq = Counter(filtered_words)
        
        # Возвращаем топ-N
        return [word for word, _ in word_freq.most_common(top_n)]
