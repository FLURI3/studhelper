@echo off
chcp 65001 >nul
echo Остановка контейнеров Student Helper...
docker-compose down
echo Готово!
pause
