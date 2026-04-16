# 🚀 Быстрый деплой на домен

## Что подготовлено:

✅ **Docker Compose** для production  
✅ **Nginx** с SSL и reverse proxy  
✅ **Автоматический скрипт** деплоя  
✅ **Production Dockerfiles** для frontend и backend  
✅ **Инструкция** в PRODUCTION.md  

---

## 📋 Что вам нужно:

1. **Сервер/VPS** (Ubuntu 20.04+, минимум 4GB RAM)
2. **Домен** с DNS записью на сервер
3. **SSL сертификат** (Let's Encrypt или свой)

---

## ⚡ Быстрый старт (5 минут):

### 1️⃣ На сервере установите Docker:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

### 2️⃣ Клонируйте проект:

```bash
git clone https://github.com/FLURI3/studeti.git
cd studeti
```

### 3️⃣ Настройте окружение:

```bash
cp .env.production.example .env
nano .env
```

Заполните:
```env
DB_PASSWORD=your-strong-password
JWT_SECRET=your-secret-key-32-chars
DOMAIN=your-domain.com
VITE_API_URL=https://your-domain.com/api
```

### 4️⃣ Получите SSL сертификат:

**Let's Encrypt (рекомендуется):**
```bash
apt-get install certbot
certbot certonly --standalone -d your-domain.com
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/
```

**Или самоподписанный (для тестов):**
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/privkey.pem \
  -out nginx/ssl/fullchain.pem \
  -subj "/CN=your-domain.com"
```

### 5️⃣ Запустите деплой:

```bash
chmod +x deploy.sh
./deploy.sh
```

### 6️⃣ Готово! 🎉

Откройте: **https://your-domain.com**

---

## 📱 Обновите Android приложение:

Измените URL в `android/app/src/main/java/com/studenthelper/app/MainActivity.java`:

```java
private static final String BASE_URL = "https://your-domain.com";
```

Соберите APK:
```bash
cd android
./gradlew assembleRelease
```

APK будет в: `app/build/outputs/apk/release/`

---

## 🔧 Полезные команды:

```bash
# Посмотреть логи
docker-compose -f docker-compose.prod.yml logs -f

# Перезапустить
docker-compose -f docker-compose.prod.yml restart

# Остановить
docker-compose -f docker-compose.prod.yml down

# Обновить
git pull
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d
```

---

## 📚 Подробная документация:

Смотрите **PRODUCTION.md** для:
- Детальных инструкций
- Настройки безопасности
- Мониторинга
- Решения проблем
- Бэкапов

---

## 🌍 Облачные провайдеры:

### DigitalOcean (рекомендуется):
- Создайте Droplet: Ubuntu 22.04, 4GB RAM ($24/мес)
- Следуйте инструкциям выше

### AWS EC2:
- Запустите t3.medium инстанс
- Откройте порты 80, 443 в Security Group

### Hetzner (дешевле):
- Cloud Server CX21 (4GB RAM, €5.83/мес)
- Следуйте инструкциям выше

---

## ⚠️ Важно:

1. **Откройте порты**: 22 (SSH), 80 (HTTP), 443 (HTTPS)
2. **Настройте Firewall**: UFW или встроенный
3. **Автообновление SSL**: Certbot автоматически обновляет
4. **Бэкапы**: Настройте регулярные бэкапы БД

---

## 🆘 Проблемы?

1. Проверьте логи: `docker-compose -f docker-compose.prod.yml logs`
2. Проверьте DNS: `nslookup your-domain.com`
3. Проверьте SSL: `curl -I https://your-domain.com`
4. Смотрите **PRODUCTION.md** раздел "Решение проблем"

---

## 📞 Поддержка:

- GitHub Issues: https://github.com/FLURI3/studeti/issues
- Email: support@studenthelper.dev

---

**Удачного деплоя! 🚀**
