# 🤖 Model Management & BPS Integration Guide

## Overview

Your RAG Chatbot API now supports:
- ✅ Multiple AI model providers (Ollama, OpenRouter, Gemini)
- ✅ Dynamic model switching
- ✅ BPS (Indonesian Statistics) API integration
- ✅ Real-time model selection via API

## 🎯 Model Management

### List Available Models

**Endpoint:** `GET /models`

Get all available AI models from different providers.

**Example:**
```bash
curl http://localhost:8000/models
```

**Response:**
```json
{
  "current_model": "llama3",
  "available_models": [
    {
      "id": "llama3",
      "name": "Llama 3 (Local)",
      "provider": "ollama",
      "description": "Local Ollama model"
    },
    {
      "id": "openai/gpt-4-turbo",
      "name": "GPT-4 Turbo (OpenRouter)",
      "provider": "openrouter",
      "description": "Via OpenRouter API",
      "context_length": 128000
    },
    {
      "id": "anthropic/claude-3-opus",
      "name": "Claude 3 Opus (OpenRouter)",
      "provider": "openrouter",
      "description": "Via OpenRouter API",
      "context_length": 200000
    },
    {
      "id": "gemini-1.5-pro",
      "name": "Gemini 1.5 Pro (Google)",
      "provider": "gemini",
      "description": "Google Gemini model",
      "context_length": 1000000
    }
  ]
}
```

### Switch Model

**Endpoint:** `POST /models/select`

Switch to a different AI model.

**Request:**
```json
{
  "model_id": "openai/gpt-4"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Switched to model: openai/gpt-4",
  "current_model": {
    "provider": "openrouter",
    "model_name": "openai/gpt-4",
    "display_name": "openai/gpt-4"
  }
}
```

**Examples:**

```bash
# Switch to GPT-4
curl -X POST "http://localhost:8000/models/select" \
  -H "Content-Type: application/json" \
  -d '{"model_id": "openai/gpt-4"}'

# Switch to Claude 3 Opus
curl -X POST "http://localhost:8000/models/select" \
  -H "Content-Type: application/json" \
  -d '{"model_id": "anthropic/claude-3-opus"}'

# Switch to Gemini Pro
curl -X POST "http://localhost:8000/models/select" \
  -H "Content-Type: application/json" \
  -d '{"model_id": "gemini-pro"}'

# Switch back to local Llama3
curl -X POST "http://localhost:8000/models/select" \
  -H "Content-Type: application/json" \
  -d '{"model_id": "llama3"}'
```

### Use Specific Model in Query

You can also specify a model per-request:

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain quantum computing",
    "model": "openai/gpt-4",
    "max_sources": 3
  }'
```

## 📊 Available Models

### Ollama (Local Models)
- ✅ **Free** - No API costs
- ✅ **Private** - Data stays local
- ✅ **Fast** - No network latency
- ⚠️ Requires GPU for best performance

**Models:**
- `llama3` - Meta's Llama 3 (recommended)
- `mistral` - Mistral AI model
- `codellama` - Code-specialized model

### OpenRouter Models
- ✅ Access to **best commercial models**
- ✅ **Pay-per-use** - No subscriptions
- ✅ **Multiple providers** in one API
- 💰 Requires credits

**Popular Models:**
- `openai/gpt-4-turbo` - Most capable, best reasoning
- `openai/gpt-4` - Powerful, reliable
- `openai/gpt-3.5-turbo` - Fast, cost-effective
- `anthropic/claude-3-opus` - Excellent for analysis
- `anthropic/claude-3-sonnet` - Balanced performance
- `anthropic/claude-3-haiku` - Fast responses
- `meta-llama/llama-3-70b-instruct` - Powerful open model
- `google/gemini-pro` - Google's multimodal AI

### Google Gemini Models
- ✅ **Free tier available**
- ✅ **Long context** (up to 1M tokens)
- ✅ **Multimodal** capabilities
- 📱 Direct Google integration

**Models:**
- `gemini-pro` - Standard model
- `gemini-1.5-pro` - Enhanced with 1M context
- `gemini-1.5-flash` - Fast, efficient

## 🏛️ BPS API Integration

Access Indonesian statistical data from Badan Pusat Statistik (BPS).

### Get BPS Info

**Endpoint:** `GET /bps/info`

```bash
curl http://localhost:8000/bps/info
```

**Returns:**
- Setup instructions
- Available endpoints
- Example domain codes
- Documentation links

### Query BPS Data

**Endpoint:** `POST /bps/query`

**Example Requests:**

```bash
# Get all domains (provinces/regencies)
curl -X POST "http://localhost:8000/bps/query" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "domains",
    "params": {"type": "all"}
  }'

# Get news for Pinrang (domain 7315)
curl -X POST "http://localhost:8000/bps/query" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "news",
    "domain": "7315",
    "params": {"year": "2022", "lang": "ind"}
  }'

# Get publications
curl -X POST "http://localhost:8000/bps/query" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "publications",
    "domain": "7315",
    "params": {"year": "2023"}
  }'

# Get strategic indicators
curl -X POST "http://localhost:8000/bps/query" \
  -H "Content-Type: application/json" \
  -d '{
    "endpoint": "indicators",
    "domain": "7315"
  }'
```

### BPS Domain Codes

**Common Domains:**
- `73` - Sulawesi Selatan (Province)
- `7315` - Kabupaten Pinrang
- `7371` - Kota Makassar
- `31` - DKI Jakarta
- `32` - Jawa Barat
- `35` - Jawa Timur

### BPS Endpoints

1. **domains** - List provinces/regencies
2. **subcat** - Subject categories
3. **subjects** - Subjects by category
4. **variables** - Variables by subject
5. **data** - Statistical data
6. **news** - BPS news articles
7. **publications** - Publications
8. **pressrelease** - Press releases
9. **indicators** - Strategic indicators

## 💻 Code Examples

### Python - List Models

```python
import requests

response = requests.get("http://localhost:8000/models")
data = response.json()

print(f"Current model: {data['current_model']}")
print(f"\nAvailable models ({len(data['available_models'])}):")
for model in data['available_models']:
    print(f"  • {model['name']} ({model['provider']})")
```

### Python - Switch Model

```python
import requests

# Switch to GPT-4
response = requests.post(
    "http://localhost:8000/models/select",
    json={"model_id": "openai/gpt-4"}
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Message: {result['message']}")
```

### Python - Query BPS

```python
import requests

# Get Pinrang news
response = requests.post(
    "http://localhost:8000/bps/query",
    json={
        "endpoint": "news",
        "domain": "7315",
        "params": {"year": "2022", "lang": "ind"}
    }
)

data = response.json()
print(f"Endpoint: {data['endpoint']}")
print(f"Query time: {data['query_time']}s")
print(f"Data: {data['data']}")
```

### JavaScript - List and Select Model

```javascript
// List models
const modelsResponse = await fetch('http://localhost:8000/models');
const models = await modelsResponse.json();

console.log('Available models:', models.available_models.length);

// Switch to Claude 3 Opus
const selectResponse = await fetch('http://localhost:8000/models/select', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({model_id: 'anthropic/claude-3-opus'})
});

const result = await selectResponse.json();
console.log('Switched to:', result.current_model.model_name);
```

## 🔧 Integration with Open WebUI

### Model Selection in Chat

The selected model via API affects all subsequent queries. You can:

1. **Via API** - Use `/models/select` endpoint
2. **Via Chat** - Use Open WebUI's model selector
3. **Per Query** - Specify model in each `/ask` request

### BPS Function in Open WebUI

For full BPS integration:

1. Open Open WebUI at http://localhost:3000
2. Go to **Workspace** → **Functions**
3. Install the **BPS API Integration** function
4. Configure your BPS API key
5. Use in chat: "Get Pinrang news for 2022"

The function provides:
- ✅ SSL certificate handling
- ✅ Automatic parameter formatting
- ✅ Error handling
- ✅ Result formatting
- ✅ Multiple endpoint support

## 📊 Model Comparison

| Model | Provider | Cost | Speed | Quality | Context | Use Case |
|-------|----------|------|-------|---------|---------|----------|
| Llama 3 | Ollama | Free | Fast | Good | 8K | Local, private |
| GPT-4 Turbo | OpenRouter | $$$ | Medium | Excellent | 128K | Complex tasks |
| GPT-3.5 Turbo | OpenRouter | $ | Fast | Good | 16K | Quick queries |
| Claude 3 Opus | OpenRouter | $$$ | Medium | Excellent | 200K | Analysis, reasoning |
| Claude 3 Haiku | OpenRouter | $ | Very Fast | Good | 200K | Speed priority |
| Gemini 1.5 Pro | Google | $$ | Medium | Excellent | 1M | Long documents |
| Gemini Flash | Google | $ | Fast | Good | 1M | Fast, efficient |

**Cost Legend:**
- `Free` - No cost
- `$` - < $0.001 per 1K tokens
- `$$` - $0.001-0.01 per 1K tokens
- `$$$` - > $0.01 per 1K tokens

## 🎯 Best Practices

### Model Selection Strategy

1. **Start Local** - Use Llama 3 for testing
2. **Scale Up** - Switch to GPT-3.5 for production
3. **Complex Tasks** - Use GPT-4 or Claude Opus
4. **Long Documents** - Use Gemini 1.5 Pro (1M context)
5. **Speed Priority** - Use Claude Haiku or Gemini Flash

### Cost Optimization

1. **Use local models** for development
2. **Cache responses** for repeated queries
3. **Use cheaper models** for simple tasks
4. **Monitor usage** via OpenRouter dashboard
5. **Set budget limits** in OpenRouter

### BPS Integration Tips

1. **Cache BPS responses** - Data doesn't change often
2. **Use domain codes** - More reliable than names
3. **Check year availability** - Not all years have data
4. **Handle SSL errors** - Use the Open WebUI function
5. **Respect rate limits** - BPS API has quotas

## 📚 Additional Resources

- **OpenRouter Dashboard**: https://openrouter.ai/activity
- **Gemini API Console**: https://aistudio.google.com
- **BPS API Docs**: https://webapi.bps.go.id/documentation
- **Ollama Models**: https://ollama.ai/library

## 🐛 Troubleshooting

### Model Not Available
```bash
# Check Ollama is running
docker logs ai-chatbot-powered-by-llama3-rag-and-open-webui-ollama-1

# Pull model if missing
docker exec ai-chatbot-powered-by-llama3-rag-and-open-webui-ollama-1 ollama pull llama3
```

### OpenRouter/Gemini Not Working
- Verify API keys in Open WebUI (Admin Panel → Connections)
- Check credits/quota in provider dashboard
- Review API key permissions

### BPS Query Fails
- Install BPS function in Open WebUI
- Configure BPS API key in function settings
- Check domain code is valid
- Verify internet connectivity

---

**Enjoy multi-model AI and Indonesian statistics integration! 🚀📊**
