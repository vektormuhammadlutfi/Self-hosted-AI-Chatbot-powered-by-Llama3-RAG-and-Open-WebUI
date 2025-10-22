# API Keys Setup Guide

This guide explains how to configure OpenRouter and Google Gemini API keys for your RAG Chatbot.

## 🔑 Supported AI Providers

Your chatbot supports multiple AI providers:
- **Ollama (Local)** - Default, runs locally with Llama3
- **OpenRouter** - Access to multiple AI models (GPT-4, Claude, etc.)
- **Google Gemini** - Google's AI models

## ⚠️ Important Note

**OpenRouter and Gemini API keys are configured through the Open WebUI interface**, not through environment variables or docker-compose.yml.

See `OPENROUTER_SETUP.md` for detailed step-by-step instructions.

## 📝 Quick Setup

### 1. OpenRouter API Key

**Get Your API Key:**
1. Visit https://openrouter.ai/
2. Sign up or login
3. Go to https://openrouter.ai/keys
4. Create a new API key
5. Copy the key

**Configure:**
Edit `backend/.env` and add:
```bash
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxx
```

**Available Models (examples):**
- `openai/gpt-4-turbo`
- `openai/gpt-3.5-turbo`
- `anthropic/claude-3-opus`
- `anthropic/claude-3-sonnet`
- `meta-llama/llama-3-70b-instruct`
- And many more at https://openrouter.ai/models

### 2. Google Gemini API Key

**Get Your API Key:**
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

**Configure:**
Edit `backend/.env` and add:
```bash
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Available Models:**
- `gemini-pro`
- `gemini-pro-vision`
- `gemini-1.5-pro`
- `gemini-1.5-flash`

## 🚀 How to Use in Open WebUI

### Configure via Web Interface (RECOMMENDED)

1. Open http://localhost:3000
2. Go to **Admin Panel** → **Connections**
3. Add OpenRouter connection:
   - API Base URL: `https://openrouter.ai/api/v1`
   - API Key: Your OpenRouter key
4. Add Gemini connection:
   - API Base URL: `https://generativelanguage.googleapis.com/v1beta/openai`
   - API Key: Your Google API key
5. Save and refresh - models will appear in model selector

**For detailed step-by-step instructions with screenshots, see:** `OPENROUTER_SETUP.md`

## 📚 Environment Variables (Backend Only)

```bash
# Stop services
docker-compose down

# Start services
docker-compose up -d

# Or just restart Open WebUI
docker-compose restart openwebui
```

## 💰 Pricing Information

### OpenRouter
- Pay-per-use pricing
- Varies by model
- Check https://openrouter.ai/models for pricing
- Add credits at https://openrouter.ai/credits

### Google Gemini
- Free tier available
- Gemini Pro: 60 requests per minute (free)
- Check https://ai.google.dev/pricing for details

## 🔒 Security Notes

1. **Never commit `.env` to git** - It contains sensitive API keys
2. The `.env` file is already in `.gitignore`
3. Share `.env.example` instead, which has placeholder values
4. For production, use Docker secrets or environment variable injection

## 🧪 Testing

Test if your API keys work:

1. **OpenRouter:**
   ```bash
   curl https://openrouter.ai/api/v1/models \
     -H "Authorization: Bearer YOUR_OPENROUTER_KEY"
   ```

2. **Gemini:**
   ```bash
   curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_GOOGLE_KEY"
   ```

## 📚 Additional Resources

- OpenRouter Docs: https://openrouter.ai/docs
- Gemini API Docs: https://ai.google.dev/docs
- Open WebUI Docs: https://docs.openwebui.com/

## ❓ Troubleshooting

**API Key not working:**
1. Check if the key is correctly copied (no extra spaces)
2. Verify the key is active in the provider's dashboard
3. Check if you have credits/quota remaining
4. Restart the container after changing `.env`

**Models not showing up:**
1. Restart Open WebUI: `docker-compose restart openwebui`
2. Clear browser cache
3. Check browser console for errors (F12)

**SSL Certificate errors:**
1. Add to docker-compose.yml under openwebui environment:
   ```yaml
   - REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
   ```
2. Or disable SSL verification (not recommended for production)
