# 🚀 Деплой на flurisrv.ru

## ✅ Что уже настроено:

- Domain: flurisrv.ru
- Nginx конфигурация обновлена
- .env файл создан с паролями
- API будет доступен через https://flurisrv.ru/api

## 📋 Инструкция по деплою:

### Вариант 1: У вас есть VPS/Сервер

#### 1️⃣ Подключитесь к серверу:
```bash
ssh root@flurisrv.ru
# или
ssh root@ВАШ_IP
```

#### 2️⃣ Установите Docker (если не установлен):
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

#### 3️⃣ Скопируйте проект на сервер:

**С вашего компьютера:**
```powershell
# Создайте архив
Compress-Archive -Path C:\Users\RobotComp.ru\Desktop\studeti\* -DestinationPath studeti.zip

# Загрузите через SFTP или SCP
scp studeti.zip root@flurisrv.ru:/root/
```

**На сервере:**
```bash
cd /root
unzip studeti.zip -d studeti
cd studeti
```

#### 4️⃣ Настройте DNS:

В панели управления доменом создайте A-запись:
```
Type: A
Name: @
Value: IP_ВАШЕГО_СЕРВЕРА
TTL: 3600
```

И для www:
```
Type: CNAME
Name: www
Value: flurisrv.ru
TTL: 3600
```

#### 5️⃣ Получите SSL сертификат:

```bash
# Установите Certbot
apt-get update
apt-get install certbot -y

# Остановите Docker если запущен
docker-compose down

# Получите сертификат
certbot certonly --standalone -d flurisrv.ru -d www.flurisrv.ru

# Скопируйте сертификаты
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/flurisrv.ru/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/flurisrv.ru/privkey.pem nginx/ssl/
chmod 644 nginx/ssl/*
```

#### 6️⃣ Запустите проект:

```bash
# Сборка и запуск
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Загрузите модель Ollama
docker-compose -f docker-compose.prod.yml exec ollama ollama pull mistral

# Проверка
docker-compose -f docker-compose.prod.yml ps
curl https://flurisrv.ru/health
```

#### 7️⃣ Настройте автообновление SSL:

```bash
# Добавьте в crontab
crontab -e

# Добавьте строку:
0 0 * * * certbot renew --quiet && docker-compose -f /root/studeti/docker-compose.prod.yml restart nginx
```

#### 8️⃣ Настройте Firewall:

```bash
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

### Вариант 2: Хостинг на текущем ПК (Windows)

Если хотите хостить на этом компьютере:

#### 1️⃣ Настройте роутер (Port Forwarding):

Пробросьте порты:
- 80 → IP вашего ПК:80
- 443 → IP вашего ПК:443

#### 2️⃣ Настройте DNS:

A-запись домена должна указывать на ваш внешний IP:
```powershell
# Узнайте свой внешний IP
Invoke-WebRequest -Uri "https://api.ipify.org" | Select-Object -ExpandProperty Content
```

#### 3️⃣ Получите SSL сертификат:

Скачайте Win-Acme: https://www.win-acme.com/

```powershell
# Запустите wacs.exe и следуйте инструкциям
.\wacs.exe
```

#### 4️⃣ Запустите:

```powershell
docker-compose -f docker-compose.prod.yml up -d
```

---

### Вариант 3: Ngrok (Временное решение)

Если нужно быстро протестировать без сервера:

```powershell
# Запустите приложение
docker-compose up -d

# Запустите Ngrok (в отдельных окнах)
ngrok http 8000  # Backend
ngrok http 5173  # Frontend
```

Минусы: рандомные URL, ограничения бесплатной версии

---

## 🔧 После деплоя:

### Обновите Android приложение:

```java
// android/app/src/main/java/com/studenthelper/app/MainActivity.java
private static final String BASE_URL = "https://flurisrv.ru";
```

Соберите APK:
```powershell
cd android
.\gradlew.bat assembleRelease
```

---

## 📊 Проверка работы:

```bash
# Статус контейнеров
docker-compose -f docker-compose.prod.yml ps

# Логи
docker-compose -f docker-compose.prod.yml logs -f

# Проверка сайта
curl https://flurisrv.ru
curl https://flurisrv.ru/api/health
curl https://flurisrv.ru/docs
```

---

## 🆘 Решение проблем:

### Nginx не запускается:
```bash
docker-compose -f docker-compose.prod.yml logs nginx
```

### SSL ошибки:
```bash
ls -la nginx/ssl/
# Должны быть fullchain.pem и privkey.pem
```

### Backend не отвечает:
```bash
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml restart backend
```

---

## 📝 Файлы на сервере:

```
/root/studeti/
├── .env                          # ✅ Готов
├── docker-compose.prod.yml       # ✅ Готов
├── nginx/
│   ├── nginx.conf                # ✅ Настроен для flurisrv.ru
│   └── ssl/
│       ├── fullchain.pem         # ⚠️ Нужно получить
│       └── privkey.pem           # ⚠️ Нужно получить
├── frontend/
│   └── Dockerfile.prod           # ✅ Готов
└── backend/
    └── Dockerfile.prod           # ✅ Готов
```

---

## ☁️ Рекомендуемые провайдеры VPS:

- **Hetzner**: €5.83/мес (CX21, 4GB RAM)
- **DigitalOcean**: $24/мес (4GB Droplet)
- **AWS EC2**: ~$30/мес (t3.medium)
- **Timeweb** (RU): ~500₽/мес

---

Какой вариант деплоя выберете?
