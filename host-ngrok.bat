@echo off
chcp 65001 >nul
title Student Helper - Ngrok Setup

echo.
echo ================================================
echo    🚀 Student Helper - Ngrok Hosting
echo ================================================
echo.

REM Проверка ngrok
where ngrok >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ngrok не найден!
    echo.
    echo Скачайте и установите Ngrok:
    echo https://ngrok.com/download
    echo.
    echo Или установите через Chocolatey:
    echo choco install ngrok
    pause
    exit /b 1
)

echo ✅ Ngrok установлен
echo.

REM Запуск Docker
echo [1/4] Запуск Docker контейнеров...
docker-compose up -d
if %errorlevel% neq 0 (
    echo ❌ Ошибка запуска Docker
    pause
    exit /b 1
)

echo.
echo ✅ Контейнеры запущены
timeout /t 5 /nobreak >nul

REM Запуск Ngrok для backend
echo.
echo [2/4] Запуск Ngrok для Backend (порт 8000)...
start "Backend Ngrok" powershell -NoExit -Command "Write-Host ''; Write-Host '🔗 BACKEND TUNNEL' -ForegroundColor Cyan; Write-Host ''; Write-Host '⚠️  СКОПИРУЙТЕ ЭТОТ URL:' -ForegroundColor Yellow; Write-Host ''; ngrok http 8000"

timeout /t 3 /nobreak >nul

REM Запуск Ngrok для frontend
echo.
echo [3/4] Запуск Ngrok для Frontend (порт 5173)...
start "Frontend Ngrok" powershell -NoExit -Command "Write-Host ''; Write-Host '🌐 FRONTEND TUNNEL' -ForegroundColor Green; Write-Host ''; Write-Host '✅ ОТКРОЙТЕ ЭТОТ URL В БРАУЗЕРЕ:' -ForegroundColor Green; Write-Host ''; ngrok http 5173"

echo.
echo ================================================
echo    ✅ Готово!
echo ================================================
echo.
echo 📋 Открылись 2 окна:
echo.
echo    1. Backend Ngrok  - Скопируйте https://xxxxx.ngrok.io
echo    2. Frontend Ngrok - Откройте https://yyyyy.ngrok.io
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo [4/4] Настройка:
echo.
echo    Создайте файл frontend\.env со строкой:
echo    VITE_API_URL=https://xxxxx.ngrok.io
echo.
echo    (замените xxxxx на URL из Backend Ngrok)
echo.
echo    Затем перезапустите:
echo    docker-compose restart frontend
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📱 Для Android приложения используйте Frontend URL:
echo    https://yyyyy.ngrok.io
echo.
echo Нажмите любую клавишу для выхода...
pause >nul
