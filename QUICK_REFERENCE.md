# Quick Reference Guide

## 🚀 One-Command Setups

### Linux/macOS
```bash
chmod +x start.sh && ./start.sh
```

### Windows PowerShell
```powershell
.\start.ps1
```

### Manual Setup
```bash
# 1. Start services
docker-compose up -d

# 2. Pull model (first time only)
docker exec openwebui-ollama-1 ollama pull llama3

# 3. Add documents to data/docs/

# 4. Index documents
docker exec openwebui-backend-1 python loader.py

# 5. Open browser
# http://localhost:3000  (Open WebUI)
# http://localhost:8000  (Backend API)
```

## 📋 Common Commands

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a service
docker-compose restart backend

# View logs
docker-compose logs -f
docker-compose logs -f backend
```

### Document Management
```bash
# Add documents
cp /path/to/file.pdf ./data/docs/

# Index documents
docker exec openwebui-backend-1 python loader.py

# Check collection stats
curl http://localhost:8000/stats
```

### Ollama Management
```bash
# List models
docker exec openwebui-ollama-1 ollama list

# Pull a model
docker exec openwebui-ollama-1 ollama pull llama3

# Pull alternative models
docker exec openwebui-ollama-1 ollama pull mistral
docker exec openwebui-ollama-1 ollama pull codellama
```

### Database Loader (Optional)
```bash
# Edit backend/.env with DB credentials
nano backend/.env

# Run database loader
docker exec openwebui-backend-1 python db_loader.py
```

### Testing
```bash
# Health check
curl http://localhost:8000/health

# Ask a question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this about?"}'

# Run test script
python test_api.py
```

### Troubleshooting
```bash
# Check service status
docker-compose ps

# View all logs
docker-compose logs -f

# Restart everything
docker-compose down && docker-compose up -d

# Clear vector database
docker-compose down
docker volume rm openwebui_qdrant_storage
docker-compose up -d
```

## 🔧 Configuration Quick Edit

### Change LLM Model
```bash
# Edit backend/.env
OLLAMA_MODEL=mistral  # or llama3, codellama, etc.

# Pull the model
docker exec openwebui-ollama-1 ollama pull mistral

# Restart backend
docker-compose restart backend
```

### Change Chunk Size
```bash
# Edit backend/.env
CHUNK_SIZE=256        # Smaller chunks (faster, less context)
CHUNK_SIZE=1024       # Larger chunks (slower, more context)

# Re-index documents
docker exec openwebui-backend-1 python loader.py
```

### Change Collection Name
```bash
# Edit backend/.env
QDRANT_COLLECTION=my_custom_collection

# Restart and re-index
docker-compose restart backend
docker exec openwebui-backend-1 python loader.py
```

## 🌐 Access URLs

| Service | Local URL | VPS URL (replace IP) |
|---------|-----------|----------------------|
| Open WebUI | http://localhost:3000 | http://YOUR-VPS-IP:3000 |
| Backend API | http://localhost:8000 | http://YOUR-VPS-IP:8000 |
| API Docs | http://localhost:8000/docs | http://YOUR-VPS-IP:8000/docs |
| Qdrant | http://localhost:6333/dashboard | http://YOUR-VPS-IP:6333/dashboard |

## 📊 File Locations

### Documents
```
./data/docs/          # Your documents (PDF, TXT, DOCX)
```

### Configuration
```
./backend/.env        # Main configuration
./docker-compose.yml  # Service definitions
```

### Logs
```bash
docker-compose logs backend  # Backend logs
docker-compose logs ollama   # Ollama logs
docker-compose logs qdrant   # Qdrant logs
```

## 🎯 Performance Tips

### For Better Speed
1. Use GPU if available (requires nvidia-docker)
2. Use smaller models (mistral instead of llama3)
3. Reduce chunk_size in .env
4. Increase RAM allocation to Docker

### For Better Quality
1. Use larger models (llama3:70b if you have resources)
2. Increase chunk_size in .env
3. Adjust similarity_top_k in engine.py
4. Use more specific queries

## 🔒 Security Checklist (Production)

- [ ] Change WEBUI_SECRET_KEY in docker-compose.yml
- [ ] Add authentication to Open WebUI
- [ ] Set up HTTPS with reverse proxy (Nginx/Caddy)
- [ ] Configure firewall (UFW)
- [ ] Restrict CORS origins in main.py
- [ ] Use strong passwords for any databases
- [ ] Regular backups of Qdrant data
- [ ] Keep Docker images updated

## 📱 Mobile Access

### Local Network
```
# Find your local IP
ip addr show  # Linux
ipconfig      # Windows

# Access from phone/tablet on same network
http://192.168.x.x:3000
```

### VPS/Internet
```
# Use your VPS IP or domain
http://your-vps-ip:3000
https://chatbot.yourdomain.com  # With SSL
```

## 💾 Backup & Restore

### Backup Vector Database
```bash
# Stop services
docker-compose down

# Backup Qdrant volume
docker run --rm -v openwebui_qdrant_storage:/data \
  -v $(pwd)/backup:/backup \
  alpine tar czf /backup/qdrant-backup.tar.gz /data

# Restart services
docker-compose up -d
```

### Restore Vector Database
```bash
# Stop services
docker-compose down

# Remove old volume
docker volume rm openwebui_qdrant_storage

# Create new volume
docker volume create openwebui_qdrant_storage

# Restore data
docker run --rm -v openwebui_qdrant_storage:/data \
  -v $(pwd)/backup:/backup \
  alpine tar xzf /backup/qdrant-backup.tar.gz -C /

# Restart services
docker-compose up -d
```

## 🎓 Learning Resources

### Official Documentation
- [Ollama Docs](https://github.com/ollama/ollama/blob/main/docs)
- [LlamaIndex Docs](https://docs.llamaindex.ai/)
- [Qdrant Docs](https://qdrant.tech/documentation/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

### Alternative Models to Try
```bash
# Faster, smaller
docker exec openwebui-ollama-1 ollama pull mistral

# Code-focused
docker exec openwebui-ollama-1 ollama pull codellama

# Conversation-optimized
docker exec openwebui-ollama-1 ollama pull neural-chat
```

## 🐛 Common Issues & Solutions

### "Connection refused" when starting
- Wait 30-60 seconds for services to fully start
- Check logs: `docker-compose logs -f`

### "Model not found"
- Pull the model: `docker exec openwebui-ollama-1 ollama pull llama3`

### Slow responses
- Use a smaller model (mistral)
- Reduce chunk_size
- Check CPU/RAM usage

### Out of memory
- Increase Docker memory limit
- Use a smaller model
- Process fewer documents at once

### Documents not indexing
- Check file format (PDF, TXT, DOCX only)
- Check file permissions
- View loader logs: `docker-compose logs backend`

---

**Quick Start: `./start.sh` (Linux/Mac) or `.\start.ps1` (Windows)**
