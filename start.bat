@echo off
chcp 65001 >nul
echo ====================================
echo  Student Helper - Запуск проекта
echo ====================================
echo.

echo Проверка Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Docker не установлен!
    echo Установите Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo Docker найден!
echo.

echo Проверка Docker Engine...
docker ps >nul 2>&1
if errorlevel 1 (
    echo.
    echo ╔═══════════════════════════════════════════════════════╗
    echo ║  ВНИМАНИЕ: Docker Desktop НЕ ЗАПУЩЕН!                ║
    echo ╚═══════════════════════════════════════════════════════╝
    echo.
    echo Пожалуйста:
    echo 1. Запустите Docker Desktop
    echo 2. Дождитесь, пока он полностью загрузится
    echo 3. Запустите этот скрипт снова
    echo.
    pause
    exit /b 1
)

echo Docker Engine работает!
echo.

echo Запуск контейнеров...
docker-compose up -d

if errorlevel 1 (
    echo.
    echo ОШИБКА при запуске контейнеров!
    echo Проверьте логи: docker-compose logs
    echo.
    pause
    exit /b 1
)

echo.
echo ====================================
echo Контейнеры запущены!
echo ====================================
echo.
echo Ждем 10 секунд, пока сервисы запустятся...
timeout /t 10 /nobreak >nul

echo.
echo Загрузка модели Ollama (mistral)...
echo Это может занять несколько минут при первом запуске...
docker exec studeti-ollama-1 ollama pull mistral

echo.
echo ====================================
echo Проект готов к работе!
echo ====================================
echo.
echo Frontend: http://localhost:5173
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Для остановки: docker-compose down
echo.

start http://localhost:5173

pause
