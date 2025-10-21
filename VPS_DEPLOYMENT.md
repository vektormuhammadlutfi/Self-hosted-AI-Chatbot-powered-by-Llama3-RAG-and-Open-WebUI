# VPS Deployment Checklist

Complete checklist for deploying RAG Chatbot to a VPS (Ubuntu 22.04).

## 📋 Pre-Deployment

### Local Testing
- [ ] Project works locally with `docker-compose up -d`
- [ ] Documents successfully indexed
- [ ] `/ask` endpoint returns good answers
- [ ] All services healthy
- [ ] No errors in logs

### VPS Requirements
- [ ] VPS with Ubuntu 22.04 (or similar)
- [ ] Minimum 8GB RAM (16GB recommended)
- [ ] 50GB+ disk space
- [ ] SSH access configured
- [ ] Sudo privileges

### Domain Setup (Optional but Recommended)
- [ ] Domain name registered
- [ ] DNS A record pointing to VPS IP
- [ ] DNS propagation complete (check: `nslookup yourdomain.com`)

## 🔧 Step 1: Initial VPS Setup

### Connect to VPS
```bash
ssh root@YOUR_VPS_IP
# or
ssh username@YOUR_VPS_IP
```

### Update System
```bash
sudo apt update
sudo apt upgrade -y
```

### Create Non-Root User (if needed)
```bash
sudo adduser chatbot
sudo usermod -aG sudo chatbot
sudo usermod -aG docker chatbot
su - chatbot
```

### Configure Firewall
```bash
# Install UFW
sudo apt install -y ufw

# Allow SSH (IMPORTANT: do this first!)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow application ports
sudo ufw allow 3000/tcp  # Open WebUI
sudo ufw allow 8000/tcp  # Backend API
sudo ufw allow 6333/tcp  # Qdrant (optional, for debugging)

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## 🐳 Step 2: Install Docker

### Install Docker
```bash
# Install dependencies
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
docker --version
```

### Install Docker Compose
```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

### Configure Docker User
```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group changes
newgrp docker

# Test (should work without sudo)
docker ps
```

## 📦 Step 3: Deploy Application

### Clone/Upload Project
```bash
# Option A: From Git
cd ~
git clone https://github.com/YOUR-USERNAME/rag-chatbot.git
cd rag-chatbot

# Option B: Upload via SCP (from local machine)
# scp -r ./openwebui username@YOUR_VPS_IP:/home/username/

# Navigate to project
cd ~/openwebui  # or wherever you uploaded
```

### Configure Environment
```bash
# Copy environment file
cp backend/.env.example backend/.env

# Edit configuration
nano backend/.env
```

**Update these values:**
```env
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3
QDRANT_HOST=qdrant
QDRANT_PORT=6333
QDRANT_COLLECTION=documents
```

### Start Services
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Pull LLM Model
```bash
# Pull Llama3 (this takes time and bandwidth)
docker exec openwebui-ollama-1 ollama pull llama3

# Verify
docker exec openwebui-ollama-1 ollama list
```

### Upload and Index Documents
```bash
# Option A: Upload via SCP (from local machine)
scp /path/to/documents/*.pdf username@YOUR_VPS_IP:~/openwebui/data/docs/

# Option B: Upload via SFTP
sftp username@YOUR_VPS_IP
cd openwebui/data/docs
put /local/path/file.pdf

# Index documents
docker exec openwebui-backend-1 python loader.py
```

### Test Access
```bash
# Test health endpoint
curl http://localhost:8000/health

# Test from local machine
curl http://YOUR_VPS_IP:8000/health
```

## 🌐 Step 4: Configure Reverse Proxy (Production)

### Install Nginx
```bash
sudo apt install -y nginx
```

### Configure Nginx for Open WebUI
```bash
# Create config file
sudo nano /etc/nginx/sites-available/chatbot
```

**Add this configuration:**
```nginx
# HTTP server block
server {
    listen 80;
    server_name chatbot.yourdomain.com;  # Change this

    # Redirect all HTTP to HTTPS (after SSL setup)
    # return 301 https://$server_name$request_uri;

    # Open WebUI
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        rewrite ^/api/(.*) /$1 break;
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Enable Site
```bash
# Create symlink
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

## 🔒 Step 5: Configure SSL with Let's Encrypt

### Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

### Obtain SSL Certificate
```bash
# Get certificate and auto-configure Nginx
sudo certbot --nginx -d chatbot.yourdomain.com

# Follow prompts:
# - Enter email address
# - Agree to terms
# - Choose redirect option (recommended: 2 - redirect HTTP to HTTPS)
```

### Test Auto-Renewal
```bash
# Dry run
sudo certbot renew --dry-run

# Check renewal timer
sudo systemctl status certbot.timer
```

### Update Nginx Config (if needed)
```bash
sudo nano /etc/nginx/sites-available/chatbot
```

Certbot should have added:
```nginx
server {
    listen 443 ssl;
    server_name chatbot.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/chatbot.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/chatbot.yourdomain.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # ... rest of configuration
}
```

## 🔐 Step 6: Security Hardening

### Update Docker Compose (Production Settings)
```bash
nano docker-compose.yml
```

**Update Open WebUI secret:**
```yaml
openwebui:
  # ... other settings
  environment:
    - OLLAMA_BASE_URL=http://ollama:11434
    - WEBUI_SECRET_KEY=YOUR_SECURE_RANDOM_KEY_HERE  # Change this!
```

Generate secret key:
```bash
openssl rand -hex 32
```

### Restrict CORS (Backend)
```bash
nano backend/main.py
```

Update:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chatbot.yourdomain.com"],  # Specific domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### Configure Fail2Ban (Optional)
```bash
# Install Fail2Ban
sudo apt install -y fail2ban

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Enable and start
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### Set Up Automated Backups
```bash
# Create backup script
nano ~/backup-qdrant.sh
```

**Add:**
```bash
#!/bin/bash
BACKUP_DIR=~/backups
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker run --rm \
  -v openwebui_qdrant_storage:/data \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/qdrant-$DATE.tar.gz /data

# Keep only last 7 backups
ls -t $BACKUP_DIR/qdrant-*.tar.gz | tail -n +8 | xargs rm -f

echo "Backup completed: qdrant-$DATE.tar.gz"
```

**Make executable and schedule:**
```bash
chmod +x ~/backup-qdrant.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add this line:
0 2 * * * /home/username/backup-qdrant.sh >> /home/username/backup.log 2>&1
```

## 📊 Step 7: Monitoring Setup

### Install Monitoring Tools
```bash
# Install htop for system monitoring
sudo apt install -y htop

# Check resources
htop
docker stats
```

### Set Up Log Rotation
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/docker-compose
```

**Add:**
```
/home/username/openwebui/*.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
}
```

### Check Service Health
```bash
# Create health check script
nano ~/check-health.sh
```

**Add:**
```bash
#!/bin/bash
curl -f http://localhost:8000/health || docker-compose restart backend
```

```bash
chmod +x ~/check-health.sh

# Run every 5 minutes
crontab -e
# Add:
*/5 * * * * /home/username/check-health.sh
```

## ✅ Post-Deployment Verification

### Check All Services
```bash
docker-compose ps
```

All should show "Up" status.

### Test Endpoints
```bash
# Health check
curl https://chatbot.yourdomain.com/api/health

# Stats
curl https://chatbot.yourdomain.com/api/stats
```

### Test Web Interface
```
https://chatbot.yourdomain.com
```

### Test Query
```bash
curl -X POST https://chatbot.yourdomain.com/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is RAG?"}'
```

## 🎉 Deployment Complete!

### Access Your Chatbot
- **Web Interface**: https://chatbot.yourdomain.com
- **API**: https://chatbot.yourdomain.com/api
- **API Docs**: https://chatbot.yourdomain.com/api/docs

### Maintenance Commands
```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Update application
git pull  # if using git
docker-compose down
docker-compose up -d --build

# Add more documents
scp file.pdf username@VPS_IP:~/openwebui/data/docs/
docker exec openwebui-backend-1 python loader.py
```

## 📞 Troubleshooting

### Services won't start
```bash
docker-compose logs -f
sudo systemctl status docker
```

### Can't access from internet
```bash
sudo ufw status  # Check firewall
sudo nginx -t    # Check Nginx config
curl localhost:3000  # Test locally first
```

### SSL issues
```bash
sudo certbot certificates
sudo nginx -t
sudo systemctl reload nginx
```

### Out of disk space
```bash
df -h  # Check disk usage
docker system prune -a  # Clean Docker
sudo apt autoremove
```

## 🔄 Updates & Maintenance

### Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Update Docker Images
```bash
docker-compose pull
docker-compose up -d
```

### Update SSL Certificates
Automatic with certbot, but verify:
```bash
sudo certbot renew
```

---

**🎊 Congratulations! Your RAG Chatbot is now live on the internet!**
