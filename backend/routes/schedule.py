from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
import httpx
from bs4 import BeautifulSoup
import re
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_URL = "http://techn.sstu.ru/schedule/spo_2025"

class Lesson(BaseModel):
    number: str
    time: str
    subject: str
    teacher: Optional[str] = None
    room: Optional[str] = None
    type: Optional[str] = None

class DaySchedule(BaseModel):
    day: str
    date: str
    day_of_week: int  # 0=Пн, 1=Вт, ..., 5=Сб
    lessons: List[Lesson]

class GroupSchedule(BaseModel):
    group_code: str
    group_name: str
    schedule_days: List[DaySchedule]  # Массив дней с датами
    last_updated: Optional[str] = None

class GroupInfo(BaseModel):
    code: str
    name: str
    url: str

class GroupsResponse(BaseModel):
    groups: List[GroupInfo]

@router.get("/schedule/groups", response_model=GroupsResponse)
def get_groups():
    """Получить список всех групп"""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(f"{BASE_URL}/cg_spo.htm")
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            groups = []
            
            # Ищем все ссылки на расписания групп
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.startswith('cg') and href.endswith('.htm'):
                    # Извлекаем код группы из URL (например, cg74.htm -> 74)
                    match = re.search(r'cg(\d+)\.htm', href)
                    if match:
                        code = match.group(1)
                        name = link.get_text(strip=True)
                        
                        if name:  # Пропускаем пустые ссылки
                            groups.append(GroupInfo(
                                code=code,
                                name=name,
                                url=f"{BASE_URL}/{href}"
                            ))
            
            logger.info(f"Found {len(groups)} groups")
            return GroupsResponse(groups=groups)
            
    except Exception as e:
        logger.error(f"Error fetching groups: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch groups: {str(e)}")

@router.get("/schedule/{group_code}", response_model=GroupSchedule)
def get_schedule(group_code: str):
    """Получить расписание конкретной группы"""
    try:
        url = f"{BASE_URL}/cg{group_code}.htm"
        
        with httpx.Client(timeout=10.0) as client:
            response = client.get(url)
            response.raise_for_status()
            
            # Сайт использует UTF-8
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Извлекаем название группы из title
            title = soup.find('title')
            group_name = title.get_text(strip=True).replace('Текущее расписание: Группа: ', '') if title else f"Группа {group_code}"
            
            # Парсим расписание
            schedule_days = []  # Список всех дней
            current_day_schedule = None
            
            # Ищем таблицу с классом inf
            table = soup.find('table', class_='inf')
            if not table:
                raise HTTPException(status_code=404, detail="Schedule table not found")
            
            rows = table.find_all('tr')
            
            from datetime import datetime
            
            for row in rows:
                cells = row.find_all(['td', 'th'])
                
                if not cells:
                    continue
                
                # Определяем начало нового дня или продолжение текущего
                first_cell = cells[0]
                first_cell_text = first_cell.get_text(strip=True)
                has_rowspan = first_cell.get('rowspan')
                
                # Проверяем, начинается ли новый день
                if has_rowspan:
                    # Сохраняем предыдущий день если есть
                    if current_day_schedule and current_day_schedule.lessons:
                        schedule_days.append(current_day_schedule)
                    
                    # Извлекаем дату (формат: "17.11.2025\nПн-2")
                    date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', first_cell_text)
                    if date_match:
                        date_str = date_match.group(1)
                        date_obj = datetime.strptime(date_str, '%d.%m.%Y')
                        day_of_week = date_obj.weekday()  # 0=Пн, 1=Вт, ..., 6=Вс
                        
                        # Создаем новый день
                        current_day_schedule = DaySchedule(
                            day=['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье'][day_of_week],
                            date=date_str,
                            day_of_week=day_of_week,
                            lessons=[]
                        )
                
                # Парсим пару
                if current_day_schedule:
                    time_cell_index = 1 if has_rowspan else 0
                    subject_cell_start = 2 if has_rowspan else 1
                    
                    if len(cells) <= time_cell_index:
                        continue
                    
                    time_cell = cells[time_cell_index]
                    time_text = time_cell.get_text(strip=True)
                    
                    # Извлекаем номер пары и время
                    lesson_num = time_text.split()[0] if time_text else ""
                    # Поддержка разных форматов времени: "08:00-10:00" или "8.30-10.00"
                    time_match = re.search(r'(\d{1,2}[\.:]\d{2}[-–]\d{1,2}[\.:]\d{2})', time_text)
                    time_str = time_match.group(1) if time_match else ""
                    
                    if not time_str:
                        continue
                    
                    # Обрабатываем ячейки с предметами
                    if len(cells) > subject_cell_start:
                        for subject_cell in cells[subject_cell_start:]:
                            cell_classes = subject_cell.get('class', [])
                            if 'nul' in cell_classes:
                                continue
                            
                            subject_link = subject_cell.find('a', class_='z1')
                            room_link = subject_cell.find('a', class_='z2')
                            teacher_link = subject_cell.find('a', class_='z3')
                            
                            subject = subject_link.get_text(strip=True) if subject_link else ""
                            room = room_link.get_text(strip=True) if room_link else None
                            teacher = teacher_link.get_text(strip=True) if teacher_link else None
                            
                            if subject:
                                lesson = Lesson(
                                    number=lesson_num,
                                    time=time_str,
                                    subject=subject,
                                    teacher=teacher,
                                    room=room,
                                    type=None
                                )
                                current_day_schedule.lessons.append(lesson)
            
            # Добавляем последний день
            if current_day_schedule and current_day_schedule.lessons:
                schedule_days.append(current_day_schedule)
            
            return GroupSchedule(
                group_code=group_code,
                group_name=group_name,
                schedule_days=schedule_days,
                last_updated=None
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching schedule for group {group_code}: {e}")
        raise HTTPException(status_code=404, detail=f"Schedule not found for group {group_code}")
    except Exception as e:
        logger.error(f"Error fetching schedule for group {group_code}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch schedule: {str(e)}")
