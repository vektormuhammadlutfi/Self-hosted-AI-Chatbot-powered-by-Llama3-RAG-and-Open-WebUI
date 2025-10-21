#!/bin/bash
# Quick start script for RAG Chatbot

set -e

echo "======================================"
echo "RAG Chatbot - Quick Start"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Create .env if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from .env.example..."
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env"
else
    echo "✓ backend/.env already exists"
fi
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose up -d
echo "✓ Services started"
echo ""

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready (this may take 30-60 seconds)..."
sleep 30

# Pull Llama3 model
echo "📥 Pulling Llama3 model (this will download ~4.7GB on first run)..."
docker exec openwebui-ollama-1 ollama pull llama3 || {
    echo "⚠️  If this fails, the container name might be different. Run:"
    echo "   docker ps"
    echo "   docker exec -it <ollama-container-name> ollama pull llama3"
}
echo "✓ Llama3 model ready"
echo ""

# Check if documents exist
if [ -z "$(ls -A data/docs 2>/dev/null | grep -E '\.(pdf|txt|docx)$')" ]; then
    echo "⚠️  No documents found in data/docs/"
    echo "   Add your PDF, TXT, or DOCX files to data/docs/ then run:"
    echo "   docker exec openwebui-backend-1 python loader.py"
else
    echo "📚 Documents found. Indexing them now..."
    sleep 5  # Give backend time to fully start
    docker exec openwebui-backend-1 python loader.py
    echo "✓ Documents indexed"
fi
echo ""

echo "======================================"
echo "✅ Setup Complete!"
echo "======================================"
echo ""
echo "Access your services:"
echo "  • Open WebUI:    http://localhost:3000"
echo "  • Backend API:   http://localhost:8000"
echo "  • API Docs:      http://localhost:8000/docs"
echo "  • Qdrant:        http://localhost:6333/dashboard"
echo ""
echo "To add more documents:"
echo "  1. Copy files to data/docs/"
echo "  2. Run: docker exec openwebui-backend-1 python loader.py"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
