Write-Host "`n🔧 Получение Ngrok URLs...`n" -ForegroundColor Cyan

Start-Sleep -Seconds 2

$api = Invoke-RestMethod -Uri "http://localhost:4040/api/tunnels"

$backend = ""
$frontend = ""

foreach ($t in $api.tunnels) {
    if ($t.config.addr -like "*8000*") { $backend = $t.public_url }
    if ($t.config.addr -like "*5173*") { $frontend = $t.public_url }
}

if ($backend -and $frontend) {
    Write-Host "✅ Backend:  $backend" -ForegroundColor Green
    Write-Host "✅ Frontend: $frontend" -ForegroundColor Green
    Write-Host ""
    
    "VITE_API_URL=$backend" | Out-File -FilePath "frontend/.env" -Encoding utf8
    Write-Host "✅ Создан frontend/.env" -ForegroundColor Green
    
    Write-Host "`nПерезапуск frontend..." -ForegroundColor Yellow
    docker-compose restart frontend
    
    Write-Host "`n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
    Write-Host "🎉 Откройте: $frontend" -ForegroundColor Green
    Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━`n" -ForegroundColor Cyan
    
    Set-Clipboard -Value $frontend
    Start-Process $frontend
}
else {
    Write-Host "❌ Ngrok туннели не найдены" -ForegroundColor Red
    Write-Host "Посмотрите URLs в окнах Ngrok" -ForegroundColor Yellow
}
