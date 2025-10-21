# Project Summary

## 📊 Project Overview

**RAG Chatbot** is a complete, production-ready, local-first AI chatbot system using Retrieval-Augmented Generation.

### Quick Stats

- **Language**: Python 3.11+
- **Framework**: FastAPI + LlamaIndex
- **LLM**: Ollama (Llama3)
- **Vector DB**: Qdrant
- **Frontend**: Open WebUI
- **Deployment**: Docker Compose
- **License**: MIT

## 📁 File Structure

```
openwebui/
├── README.md                    # Main documentation (setup, usage, deployment)
├── ARCHITECTURE.md              # System architecture and data flow diagrams
├── CONTRIBUTING.md              # Contribution guidelines
├── docker-compose.yml           # Service orchestration (Qdrant, Ollama, Backend, WebUI)
├── .gitignore                   # Git ignore rules
├── start.sh                     # Quick start script (Linux/macOS)
├── start.ps1                    # Quick start script (Windows)
├── test_api.py                  # API testing script
│
├── backend/                     # FastAPI backend service
│   ├── Dockerfile              # Backend container definition
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # Environment configuration (not in git)
│   ├── .env.example           # Example environment file
│   ├── main.py                # FastAPI app with /ask, /health, /stats endpoints
│   ├── engine.py              # RAG engine (LlamaIndex + Ollama + Qdrant)
│   ├── loader.py              # Document loader (PDF/TXT/DOCX → Qdrant)
│   └── db_loader.py           # Database loader (PostgreSQL/MySQL → Qdrant)
│
└── data/
    └── docs/                   # Document storage for indexing
        ├── README.md          # Instructions for adding documents
        └── sample-document.txt # Sample document for testing
```

## 🔑 Key Features

### 1. Local-First Architecture
- No external API dependencies
- Complete data privacy
- Run entirely offline
- Zero ongoing costs

### 2. Document Intelligence
- Supports PDF, TXT, DOCX
- Automatic chunking and embedding
- Semantic search with Qdrant
- Source attribution in responses

### 3. Database Integration
- Optional PostgreSQL/MySQL support
- Index structured data (FAQs, catalogs)
- Custom schema support
- Flexible filtering

### 4. Production-Ready
- Docker Compose orchestration
- Health check endpoints
- Comprehensive logging
- Error handling

### 5. Developer-Friendly
- Clear documentation
- Example scripts
- Test utilities
- Easy customization

## 🚀 Quick Start Commands

```bash
# Linux/macOS
./start.sh

# Windows
.\start.ps1

# Manual
docker-compose up -d
docker exec openwebui-ollama-1 ollama pull llama3
docker exec openwebui-backend-1 python loader.py
```

## 🌐 Service URLs

| Service | URL | Purpose |
|---------|-----|---------|
| Open WebUI | http://localhost:3000 | Chat interface |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger UI |
| Qdrant | http://localhost:6333/dashboard | Vector DB UI |

## 📊 API Endpoints

### POST `/ask`
Query the RAG system with a question.

**Request:**
```json
{
  "question": "What are the key features?"
}
```

**Response:**
```json
{
  "answer": "The key features include...",
  "sources": [...]
}
```

### GET `/health`
Check backend health status.

### GET `/stats`
Get vector database statistics.

## 🔧 Configuration

### Environment Variables (backend/.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://ollama:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | `llama3` | LLM model name |
| `QDRANT_HOST` | `qdrant` | Qdrant hostname |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `QDRANT_COLLECTION` | `documents` | Collection name |
| `CHUNK_SIZE` | `512` | Document chunk size |
| `CHUNK_OVERLAP` | `50` | Chunk overlap tokens |

### Database Configuration (Optional)

| Variable | Example | Description |
|----------|---------|-------------|
| `DB_TYPE` | `postgresql` | Database type |
| `DB_HOST` | `localhost` | Database host |
| `DB_PORT` | `5432` | Database port |
| `DB_NAME` | `mydb` | Database name |
| `DB_USER` | `user` | Database user |
| `DB_PASSWORD` | `password` | Database password |
| `DB_TABLE` | `faq` | Table to index |

## 🧪 Testing

### Run API Tests
```bash
# Install requests library (if testing from host)
pip install requests

# Run tests
python test_api.py
```

### Manual Testing
```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'

# Get stats
curl http://localhost:8000/stats
```

## 📈 Performance

### Expected Performance (8GB RAM, CPU-only)

| Metric | Value |
|--------|-------|
| Indexing Speed | ~10-20 docs/min |
| Query Response Time | 2-10 seconds |
| Concurrent Users | 1-10 |
| Document Limit | ~10,000 docs |

### With GPU (16GB RAM + CUDA)

| Metric | Value |
|--------|-------|
| Indexing Speed | ~50-100 docs/min |
| Query Response Time | 1-3 seconds |
| Concurrent Users | 10-50 |
| Document Limit | ~100,000 docs |

## 🚢 Deployment Options

### 1. Local Development
```bash
docker-compose up -d
```

### 2. VPS (Ubuntu 22.04)
```bash
# SSH to VPS
ssh user@your-vps-ip

# Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose

# Deploy
git clone <repo-url>
cd openwebui
docker-compose up -d
```

### 3. Production with SSL
```bash
# Add Nginx reverse proxy
# Add SSL with Certbot
# See README.md for detailed instructions
```

## 🔐 Security Considerations

- **Local-First**: No external API calls by default
- **Network Isolation**: Docker network isolation
- **Environment Variables**: Sensitive data in .env (not committed)
- **Production**: Add authentication, HTTPS, rate limiting

## 🤝 Contributing

See `CONTRIBUTING.md` for:
- Code style guidelines
- Testing procedures
- Pull request process
- Bug reporting

## 📚 Documentation

| File | Purpose |
|------|---------|
| `README.md` | Setup and usage guide |
| `ARCHITECTURE.md` | Technical architecture |
| `CONTRIBUTING.md` | Contribution guide |
| `data/docs/README.md` | Document upload instructions |

## 🛠️ Tech Stack Details

### Backend
- **FastAPI**: Modern Python web framework
- **LlamaIndex**: RAG orchestration
- **Pydantic**: Data validation
- **Uvicorn**: ASGI server

### LLM & Embeddings
- **Ollama**: Local LLM runtime
- **Llama3**: Default language model
- Alternative models: Mistral, CodeLlama, Neural-Chat

### Vector Database
- **Qdrant**: High-performance vector search
- Supports: Filtering, metadata, collections

### Document Processing
- **PyPDF**: PDF parsing
- **python-docx**: DOCX parsing
- **BeautifulSoup4**: HTML parsing

### Database (Optional)
- **SQLAlchemy**: SQL toolkit
- **psycopg2**: PostgreSQL adapter
- **PyMySQL**: MySQL adapter

## 📝 License

MIT License - free for personal and commercial use.

## 🙏 Acknowledgments

Built with open-source tools:
- [Ollama](https://ollama.ai/)
- [LlamaIndex](https://www.llamaindex.ai/)
- [Qdrant](https://qdrant.tech/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Open WebUI](https://github.com/open-webui/open-webui)

## 📞 Support

- Documentation: See README.md
- Issues: GitHub Issues
- Architecture: See ARCHITECTURE.md
- Contributing: See CONTRIBUTING.md

---

**Built with ❤️ for the open-source community**
