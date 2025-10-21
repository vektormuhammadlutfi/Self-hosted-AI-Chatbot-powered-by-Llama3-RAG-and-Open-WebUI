# Quick start script for RAG Chatbot (Windows PowerShell)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "RAG Chatbot - Quick Start" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

if (-not (Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host "✓ Docker and Docker Compose are installed" -ForegroundColor Green
Write-Host ""

# Create .env if it doesn't exist
if (-not (Test-Path "backend\.env")) {
    Write-Host "📝 Creating backend\.env from .env.example..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "✓ Created backend\.env" -ForegroundColor Green
} else {
    Write-Host "✓ backend\.env already exists" -ForegroundColor Green
}
Write-Host ""

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Yellow
docker-compose up -d
Write-Host "✓ Services started" -ForegroundColor Green
Write-Host ""

# Wait for Ollama to be ready
Write-Host "⏳ Waiting for Ollama to be ready (this may take 30-60 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Pull Llama3 model
Write-Host "📥 Pulling Llama3 model (this will download ~4.7GB on first run)..." -ForegroundColor Yellow
docker exec openwebui-ollama-1 ollama pull llama3
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  If this failed, the container name might be different. Run:" -ForegroundColor Yellow
    Write-Host "   docker ps" -ForegroundColor Yellow
    Write-Host "   docker exec -it <ollama-container-name> ollama pull llama3" -ForegroundColor Yellow
} else {
    Write-Host "✓ Llama3 model ready" -ForegroundColor Green
}
Write-Host ""

# Check if documents exist
$docs = Get-ChildItem -Path "data\docs" -Include *.pdf,*.txt,*.docx -Recurse -ErrorAction SilentlyContinue
if ($docs.Count -eq 0) {
    Write-Host "⚠️  No documents found in data\docs\" -ForegroundColor Yellow
    Write-Host "   Add your PDF, TXT, or DOCX files to data\docs\ then run:" -ForegroundColor Yellow
    Write-Host "   docker exec openwebui-backend-1 python loader.py" -ForegroundColor Yellow
} else {
    Write-Host "📚 Documents found. Indexing them now..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5  # Give backend time to fully start
    docker exec openwebui-backend-1 python loader.py
    Write-Host "✓ Documents indexed" -ForegroundColor Green
}
Write-Host ""

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access your services:"
Write-Host "  • Open WebUI:    http://localhost:3000"
Write-Host "  • Backend API:   http://localhost:8000"
Write-Host "  • API Docs:      http://localhost:8000/docs"
Write-Host "  • Qdrant:        http://localhost:6333/dashboard"
Write-Host ""
Write-Host "To add more documents:"
Write-Host "  1. Copy files to data\docs\"
Write-Host "  2. Run: docker exec openwebui-backend-1 python loader.py"
Write-Host ""
Write-Host "To view logs:"
Write-Host "  docker-compose logs -f"
Write-Host ""
Write-Host "To stop services:"
Write-Host "  docker-compose down"
Write-Host ""
