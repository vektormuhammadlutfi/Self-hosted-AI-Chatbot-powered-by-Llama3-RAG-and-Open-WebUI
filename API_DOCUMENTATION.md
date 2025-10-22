# 🎨 API Documentation Guide

## Beautiful API Docs with Scalar

Your RAG Chatbot API now features modern, interactive documentation powered by Scalar!

## 📍 Access Documentation

### Scalar API Reference (Recommended)
**URL:** http://localhost:8000/docs

**Features:**
- ✨ Modern, clean purple theme
- 🎯 Interactive "Try it out" functionality
- 📱 Mobile-responsive design
- 🔍 Built-in search
- 💻 Code examples in multiple languages
- 📊 Request/response visualizations
- 🎨 Syntax highlighting
- 📖 Comprehensive endpoint documentation

### ReDoc (Alternative)
**URL:** http://localhost:8000/redoc

Clean, three-panel documentation interface.

### OpenAPI Specification
**URL:** http://localhost:8000/openapi.json

Raw OpenAPI 3.0 specification in JSON format.

## 🚀 Using the API Documentation

### 1. Explore Endpoints

Navigate through the left sidebar to see all available endpoints:
- **General**: Root, Health Check
- **Q&A**: Ask questions endpoint
- **Statistics**: Get collection stats

### 2. Try Out Endpoints

Each endpoint has a "Try it" button:

1. Click on any endpoint (e.g., `POST /ask`)
2. Fill in the request body:
   ```json
   {
     "question": "What is this document about?",
     "max_sources": 3
   }
   ```
3. Click **"Send Request"**
4. View the response in real-time!

### 3. View Examples

Each endpoint includes:
- 📝 Detailed description
- 📥 Request schema with field descriptions
- 📤 Response schema with examples
- ⚠️ Possible error responses
- 💡 Usage examples

### 4. Code Generation

Scalar automatically generates code examples in:
- cURL
- JavaScript (fetch)
- Python (requests)
- Node.js
- PHP
- And more!

## 📚 API Endpoints Overview

### POST /ask
**Purpose:** Ask questions about your documents

**Key Features:**
- Context-aware AI responses
- Source document references
- Relevance scoring
- Configurable source count

**Example Use Cases:**
- "What are the system requirements?"
- "Explain the installation process"
- "What are the main features?"

### GET /health
**Purpose:** Service health monitoring

**Returns:**
- Service status
- RAG engine status
- Current timestamp

**Use Cases:**
- Monitoring scripts
- Load balancer health checks
- Service availability verification

### GET /stats
**Purpose:** Document collection statistics

**Returns:**
- Number of indexed vectors
- Total queries processed
- Collection health status
- Collection name

**Use Cases:**
- Monitoring index size
- Tracking API usage
- Verifying document indexing

### GET /
**Purpose:** API information

**Returns:**
- Service name and version
- Available endpoints
- Documentation links

## 🔧 Advanced Features

### Authentication (Coming Soon)
Currently, the API is open. For production:
- Add API key authentication
- Implement rate limiting
- Use HTTPS/TLS

### Filtering & Pagination
Future enhancements:
- Filter sources by metadata
- Paginate large result sets
- Advanced search options

### Batch Processing
Planned features:
- Batch question processing
- Bulk document indexing API
- Async processing endpoints

## 💻 Code Examples

### cURL
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the key features?",
    "max_sources": 3
  }'
```

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/ask",
    json={
        "question": "What are the key features?",
        "max_sources": 3
    }
)

data = response.json()
print(f"Answer: {data['answer']}")
print(f"Sources: {len(data['sources'])}")
```

### JavaScript (fetch)
```javascript
const response = await fetch('http://localhost:8000/ask', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'What are the key features?',
    max_sources: 3
  })
});

const data = await response.json();
console.log('Answer:', data.answer);
console.log('Query time:', data.query_time, 'seconds');
```

### Node.js (axios)
```javascript
const axios = require('axios');

async function askQuestion(question) {
  try {
    const response = await axios.post('http://localhost:8000/ask', {
      question: question,
      max_sources: 3
    });
    
    console.log('Answer:', response.data.answer);
    console.log('Sources:', response.data.sources.length);
    return response.data;
  } catch (error) {
    console.error('Error:', error.message);
  }
}

askQuestion('What are the key features?');
```

## 🎯 Best Practices

### 1. Error Handling
Always handle potential errors:
```python
try:
    response = requests.post(url, json=data, timeout=30)
    response.raise_for_status()  # Raise exception for 4xx/5xx
    return response.json()
except requests.exceptions.Timeout:
    print("Request timed out")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

### 2. Timeouts
Set reasonable timeouts:
```python
response = requests.post(url, json=data, timeout=30)
```

### 3. Retry Logic
Implement exponential backoff for retries:
```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.3)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
```

### 4. Connection Pooling
Reuse sessions for better performance:
```python
session = requests.Session()
# Make multiple requests with the same session
response1 = session.post(url, json=data1)
response2 = session.post(url, json=data2)
```

## 🔍 Troubleshooting

### API Not Responding
```bash
# Check if service is running
docker ps | grep backend

# Check logs
docker logs ai-chatbot-powered-by-llama3-rag-and-open-webui-backend-1

# Restart backend
docker-compose restart backend
```

### Slow Responses
- Check document index size (`/stats`)
- Reduce `max_sources` parameter
- Optimize question phrasing
- Consider using smaller LLM models

### Connection Refused
```bash
# Verify port is accessible
curl http://localhost:8000/health

# Check firewall settings
# Check Docker port mapping
docker port ai-chatbot-powered-by-llama3-rag-and-open-webui-backend-1
```

## 📖 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Scalar Documentation**: https://github.com/scalar/scalar
- **OpenAPI Specification**: https://swagger.io/specification/
- **HTTP Status Codes**: https://httpstatuses.com/

## 🎨 Customizing Documentation

To customize the Scalar theme, edit `backend/main.py`:

```python
data-configuration='{
    "theme": "purple",          # Options: purple, blue, green, orange
    "layout": "modern",         # Options: modern, classic
    "showSidebar": true,
    "darkMode": false,
    "searchHotKey": "k"
}'
```

Available themes:
- `purple` (default) - Modern purple theme
- `blue` - Professional blue theme
- `green` - Fresh green theme
- `orange` - Warm orange theme
- `alternate` - High contrast theme

---

**Enjoy your beautiful API documentation! 🚀**

For questions or issues, check the main README.md or project documentation.
