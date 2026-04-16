# 🌐 Локальный хостинг с Ngrok

## Что это?
Ngrok создает безопасный туннель от вашего локального сервера к публичному URL.
Вы получите адрес типа: `https://random-name.ngrok.io`

## Установка Ngrok:

1. Скачайте: https://ngrok.com/download
2. Распакуйте в `C:\ngrok`
3. Зарегистрируйтесь на ngrok.com и получите токен
4. Настройте токен:
   ```powershell
   C:\ngrok\ngrok.exe authtoken YOUR_TOKEN
   ```

## Запуск:

### 1. Запустите проект локально:
```powershell
cd C:\Users\RobotComp.ru\Desktop\studeti
docker-compose up -d
```

### 2. Запустите Ngrok для backend (в новом терминале):
```powershell
C:\ngrok\ngrok.exe http 8000
```

### 3. Запустите Ngrok для frontend (еще один терминал):
```powershell
C:\ngrok\ngrok.exe http 5173
```

### 4. Ngrok покажет URLs:
```
Forwarding   https://abc123.ngrok.io -> http://localhost:8000
Forwarding   https://xyz456.ngrok.io -> http://localhost:5173
```

### 5. Обновите frontend для использования backend URL:

Измените в `frontend/src/App.jsx` или создайте `.env`:
```env
VITE_API_URL=https://abc123.ngrok.io
```

Перезапустите frontend:
```powershell
docker-compose restart frontend
```

### 6. Обновите Android приложение:
```java
private static final String BASE_URL = "https://xyz456.ngrok.io";
```

## Плюсы:
✅ Очень быстро (2 минуты)
✅ HTTPS из коробки
✅ Работает из любой точки мира
✅ Бесплатно для базового использования

## Минусы:
❌ Рандомный URL каждый раз (платная версия дает фиксированный)
❌ Компьютер должен быть включен
❌ Ограничение 40 запросов/минуту (бесплатная версия)

---

## Платный план Ngrok ($8/месяц):
- Фиксированный домен (your-name.ngrok.app)
- Свой домен (your-domain.com)
- Больше запросов
