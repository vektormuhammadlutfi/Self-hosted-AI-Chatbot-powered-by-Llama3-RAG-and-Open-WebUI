# 🚀 Panduan Menambahkan OpenRouter & Gemini ke Open WebUI

## 📋 Langkah-langkah Konfigurasi

### 1️⃣ Akses Admin Panel

1. Buka http://localhost:3000
2. Login dengan akun admin Anda
3. Klik **ikon profil** di pojok kanan atas
4. Pilih **Admin Panel** atau **Settings**

### 2️⃣ Konfigurasi OpenRouter

#### A. Melalui Admin Panel → Connections

1. Di Admin Panel, pilih **Connections**
2. Scroll ke bagian **OpenAI API**
3. Klik **+ Add OpenAI API Connection** atau **Add Connection**

4. Masukkan detail berikut:
   ```
   Name: OpenRouter
   API Base URL: https://openrouter.ai/api/v1
   API Key: sk****************************************************
   ```

5. Klik **Save** atau **Verify Connection**

#### B. Alternatif: Melalui Settings → Connections

1. Klik **Settings** (ikon gear)
2. Pilih tab **Connections** atau **External Connections**
3. Cari bagian **OpenAI API**
4. Klik **+ Add**
5. Masukkan:
   ```
   Base URL: https://openrouter.ai/api/v1
   API Key: sk****************************************************
   ```

### 3️⃣ Konfigurasi Google Gemini

1. Di bagian yang sama (Connections)
2. Klik **+ Add OpenAI API Connection** (atau tombol serupa)
3. Masukkan detail:
   ```
   Name: Google Gemini
   API Base URL: https://generativelanguage.googleapis.com/v1beta/openai
   API Key: AI*************************************************
   ```
   
   **Catatan:** Untuk Gemini, gunakan endpoint OpenAI-compatible: `/v1beta/openai`

4. Klik **Save**

### 4️⃣ Refresh Models

Setelah menambahkan connections:

1. Kembali ke halaman chat
2. Klik **Model selector** (biasanya di atas kotak chat)
3. Klik tombol **Refresh** atau **⟳** untuk memuat ulang models
4. Atau tunggu beberapa detik, models akan muncul otomatis

### 5️⃣ Pilih Model

Di model selector, Anda seharusnya melihat:

**Dari OpenRouter:**
- `openai/gpt-4-turbo`
- `openai/gpt-4`
- `openai/gpt-3.5-turbo`
- `anthropic/claude-3-opus`
- `anthropic/claude-3-sonnet`
- `meta-llama/llama-3-70b-instruct`
- `google/gemini-pro`
- Dan banyak lagi...

**Dari Gemini:**
- `gemini-pro`
- `gemini-1.5-pro`
- `gemini-1.5-flash`

**Dari Ollama (Local):**
- `llama3`

## 🔧 Troubleshooting

### Model tidak muncul?

**1. Restart Open WebUI container:**
```bash
docker-compose restart openwebui
```

**2. Clear browser cache:**
- Tekan `Ctrl + Shift + Delete`
- Atau buka di Incognito/Private window

**3. Cek console browser:**
- Tekan `F12`
- Lihat tab **Console** untuk error messages
- Lihat tab **Network** untuk failed requests

**4. Verify API key di terminal:**

Test OpenRouter:
```bash
curl https://openrouter.ai/api/v1/models `
  -H "Authorization: Bearer sk****************************************************"
```

Test Gemini:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=AI*************************************************"
```

**5. Cek logs:**
```bash
docker logs ai-chatbot-powered-by-llama3-rag-and-open-webui-openwebui-1 --tail 100
```

### Error SSL Certificate?

Jika ada error SSL saat akses API external, tambahkan di `docker-compose.yml`:

```yaml
openwebui:
  environment:
    - REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
    - CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
    - SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
```

### Connection Timeout?

Jika koneksi timeout, coba:
1. Cek koneksi internet
2. Pastikan firewall tidak memblokir
3. Coba restart Docker Desktop

## 📱 Cara Menggunakan Model

### Di Chat:
1. Klik **model selector** di atas chat box
2. Pilih model yang diinginkan (contoh: `openai/gpt-4-turbo`)
3. Mulai chat!

### Switch Between Models:
- Anda bisa ganti model kapan saja di tengah conversation
- Setiap model punya karakteristik berbeda
- GPT-4: Lebih pintar, lebih mahal
- GPT-3.5: Cepat, lebih murah
- Claude: Bagus untuk reasoning dan analisis
- Llama3 (local): Gratis, privat, tapi butuh resource

## 💰 Monitoring Usage

### OpenRouter:
- Check usage di: https://openrouter.ai/activity
- Monitor credits: https://openrouter.ai/credits
- Set budget limits untuk avoid surprise charges

### Gemini:
- Check quota: https://aistudio.google.com/
- Free tier: 60 requests/minute
- Untuk production, consider paid tier

## 🎯 Best Practices

1. **Start dengan model murah** untuk testing (GPT-3.5, Gemini Flash)
2. **Use local Llama3** untuk data sensitif
3. **Set budget limits** di OpenRouter
4. **Monitor usage regularly**
5. **Don't share API keys** - mereka sudah di `.env` yang tidak di-commit ke git

## 📚 Model Recommendations

**Untuk coding:**
- `openai/gpt-4-turbo`
- `anthropic/claude-3-opus`

**Untuk chat umum:**
- `openai/gpt-3.5-turbo` (murah, cepat)
- `google/gemini-pro`

**Untuk privacy/local:**
- `llama3` (via Ollama)

**Untuk analisis data:**
- `anthropic/claude-3-sonnet`
- `openai/gpt-4`

**Untuk speed:**
- `gemini-1.5-flash`
- `openai/gpt-3.5-turbo`

## 🔐 Security Notes

- API keys disimpan di database Open WebUI (encrypted)
- Jangan expose port 3000 ke internet tanpa authentication
- Gunakan HTTPS jika deploy ke production
- Rotate API keys secara berkala

---

**Need help?** Check the logs atau tanya di chat! 🚀
