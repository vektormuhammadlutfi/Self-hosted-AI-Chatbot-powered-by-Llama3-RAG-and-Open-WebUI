# Test OpenRouter and Gemini API Keys
# Run this to verify your API keys are working

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Testing API Keys" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Load environment variables
$envFile = Get-Content "backend\.env"
$openrouterKey = ($envFile | Select-String "OPENROUTER_API_KEY=").ToString().Split("=")[1]
$geminiKey = ($envFile | Select-String "GOOGLE_API_KEY=").ToString().Split("=")[1]

Write-Host "OpenRouter API Key: $($openrouterKey.Substring(0,20))..." -ForegroundColor Yellow
Write-Host "Gemini API Key: $($geminiKey.Substring(0,20))..." -ForegroundColor Yellow
Write-Host ""

# Test OpenRouter
Write-Host "Testing OpenRouter..." -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $openrouterKey"
        "HTTP-Referer" = "http://localhost:3000"
    }
    $response = Invoke-RestMethod -Uri "https://openrouter.ai/api/v1/models" -Headers $headers -Method Get -TimeoutSec 10
    Write-Host "✓ OpenRouter API is working!" -ForegroundColor Green
    Write-Host "  Available models: $($response.data.Count)" -ForegroundColor Green
    Write-Host "  Sample models:" -ForegroundColor Cyan
    $response.data | Select-Object -First 5 | ForEach-Object {
        Write-Host "    - $($_.id)" -ForegroundColor White
    }
} catch {
    Write-Host "✗ OpenRouter API failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""

# Test Gemini
Write-Host "Testing Google Gemini..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "https://generativelanguage.googleapis.com/v1beta/models?key=$geminiKey" -Method Get -TimeoutSec 10
    Write-Host "✓ Gemini API is working!" -ForegroundColor Green
    Write-Host "  Available models: $($response.models.Count)" -ForegroundColor Green
    Write-Host "  Sample models:" -ForegroundColor Cyan
    $response.models | Select-Object -First 5 | ForEach-Object {
        Write-Host "    - $($_.name)" -ForegroundColor White
    }
} catch {
    Write-Host "✗ Gemini API failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Test Complete!" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
