#!/bin/bash
# Firebase Setup Script - Автоматизированная настройка
# Использование: bash setup_firebase.sh

set -e

echo "=========================================="
echo "🚀 Firebase Firestore Setup Script"
echo "=========================================="
echo ""

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для печати сообщений
print_step() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Шаг 1: Проверка структуры проекта
print_step "Проверка структуры проекта..."

if [ ! -f "backend/main.py" ]; then
    print_error "backend/main.py не найден"
    exit 1
fi

if [ ! -f "backend/requirements.txt" ]; then
    print_error "backend/requirements.txt не найден"
    exit 1
fi

print_step "Структура проекта OK"
echo ""

# Шаг 2: Создание директорий
print_step "Создание необходимых директорий..."

mkdir -p backend/config
mkdir -p backend/data
mkdir -p logs

print_step "Директории созданы"
echo ""

# Шаг 3: Проверка Firebase credentials
print_step "Проверка Firebase credentials..."

if [ -f "backend/config/firebase-credentials.json" ]; then
    print_step "Firebase credentials найдены"
else
    print_warning "Firebase credentials не найдены"
    echo ""
    echo "Пожалуйста, выполните следующее:"
    echo "1. Перейдите на https://console.firebase.google.com/"
    echo "2. Создайте новый проект 'studeti'"
    echo "3. Включите Firestore Database (Production mode)"
    echo "4. Создайте Service Account:"
    echo "   - Параметры проекта → Служебные аккаунты → Python → Создать ключ"
    echo "5. Скопируйте загруженный JSON файл в:"
    echo "   backend/config/firebase-credentials.json"
    echo ""
    read -p "Нажмите Enter когда файл будет скопирован..."
    
    if [ ! -f "backend/config/firebase-credentials.json" ]; then
        print_error "Firebase credentials по-прежнему не найдены. Выход."
        exit 1
    fi
    
    print_step "Firebase credentials установлены"
fi

echo ""

# Шаг 4: Установка зависимостей Python
print_step "Установка Python зависимостей..."

if command -v pip &> /dev/null; then
    if pip install firebase-admin==6.2.0 2>&1 | grep -q "Successfully installed"; then
        print_step "firebase-admin установлен"
    else
        print_warning "firebase-admin может быть уже установлен или возникла ошибка"
    fi
else
    print_error "pip не найден. Установите Python 3.8+"
    exit 1
fi

echo ""

# Шаг 5: Проверка конфигурации .env
print_step "Проверка конфигурации .env..."

if [ ! -f ".env" ]; then
    print_warning ".env файл не найден, создаю из примера..."
    if [ -f ".env.firebase.example" ]; then
        cp .env.firebase.example .env
        print_step ".env создан из примера"
        echo ""
        echo "ВАЖНО: Отредактируйте .env и добавьте свои значения!"
    else
        print_error ".env.firebase.example не найден"
        exit 1
    fi
else
    print_step ".env файл найден"
fi

echo ""

# Шаг 6: Проверка подключения к Firebase
print_step "Проверка подключения к Firebase..."

cat > /tmp/test_firebase.py << 'EOF'
import sys
sys.path.insert(0, 'backend')

try:
    from services.firebase_service import firebase_service
    
    # Попытка подключиться
    db = firebase_service.db
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
EOF

if python3 /tmp/test_firebase.py 2>&1 | grep -q "SUCCESS"; then
    print_step "Подключение к Firebase OK"
else
    print_error "Не удалось подключиться к Firebase"
    echo ""
    echo "Проверьте:"
    echo "1. Firebase credentials скопирован в backend/config/"
    echo "2. FIREBASE_CREDENTIALS_PATH установлен в .env"
    echo "3. Firebase проект активен"
    exit 1
fi

rm /tmp/test_firebase.py
echo ""

# Шаг 7: Создание Security Rules
print_step "Инструкции для Security Rules..."

echo ""
echo "СЛЕДУЮЩИЙ ШАГ: Установить Security Rules в Firebase"
echo ""
echo "1. Перейдите на https://console.firebase.google.com/"
echo "2. Выберите проект 'studeti'"
echo "3. Firestore Database → Rules"
echo "4. Замените содержимое на:"
echo ""
cat > /tmp/firestore_rules.txt << 'RULES'
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    
    match /users/{username} {
      allow read, write: if request.auth.uid == username;
    }
    
    match /documents/{documentId} {
      allow read, write: if request.auth.uid == resource.data.user_id;
      allow create: if request.auth.uid == request.resource.data.user_id;
    }
    
    match /user_documents_index/{userId} {
      allow read, write: if request.auth.uid == userId;
    }
  }
}
RULES

cat /tmp/firestore_rules.txt
echo ""
echo "5. Нажмите 'Опубликовать'"
echo ""

read -p "Нажмите Enter когда Rules будут опубликованы..."

rm /tmp/firestore_rules.txt
echo ""

# Шаг 8: Миграция данных (опционально)
print_step "Готовность к миграции данных..."

if [ -f "backend/data/users.json" ] && [ -f "backend/data/documents.json" ]; then
    read -p "Найдены JSON файлы. Выполнить миграцию? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_step "Запуск миграции..."
        python3 migrate_to_firebase.py
        print_step "Миграция завершена"
    else
        print_warning "Миграция пропущена"
    fi
else
    print_warning "JSON файлы не найдены - миграция пропущена"
fi

echo ""

# Шаг 9: Тестирование приложения
print_step "Готовность к тестированию..."

echo ""
echo "Для локального тестирования запустите:"
echo ""
echo "  python3 backend/main.py"
echo ""
echo "Для Docker тестирования запустите:"
echo ""
echo "  docker-compose -f docker-compose.firebase.yml up"
echo ""
echo "Тестовые endpoints:"
echo ""
echo "  POST   http://localhost:8000/api/auth/register"
echo "  POST   http://localhost:8000/api/auth/login"
echo "  GET    http://localhost:8000/api/auth/me"
echo "  PUT    http://localhost:8000/api/auth/profile"
echo ""
echo "  POST   http://localhost:8000/api/documents/save"
echo "  GET    http://localhost:8000/api/documents/my"
echo ""

# Шаг 10: Справка
print_step "Справка и документация"

echo ""
echo "Документация:"
echo "  📖 FIREBASE_QUICKSTART.md - Быстрый старт"
echo "  📖 FIREBASE_SETUP.md - Полная инструкция"
echo "  📖 DATABASE_COMPARISON.md - Сравнение БД"
echo "  📖 examples_firebase_api.py - Примеры кода"
echo ""
echo "Файлы конфигурации:"
echo "  ⚙️  backend/services/firebase_service.py"
echo "  ⚙️  backend/routes/auth_firebase.py"
echo "  ⚙️  backend/routes/documents_firebase.py"
echo "  ⚙️  docker-compose.firebase.yml"
echo ""

# Финальное сообщение
echo ""
echo "=========================================="
print_step "Firebase Firestore успешно настроен!"
echo "=========================================="
echo ""
echo "Следующие шаги:"
echo "1. ✓ Установить Security Rules (см. выше)"
echo "2. ✓ Запустить приложение (python3 backend/main.py)"
echo "3. ✓ Протестировать API endpoints"
echo "4. ✓ Прочитать документацию"
echo ""
