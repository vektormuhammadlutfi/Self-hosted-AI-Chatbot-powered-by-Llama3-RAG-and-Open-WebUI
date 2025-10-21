# RAG Chatbot - Local-First AI Assistant

A self-hostable, open-source chatbot using **Retrieval-Augmented Generation (RAG)** powered by Ollama, LlamaIndex, Qdrant, and Open WebUI.

## 🎯 Features

- **Local-first**: Run entirely on your machine or VPS—no external API keys required
- **Document learning**: Upload PDFs, TXT, DOCX files and the chatbot learns from them
- **Database integration**: Optionally index content from PostgreSQL or MySQL tables
- **Modern stack**: FastAPI backend, Qdrant vector DB, Ollama for LLM inference
- **Production-ready**: Fully containerized with Docker Compose

## 🧱 Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM Runtime | Ollama (Llama3) |
| RAG Framework | LlamaIndex |
| Vector Database | Qdrant |
| Backend API | FastAPI |
| Frontend UI | Open WebUI |
| Database (optional) | PostgreSQL / MySQL |
| Containerization | Docker Compose |

## 📁 Project Structure

```
.
├── docker-compose.yml          # Main orchestration file
├── backend/
│   ├── Dockerfile             # Backend container definition
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Environment configuration
│   ├── .env.example          # Example configuration
│   ├── main.py               # FastAPI application
│   ├── engine.py             # RAG engine (LlamaIndex + Qdrant)
│   ├── loader.py             # Document indexing script
│   └── db_loader.py          # Database indexing script (optional)
├── data/
│   └── docs/                 # Place your documents here (PDF, TXT, DOCX)
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

- **Docker** and **Docker Compose** installed
- At least **8GB RAM** (16GB recommended for better performance)
- **Ubuntu 22.04** or similar Linux environment (also works on Windows/macOS)

### Installation Steps

#### 1. Clone or Copy This Project

```bash
# If you have the files, cd into the project directory
cd openwebui
```

#### 2. Configure Environment Variables

```bash
# Copy the example environment file
cp backend/.env.example backend/.env

# Edit if needed (defaults work for Docker Compose setup)
nano backend/.env
```

**Default configuration** (works out-of-the-box):
```env
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=documents
```

#### 3. Start All Services

```bash
# Start Qdrant, Ollama, Backend, and Open WebUI
docker-compose up -d
```

This will:
- Download and start **Qdrant** (vector database)
- Download and start **Ollama** (LLM runtime)
- Build and start the **FastAPI backend**
- Start **Open WebUI** (web interface)

#### 4. Pull the Llama3 Model (First Time Only)

```bash
# Access the Ollama container
docker exec -it openwebui-ollama-1 ollama pull llama3

# Verify the model is downloaded
docker exec -it openwebui-ollama-1 ollama list
```

> **Note**: This downloads ~4.7GB. Ensure you have sufficient disk space and bandwidth.

#### 5. Add Your Documents

```bash
# Place your documents in the data/docs folder
cp /path/to/your/document.pdf ./data/docs/
cp /path/to/your/notes.txt ./data/docs/
```

Supported formats: **PDF**, **TXT**, **DOCX**

#### 6. Index Your Documents

```bash
# Run the document loader inside the backend container
docker exec -it openwebui-backend-1 python loader.py
```

You should see output like:
```
INFO - Loading documents...
INFO - Loaded 15 document chunks
INFO - Creating embeddings and indexing documents...
INFO - ✓ Documents successfully indexed into Qdrant!
```

#### 7. Access the Services

| Service | URL | Purpose |
|---------|-----|---------|
| **Open WebUI** | http://localhost:3000 | Chat interface |
| **FastAPI Backend** | http://localhost:8000 | API endpoints |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Qdrant Dashboard** | http://localhost:6333/dashboard | Vector database UI |

### Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'

# Get collection statistics
curl http://localhost:8000/stats
```

## 🗄️ Database Integration (Optional)

If you want to index data from a PostgreSQL or MySQL database:

### 1. Configure Database Connection

Edit `backend/.env`:
```env
DB_TYPE=postgresql
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password
DB_TABLE=faq
```

### 2. Run the Database Loader

```bash
docker exec -it openwebui-backend-1 python db_loader.py
```

### 3. Customize for Your Schema

Edit `backend/db_loader.py` and modify the `main()` function:

```python
loader.load_from_table(
    text_columns=['question', 'answer'],  # Your column names
    filter_clause="status = 'active'"     # Optional WHERE clause
)
```

## 🌐 Deploying to VPS

### Option 1: Docker Compose on VPS

1. **SSH into your VPS**:
   ```bash
   ssh user@your-vps-ip
   ```

2. **Install Docker and Docker Compose**:
   ```bash
   # Update packages
   sudo apt update
   sudo apt install -y docker.io docker-compose git
   
   # Start Docker
   sudo systemctl start docker
   sudo systemctl enable docker
   
   # Add user to docker group
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Copy your project to VPS**:
   ```bash
   # Option A: Use git
   git clone https://github.com/your-repo/rag-chatbot.git
   cd rag-chatbot
   
   # Option B: Use scp from your local machine
   scp -r ./openwebui user@your-vps-ip:/home/user/
   ```

4. **Configure and start**:
   ```bash
   cp backend/.env.example backend/.env
   nano backend/.env  # Edit if needed
   
   docker-compose up -d
   docker exec -it openwebui-ollama-1 ollama pull llama3
   docker exec -it openwebui-backend-1 python loader.py
   ```

5. **Configure firewall** (if needed):
   ```bash
   sudo ufw allow 3000  # Open WebUI
   sudo ufw allow 8000  # Backend API
   ```

6. **Access via VPS IP**:
   - Open WebUI: `http://your-vps-ip:3000`
   - Backend API: `http://your-vps-ip:8000`

### Option 2: Using Reverse Proxy (Production)

For production deployment with SSL/domain names, use Nginx or Caddy:

**Example Nginx config** (`/etc/nginx/sites-available/chatbot`):
```nginx
server {
    listen 80;
    server_name chatbot.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Then use **Certbot** for SSL:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d chatbot.yourdomain.com
```

## 🛠️ Common Operations

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f ollama
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Stop Services

```bash
docker-compose down
```

### Update Documents

```bash
# Add more documents to data/docs/
cp new-file.pdf ./data/docs/

# Re-index (this adds to existing index)
docker exec -it openwebui-backend-1 python loader.py
```

### Clear Vector Database

```bash
# Stop services
docker-compose down

# Remove Qdrant volume
docker volume rm openwebui_qdrant_storage

# Restart and re-index
docker-compose up -d
docker exec -it openwebui-ollama-1 ollama pull llama3
docker exec -it openwebui-backend-1 python loader.py
```

## 🔧 Troubleshooting

### Ollama Model Not Found

```bash
# Pull the model manually
docker exec -it openwebui-ollama-1 ollama pull llama3

# List available models
docker exec -it openwebui-ollama-1 ollama list
```

### Backend Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issue: Qdrant not ready yet
# Solution: Wait 10-20 seconds and restart
docker-compose restart backend
```

### Out of Memory

If you see OOM errors:
- Increase Docker memory limit (Docker Desktop: Settings → Resources)
- Use a smaller model: `ollama pull llama3:8b` or `ollama pull mistral`
- Close other applications

### Slow Performance

- **GPU acceleration**: Install nvidia-docker for GPU support
- **Use smaller model**: Try `mistral` instead of `llama3`
- **Reduce chunk size**: Edit `backend/.env` and set `CHUNK_SIZE=256`

## 📚 API Reference

### POST `/ask`

Ask a question based on indexed documents.

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
  "sources": [
    {
      "text": "Document excerpt...",
      "score": 0.85,
      "metadata": {"filename": "guide.pdf"}
    }
  ]
}
```

### GET `/health`

Check if the service is ready.

**Response:**
```json
{
  "status": "healthy"
}
```

### GET `/stats`

Get vector database statistics.

**Response:**
```json
{
  "collection_name": "documents",
  "vectors_count": 150,
  "points_count": 150,
  "status": "green"
}
```

## 🤝 Contributing

This is an open-source project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🙏 Credits

Built with:
- [Ollama](https://ollama.ai/) - Local LLM runtime
- [LlamaIndex](https://www.llamaindex.ai/) - RAG framework
- [Qdrant](https://qdrant.tech/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Open WebUI](https://github.com/open-webui/open-webui) - Chat interface

## 📞 Support

For issues or questions:
- Check the [Troubleshooting](#-troubleshooting) section
- Review logs: `docker-compose logs -f`
- Open an issue on GitHub

---

**Happy chatting! 🚀**
