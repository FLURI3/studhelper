@echo off
echo ================================================
echo    Student Helper - Ngrok Quick Start
echo ================================================
echo.

REM Проверка Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker не установлен!
    echo Установите Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Проверка Ngrok
if not exist "C:\ngrok\ngrok.exe" (
    echo [ERROR] Ngrok не найден!
    echo.
    echo Установите Ngrok:
    echo 1. Скачайте: https://ngrok.com/download
    echo 2. Распакуйте в C:\ngrok\
    echo 3. Зарегистрируйтесь и получите токен
    echo 4. Выполните: C:\ngrok\ngrok.exe authtoken YOUR_TOKEN
    pause
    exit /b 1
)

echo [1/3] Запуск Docker контейнеров...
docker-compose up -d

echo.
echo [2/3] Ожидание запуска сервисов...
timeout /t 10 /nobreak >nul

echo.
echo [3/3] Запуск Ngrok...
echo.
echo ================================================
echo  Ngrok туннели запускаются...
echo ================================================
echo.
echo Откроются 2 окна:
echo  1. Backend  (порт 8000) - Скопируйте URL
echo  2. Frontend (порт 5173) - Используйте этот URL
echo.
echo После запуска:
echo  1. Скопируйте Backend URL из первого окна
echo  2. Обновите VITE_API_URL в frontend/.env
echo  3. Перезапустите: docker-compose restart frontend
echo  4. Используйте Frontend URL для доступа
echo.
pause

REM Запуск Ngrok для backend
start "Ngrok Backend" cmd /k "C:\ngrok\ngrok.exe http 8000"

REM Ожидание 2 секунды
timeout /t 2 /nobreak >nul

REM Запуск Ngrok для frontend
start "Ngrok Frontend" cmd /k "C:\ngrok\ngrok.exe http 5173"

echo.
echo ================================================
echo  Готово! Проверьте окна Ngrok
echo ================================================
pause
