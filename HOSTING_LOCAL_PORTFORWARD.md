# 🌐 Локальный хостинг с проброшенными портами

## Что нужно:
- Статический IP от провайдера или динамический DNS
- Настройка роутера (Port Forwarding)
- Домен (опционально)

## Шаги:

### 1️⃣ Узнайте свой внешний IP:
```powershell
Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing | Select-Object -ExpandProperty Content
```

### 2️⃣ Настройте Port Forwarding на роутере:

Зайдите в панель роутера (обычно 192.168.1.1 или 192.168.0.1)

Пробросьте порты:
- **80** → IP вашего ПК:80 (HTTP)
- **443** → IP вашего ПК:443 (HTTPS)
- **8000** → IP вашего ПК:8000 (Backend)
- **5173** → IP вашего ПК:5173 (Frontend)

### 3️⃣ Настройте Windows Firewall:
```powershell
# Разрешите входящие подключения
New-NetFirewallRule -DisplayName "Student Helper HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "Student Helper HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow
New-NetFirewallRule -DisplayName "Student Helper Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
New-NetFirewallRule -DisplayName "Student Helper Frontend" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow
```

### 4️⃣ Настройте домен (опционально):

Если у вас есть домен, создайте A-запись:
```
Type: A
Name: @
Value: ВАШ_ВНЕШНИЙ_IP
```

### 5️⃣ Установите Nginx на Windows:

Скачайте: http://nginx.org/en/download.html

Замените `nginx.conf`:
```nginx
http {
    server {
        listen 80;
        server_name localhost;
        
        location / {
            proxy_pass http://localhost:5173;
        }
        
        location /api/ {
            proxy_pass http://localhost:8000/api/;
        }
    }
}
```

Запустите:
```powershell
cd C:\nginx
start nginx
```

### 6️⃣ Для HTTPS:

Используйте Certbot для Windows или Let's Encrypt:
- Win-Acme: https://www.win-acme.com/

## Плюсы:
✅ Полный контроль
✅ Свой домен
✅ Без ограничений
✅ Бесплатно

## Минусы:
❌ Сложная настройка
❌ Нужен статический IP
❌ Компьютер всегда включен
❌ Безопасность на вас
