#!/bin/bash

# 🚀 Скрипт деплоя Student Helper на сервер

set -e

echo "🚀 Student Helper - Production Deployment"
echo "=========================================="

# Проверка .env файла
if [ ! -f .env ]; then
    echo "❌ Файл .env не найден!"
    echo "📝 Скопируйте .env.production.example в .env и заполните значения:"
    echo "   cp .env.production.example .env"
    echo "   nano .env"
    exit 1
fi

# Загрузка переменных окружения
export $(cat .env | xargs)

echo "✅ Переменные окружения загружены"

# Замена домена в конфигурации Nginx
echo "🔧 Настройка Nginx для домена: $DOMAIN"
sed -i "s/your-domain.com/$DOMAIN/g" nginx/nginx.conf

# Остановка старых контейнеров
echo "⏹️  Остановка старых контейнеров..."
docker-compose -f docker-compose.prod.yml down

# Сборка образов
echo "🏗️  Сборка Docker образов..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Запуск контейнеров
echo "🚀 Запуск сервисов..."
docker-compose -f docker-compose.prod.yml up -d

# Ожидание запуска
echo "⏳ Ожидание запуска сервисов..."
sleep 10

# Проверка Ollama и загрузка модели
echo "🤖 Настройка Ollama..."
docker-compose -f docker-compose.prod.yml exec -T ollama ollama pull mistral || echo "⚠️  Модель будет загружена при первом использовании"

# Проверка здоровья сервисов
echo "🔍 Проверка работоспособности..."
docker-compose -f docker-compose.prod.yml ps

# Тест backend
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ Backend работает!"
else
    echo "❌ Backend не отвечает"
fi

echo ""
echo "🎉 Деплой завершен!"
echo "================================"
echo "📱 Приложение: https://$DOMAIN"
echo "📚 API Docs: https://$DOMAIN/docs"
echo "💚 Health: https://$DOMAIN/health"
echo ""
echo "📊 Мониторинг:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "⚠️  Не забудьте настроить SSL сертификаты!"
echo "   Используйте Let's Encrypt или разместите сертификаты в nginx/ssl/"
