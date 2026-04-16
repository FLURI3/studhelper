# 🚀 Student Helper - Production Deployment (Windows)

Write-Host "🚀 Student Helper - Production Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Проверка .env файла
if (-not (Test-Path .env)) {
    Write-Host "❌ Файл .env не найден!" -ForegroundColor Red
    Write-Host "📝 Скопируйте .env.production.example в .env и заполните значения:" -ForegroundColor Yellow
    Write-Host "   Copy-Item .env.production.example .env" -ForegroundColor Yellow
    Write-Host "   notepad .env" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Переменные окружения найдены" -ForegroundColor Green

# Загрузка переменных из .env
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^#][^=]+)=(.+)$') {
        $name = $matches[1].Trim()
        $value = $matches[2].Trim()
        Set-Item -Path "env:$name" -Value $value
    }
}

$domain = $env:DOMAIN
if (-not $domain) {
    Write-Host "❌ DOMAIN не указан в .env файле!" -ForegroundColor Red
    exit 1
}

Write-Host "🔧 Настройка для домена: $domain" -ForegroundColor Yellow

# Замена домена в nginx.conf
$nginxConf = Get-Content nginx/nginx.conf -Raw
$nginxConf = $nginxConf -replace 'your-domain.com', $domain
Set-Content nginx/nginx.conf -Value $nginxConf

# Остановка старых контейнеров
Write-Host "⏹️  Остановка старых контейнеров..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yml down

# Сборка образов
Write-Host "🏗️  Сборка Docker образов..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yml build --no-cache

# Запуск контейнеров
Write-Host "🚀 Запуск сервисов..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yml up -d

# Ожидание запуска
Write-Host "⏳ Ожидание запуска сервисов..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Проверка Ollama
Write-Host "🤖 Настройка Ollama..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yml exec ollama ollama pull mistral

# Проверка здоровья
Write-Host "🔍 Проверка работоспособности..." -ForegroundColor Yellow
docker-compose -f docker-compose.prod.yml ps

# Тест backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend работает!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Backend не отвечает" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Деплой завершен!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host "📱 Приложение: https://$domain" -ForegroundColor Cyan
Write-Host "📚 API Docs: https://$domain/docs" -ForegroundColor Cyan
Write-Host "💚 Health: https://$domain/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Мониторинг:" -ForegroundColor Yellow
Write-Host "   docker-compose -f docker-compose.prod.yml logs -f" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Не забудьте настроить SSL сертификаты!" -ForegroundColor Yellow
Write-Host "   Разместите сертификаты в nginx/ssl/" -ForegroundColor White
