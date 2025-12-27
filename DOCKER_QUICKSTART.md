# 🐳 Docker Quick Start

## One-Command Launch

```bash
docker-compose up
```

That's it! The entire stack (API + Web UI) will be running in under 2 minutes.

---

## What Gets Installed

- **API Server** (Flask) on http://localhost:5000
- **Web UI** (Next.js) on http://localhost:3000
- All Python dependencies (PyTorch, OpenCV, etc.)
- All Node.js dependencies

---

## Usage

### 1. Start Services

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background (detached)
docker-compose up -d
```

### 2. Access Web UI

Open browser: **http://localhost:3000**

- Drag and drop images
- Adjust epsilon slider
- Download poisoned images + signatures

### 3. Use API Directly

```bash
curl -X POST http://localhost:5000/api/poison \
  -F "image=@my_art.jpg" \
  -F "epsilon=0.01" \
  > response.json
```

### 4. Stop Services

```bash
# Stop and remove containers
docker-compose down

# Stop, remove containers, and clean volumes
docker-compose down -v
```

---

## Troubleshooting

### Port Already in Use

If ports 3000 or 5000 are taken:

```yaml
# Edit docker-compose.yml
services:
  api:
    ports:
      - "5001:5000"  # Change left side only
  web:
    ports:
      - "3001:3000"  # Change left side only
```

### Check Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service
docker-compose logs api
docker-compose logs web
```

### Rebuild After Code Changes

```bash
# Rebuild containers
docker-compose build

# Rebuild and restart
docker-compose up --build
```

---

## Development Mode

For local development with hot-reload:

```bash
# Use local setup instead
./setup.sh
./run_api.sh    # Terminal 1
./run_web.sh    # Terminal 2
```

Docker is best for:
- ✅ Clean installation
- ✅ Production deployment
- ✅ Sharing with non-technical users
- ✅ Consistent environment

Local setup is best for:
- ✅ Active development
- ✅ Debugging
- ✅ Faster iteration

---

## Production Deployment

### Deploy to Cloud

**Option 1: Docker Hub + AWS ECS**

```bash
# Build and push
docker build -t yourusername/basilisk-api:latest -f Dockerfile.api .
docker build -t yourusername/basilisk-web:latest -f Dockerfile.web .
docker push yourusername/basilisk-api:latest
docker push yourusername/basilisk-web:latest

# Deploy to ECS (follow AWS docs)
```

**Option 2: Fly.io (Recommended for MVP)**

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy API
flyctl launch --dockerfile Dockerfile.api --name basilisk-api

# Deploy Web
flyctl launch --dockerfile Dockerfile.web --name basilisk-web
```

**Option 3: Railway**

1. Connect GitHub repo
2. Select `Dockerfile.api` for API service
3. Select `Dockerfile.web` for Web service
4. Deploy automatically

---

## System Requirements

### Minimum

- Docker Desktop (or Docker + Docker Compose)
- 4GB RAM
- 5GB disk space

### Recommended

- 8GB RAM (for faster processing)
- 10GB disk space
- SSD for better performance

### GPU Support (Optional)

For GPU acceleration:

```yaml
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

Requires:
- NVIDIA GPU
- nvidia-docker2 installed
- CUDA-compatible drivers

---

## FAQ

**Q: Can I use this without Docker?**
A: Yes! Use `./setup.sh` for local installation.

**Q: How much RAM does it need?**
A: 2GB minimum, 4GB recommended. PyTorch loads models into memory.

**Q: Can I deploy to Vercel/Netlify?**
A: Web UI yes, API no (needs Python runtime). Use Fly.io or Railway for API.

**Q: Is GPU required?**
A: No, CPU works fine. GPU just makes it 10x faster.

**Q: Can I run this on a Raspberry Pi?**
A: Technically yes, but very slow. Use cloud GPU workers instead.

---

## Support

- **Issues:** https://github.com/abendrothj/basilisk/issues
- **Docs:** See README.md
- **Community:** GitHub Discussions

---

**Next:** After starting with Docker, see [README.md](README.md) for usage examples.
