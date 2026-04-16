# Автоматическая настройка Ngrok URLs

Write-Host ""
Write-Host "🔧 Настройка Student Helper с Ngrok" -ForegroundColor Cyan
Write-Host ""

# Получение Ngrok URLs через API
Write-Host "Проверка Ngrok туннелей..." -ForegroundColor Yellow

$error.Clear()
$backendUrl = ""
$frontendUrl = ""

try {
    $ngrokApi = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels" -ErrorAction Stop
    
    foreach ($tunnel in $ngrokApi.tunnels) {
        if ($tunnel.config.addr -like "*8000*") {
            $backendUrl = $tunnel.public_url
        }
        if ($tunnel.config.addr -like "*5173*") {
            $frontendUrl = $tunnel.public_url
        }
    }
    
    if ($backendUrl -ne "" -and $frontendUrl -ne "") {
        Write-Host ""
        Write-Host "✅ Найдены Ngrok туннели:" -ForegroundColor Green
        Write-Host ""
        Write-Host "   Backend:  $backendUrl" -ForegroundColor White
        Write-Host "   Frontend: $frontendUrl" -ForegroundColor White
        Write-Host ""
        
        # Создание .env файла
        $envContent = "VITE_API_URL=$backendUrl"
        Set-Content -Path "frontend/.env" -Value $envContent
        
        Write-Host "✅ Создан frontend/.env" -ForegroundColor Green
        
        # Перезапуск frontend
        Write-Host ""
        Write-Host "Перезапуск frontend..." -ForegroundColor Yellow
        docker-compose restart frontend
        
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host "🎉 Готово! Приложение доступно по адресу:" -ForegroundColor Green
        Write-Host ""
        Write-Host "   $frontendUrl" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
        Write-Host ""
        
        Write-Host "📱 Для Android приложения обновите URL:" -ForegroundColor Yellow
        Write-Host "   BASE_URL = `"$frontendUrl`"" -ForegroundColor White
        Write-Host ""
        
        # Копирование в буфер обмена
        Set-Clipboard -Value $frontendUrl
        Write-Host "📋 Frontend URL скопирован в буфер обмена!" -ForegroundColor Green
        
        # Открытие в браузере
        Start-Process $frontendUrl
    }
    else {
        Write-Host ""
        Write-Host "❌ Туннели не найдены" -ForegroundColor Red
        Write-Host "Убедитесь что Ngrok запущен для портов 8000 и 5173" -ForegroundColor Yellow
    }
}
catch {
    Write-Host ""
    Write-Host "❌ Не удалось подключиться к Ngrok API" -ForegroundColor Red
    Write-Host ""
    Write-Host "Вручную:" -ForegroundColor Yellow
    Write-Host "1. Посмотрите URLs в окнах Ngrok" -ForegroundColor White
    Write-Host "2. Создайте frontend/.env:" -ForegroundColor White
    Write-Host "   VITE_API_URL=https://your-backend.ngrok.io" -ForegroundColor Gray
    Write-Host "3. Перезапустите: docker-compose restart frontend" -ForegroundColor White
    Write-Host ""
}

Write-Host "Нажмите Enter для выхода..."
Read-Host
