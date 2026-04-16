# 🌐 Production Deployment Guide

## Развертывание Student Helper на сервере

### Требования

- **VPS/Сервер** с Ubuntu 20.04+ (минимум 4GB RAM, 2 CPU)
- **Docker** и **Docker Compose** установлены
- **Домен** с A-записью, указывающей на IP сервера
- **Открытые порты**: 80 (HTTP), 443 (HTTPS)

---

## 🚀 Быстрый старт

### 1. Подключитесь к серверу

```bash
ssh root@your-server-ip
```

### 2. Установите Docker (если не установлен)

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### 3. Клонируйте репозиторий

```bash
git clone https://github.com/FLURI3/studeti.git
cd studeti
```

### 4. Настройте переменные окружения

```bash
cp .env.production.example .env
nano .env
```

Заполните:
```env
DB_PASSWORD=your-strong-password
JWT_SECRET=$(openssl rand -hex 32)
DOMAIN=your-domain.com
VITE_API_URL=https://your-domain.com/api
```

### 5. Настройте SSL сертификаты

#### Вариант A: Let's Encrypt (рекомендуется)

```bash
# Установите Certbot
apt-get update
apt-get install certbot

# Получите сертификат
certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Скопируйте сертификаты
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/

# Настройте автообновление
echo "0 0 * * * certbot renew --quiet && docker-compose -f /path/to/studeti/docker-compose.prod.yml restart nginx" | crontab -
```

#### Вариант B: Самоподписанный сертификат (только для тестов)

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/CN=your-domain.com"
```

### 6. Запустите деплой

```bash
chmod +x deploy.sh
./deploy.sh
```

Или вручную:

```bash
# Сборка и запуск
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Загрузка модели Ollama
docker-compose -f docker-compose.prod.yml exec ollama ollama pull mistral
```

### 7. Проверьте работу

```bash
# Статус контейнеров
docker-compose -f docker-compose.prod.yml ps

# Логи
docker-compose -f docker-compose.prod.yml logs -f

# Тест API
curl https://your-domain.com/health
```

---

## 📱 Обновление Android приложения

После деплоя обновите URL в Android приложении:

**`android/app/src/main/java/com/studenthelper/app/MainActivity.java`:**

```java
private static final String BASE_URL = "https://your-domain.com";
```

Пересоберите APK:

```bash
cd android
./gradlew assembleRelease
```

APK: `app/build/outputs/apk/release/app-release.apk`

---

## 🔧 Управление

### Остановка

```bash
docker-compose -f docker-compose.prod.yml down
```

### Перезапуск

```bash
docker-compose -f docker-compose.prod.yml restart
```

### Обновление

```bash
git pull
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### Логи

```bash
# Все сервисы
docker-compose -f docker-compose.prod.yml logs -f

# Конкретный сервис
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Бэкап базы данных

```bash
docker-compose -f docker-compose.prod.yml exec postgres pg_dump -U user studentdb > backup.sql
```

### Восстановление базы

```bash
docker-compose -f docker-compose.prod.yml exec -T postgres psql -U user studentdb < backup.sql
```

---

## 🔒 Безопасность

### 1. Firewall

```bash
# UFW
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 2. Обновление системы

```bash
apt-get update && apt-get upgrade -y
```

### 3. Ротация паролей

Регулярно обновляйте:
- `DB_PASSWORD` в `.env`
- `JWT_SECRET` в `.env`

### 4. Мониторинг

Установите мониторинг (опционально):

```bash
# Prometheus + Grafana
docker-compose -f docker-compose.monitoring.yml up -d
```

---

## 📊 Оптимизация

### Увеличение лимитов для больших файлов

**`nginx/nginx.conf`:**
```nginx
client_max_body_size 500M;
```

### Масштабирование Backend

**`docker-compose.prod.yml`:**
```yaml
backend:
  deploy:
    replicas: 3
  command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Кеширование Redis

Backend уже использует Redis для кеширования LLM запросов.

---

## 🌍 Несколько доменов

Добавьте в `nginx/nginx.conf`:

```nginx
server {
    listen 443 ssl http2;
    server_name domain2.com;
    
    # Те же настройки SSL и proxy
    ...
}
```

---

## ☁️ Облачные провайдеры

### DigitalOcean

1. Создайте Droplet (Ubuntu 22.04, 4GB RAM)
2. Добавьте домен в DNS
3. Следуйте инструкциям выше

### AWS EC2

1. Запустите t3.medium инстанс
2. Откройте Security Group: 22, 80, 443
3. Следуйте инструкциям выше

### Hetzner

1. Создайте Cloud Server (CX21)
2. Настройте Firewall
3. Следуйте инструкциям выше

---

## 🆘 Решение проблем

### Nginx не запускается

```bash
# Проверьте конфигурацию
docker-compose -f docker-compose.prod.yml exec nginx nginx -t

# Проверьте SSL сертификаты
ls -la nginx/ssl/
```

### Backend ошибки 502

```bash
# Проверьте логи backend
docker-compose -f docker-compose.prod.yml logs backend

# Перезапустите
docker-compose -f docker-compose.prod.yml restart backend
```

### Ollama не отвечает

```bash
# Проверьте GPU (если есть)
docker-compose -f docker-compose.prod.yml logs ollama

# Загрузите модель вручную
docker-compose -f docker-compose.prod.yml exec ollama ollama pull mistral
```

### База данных не доступна

```bash
# Проверьте статус
docker-compose -f docker-compose.prod.yml exec postgres pg_isready -U user

# Проверьте пароль в .env
```

---

## 📞 Поддержка

- GitHub Issues: https://github.com/FLURI3/studeti/issues
- Email: support@studenthelper.dev

---

## 📝 Checklist

- [ ] Сервер настроен (Docker установлен)
- [ ] Домен указывает на сервер (A-запись)
- [ ] SSL сертификаты установлены
- [ ] `.env` файл заполнен
- [ ] Деплой выполнен успешно
- [ ] Backend отвечает на `/health`
- [ ] Frontend открывается в браузере
- [ ] Ollama модель загружена
- [ ] Android APK обновлен с новым URL
- [ ] Firewall настроен
- [ ] Бэкапы настроены
