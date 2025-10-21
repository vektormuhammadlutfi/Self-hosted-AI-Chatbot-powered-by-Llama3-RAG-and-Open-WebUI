# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │                    Open WebUI (Port 3000)                  │ │
│  │           Modern chat interface for user interaction       │ │
│  └───────────────────────────────────────────────────────────┘ │
└───────────────────────────────┬─────────────────────────────────┘
                                │ HTTP/WebSocket
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend Services                           │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              FastAPI Backend (Port 8000)                   │ │
│  │                                                            │ │
│  │  Endpoints:                                                │ │
│  │  • POST /ask        - Query documents                      │ │
│  │  • GET  /health     - Health check                         │ │
│  │  • GET  /stats      - Collection statistics                │ │
│  │                                                            │ │
│  │  Components:                                               │ │
│  │  • main.py          - FastAPI application                  │ │
│  │  • engine.py        - RAG engine (LlamaIndex orchestration)│ │
│  │  • loader.py        - Document indexing script             │ │
│  │  • db_loader.py     - Database indexing script             │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│         ┌─────────────────────┬─────────────────────┐         │
│         ▼                     ▼                     ▼         │
│  ┌─────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Ollama    │      │   Qdrant     │      │  PostgreSQL  │ │
│  │ (Port 11434)│      │ (Port 6333)  │      │  (Optional)  │ │
│  │             │      │              │      │              │ │
│  │ LLM Runtime │      │   Vector DB  │      │   Relational │ │
│  │ - Llama3    │      │ - Embeddings │      │   Database   │ │
│  │ - Embedding │      │ - Similarity │      │              │ │
│  │ - Generation│      │   Search     │      │              │ │
│  └─────────────┘      └──────────────┘      └──────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Document Indexing Flow

```
Documents (PDF/TXT/DOCX)
         │
         ▼
   loader.py reads files
         │
         ▼
   LlamaIndex chunks documents
         │
         ▼
   Ollama creates embeddings
         │
         ▼
   Store in Qdrant vector DB
```

### 2. Query Flow

```
User Question
     │
     ▼
FastAPI /ask endpoint
     │
     ▼
RAGEngine.query()
     │
     ├─────────────────────┐
     ▼                     ▼
Qdrant similarity      Retrieve top-k
   search             document chunks
     │                     │
     └──────────┬──────────┘
                ▼
         Combine context
                │
                ▼
         Ollama LLM
                │
                ▼
      Generated answer
                │
                ▼
      Return to user
```

## Component Responsibilities

### FastAPI Backend (`main.py`)
- REST API endpoints
- Request validation
- Response formatting
- CORS configuration
- Health checks

### RAG Engine (`engine.py`)
- LlamaIndex configuration
- Ollama LLM integration
- Qdrant vector store connection
- Query orchestration
- Index management

### Document Loader (`loader.py`)
- File system scanning
- Document parsing (PDF/TXT/DOCX)
- Text chunking
- Embedding generation
- Vector storage

### Database Loader (`db_loader.py`)
- SQL database connection
- Data extraction
- Row-to-document conversion
- Embedding generation
- Vector storage

### Ollama
- Local LLM hosting
- Text generation
- Embedding creation
- Model management

### Qdrant
- Vector storage
- Similarity search
- Collection management
- Metadata filtering

### Open WebUI
- User interface
- Chat history
- Ollama integration
- User authentication (optional)

## Technology Stack Details

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Open WebUI | Modern chat interface |
| API | FastAPI | High-performance Python web framework |
| RAG Framework | LlamaIndex | Document indexing and retrieval orchestration |
| LLM | Ollama + Llama3 | Local language model inference |
| Vector DB | Qdrant | Semantic search and vector storage |
| Database (optional) | PostgreSQL/MySQL | Structured data source |
| Containerization | Docker Compose | Service orchestration |

## Deployment Architecture

### Local Development
```
localhost:3000  → Open WebUI
localhost:8000  → FastAPI Backend
localhost:11434 → Ollama
localhost:6333  → Qdrant
```

### VPS Production
```
https://chat.domain.com  → Nginx → Open WebUI
https://api.domain.com   → Nginx → FastAPI
(Internal) Ollama
(Internal) Qdrant
```

## Scalability Considerations

### Current Setup (Single Server)
- Suitable for: 1-100 concurrent users
- Document limit: ~100k documents
- Response time: 2-10 seconds

### Horizontal Scaling (Future)
- Multiple FastAPI instances behind load balancer
- Qdrant cluster for distributed vector search
- Separate Ollama instances for LLM serving
- Redis for caching frequent queries

## Security Considerations

### Current Implementation
- Local-first (no external API calls)
- Docker network isolation
- Environment-based configuration

### Production Recommendations
- Add authentication/authorization
- Use HTTPS with valid certificates
- Implement rate limiting
- Add input validation and sanitization
- Enable CORS restrictions
- Regular security updates
- Backup vector database regularly

## Performance Optimization

### Current Optimizations
- Document chunking (512 tokens)
- Top-k retrieval (k=5)
- Embedding caching in Qdrant
- Docker volume persistence

### Advanced Optimizations
- GPU acceleration for Ollama
- Qdrant quantization
- Query result caching
- Batch document processing
- Async document loading
