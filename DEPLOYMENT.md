# MarketMind Deployment Guide

This guide covers complete deployment instructions for MarketMind across different environments:
1. **[Docker Compose (Recommended - Local & VPS)](#1-docker-compose-deployment)**
2. **[Cloud PaaS Deployment (Render / Railway / Neon / Vercel)](#2-cloud-paas-deployment)**
3. **[Cloud VM / VPS Deployment (AWS EC2 / DigitalOcean)](#3-cloud-vm--vps-deployment)**

---

## 1. Docker Compose Deployment

Docker Compose orchestrates all 4 services with a single command:
- **`postgres`**: PostgreSQL 15 container initialized with schema and seed data from `db.sql`.
- **`ml-service`**: FastAPI container with PyTorch, TensorFlow, FinBERT, and multimodal predictors.
- **`backend`**: Spring Boot container packaged via multi-stage Maven build.
- **`frontend`**: Nginx container serving the web UI on port 3000.

### Prerequisites
- [Docker Engine & Docker Compose](https://docs.docker.com/get-docker/) installed.

### Steps

1. **Configure Environment Variables (Optional)**:
   ```bash
   cp .env.example .env
   ```
   *(Optionally edit `.env` to set your `FINNHUB_API_KEY` or custom database credentials).*

2. **Build and Run All Services**:
   ```bash
   docker compose up --build -d
   ```

3. **Check Service Logs & Status**:
   ```bash
   docker compose ps
   docker compose logs -f
   ```

4. **Access the Application**:
   - **Frontend UI**: [http://localhost:3000](http://localhost:3000)
   - **Spring Boot API**: [http://localhost:8080](http://localhost:8080)
   - **FastAPI ML Service**: [http://localhost:8000](http://localhost:8000)
   - **PostgreSQL**: `localhost:5432`

5. **Stop Services**:
   ```bash
   docker compose down
   ```

---

## 2. Cloud PaaS Deployment

If deploying to hosted cloud platforms (e.g. Free/Hobby tiers):

### Step A: Hosted Database (Neon / Supabase / Render Postgres)
1. Create a free PostgreSQL instance on [Neon.tech](https://neon.tech) or [Supabase](https://supabase.com).
2. Run the SQL initialization script located at:
   `AI_Investment_System_Backend/src/main/resources/db.sql` in the provider's SQL console.
3. Save your connection string: `jdbc:postgresql://<HOST>:<PORT>/<DB_NAME>`.

### Step B: ML Service (Render / Railway / Hugging Face Spaces)
1. Deploy the `ml-service/` directory as a Web Service on [Render](https://render.com) or [Railway](https://railway.app).
2. Runtime: **Python 3.10**
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Note your ML Service URL (e.g. `https://marketmind-ml.onrender.com`).

### Step C: Spring Boot Backend (Render / Railway / AWS App Runner)
1. Deploy `AI_Investment_System_Backend/` as a Web Service.
2. Build Command: `mvn clean package -DskipTests`
3. Start Command: `java -jar target/*.jar` (or use the provided `Dockerfile`).
4. Set Environment Variables:
   - `SPRING_DATASOURCE_URL`: your PostgreSQL JDBC connection string
   - `SPRING_DATASOURCE_USERNAME`: database username
   - `SPRING_DATASOURCE_PASSWORD`: database password
   - `ML_SERVICE_URL`: your ML Service URL from Step B (e.g. `https://marketmind-ml.onrender.com`)
   - `FINNHUB_API_KEY`: your Finnhub API Key

### Step D: Frontend (Vercel / Netlify / Cloudflare Pages)
1. Deploy `frontend/` to [Vercel](https://vercel.com) or [Netlify](https://netlify.com).
2. In `frontend/app.js`, configure `API_BASE_URL` to point to your deployed Spring Boot backend URL:
   ```javascript
   const API_BASE_URL = 'https://marketmind-backend.onrender.com';
   ```

---

## 3. Cloud VM / VPS Deployment (AWS EC2 / DigitalOcean)

1. Provision an Ubuntu 22.04+ Server instance (Recommended: at least 2GB RAM / 2 vCPUs).
2. Install Docker & Git:
   ```bash
   sudo apt update && sudo apt install -y docker.io docker-compose-v2 git
   sudo usermod -aG docker $USER
   ```
3. Clone your repository:
   ```bash
   git clone <YOUR_REPO_URL>
   cd MarketMind
   ```
4. Start the stack:
   ```bash
   docker compose up --build -d
   ```
5. Configure your firewall / Security Group to allow inbound traffic on ports `80`, `443`, `3000`, and `8080`.

---

## Environment Variables Reference

| Variable | Description | Default / Example |
|---|---|---|
| `POSTGRES_DB` | PostgreSQL database name | `investment_system` |
| `POSTGRES_USER` | PostgreSQL user | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres` |
| `SPRING_DATASOURCE_URL` | JDBC URL for Spring Boot | `jdbc:postgresql://postgres:5432/investment_system` |
| `ML_SERVICE_URL` | Base URL for FastAPI ML Service | `http://ml-service:8000` |
| `FINNHUB_API_KEY` | Finnhub API key for market news/quotes | Optional |
| `PORT` | Web server port override | `8080` (backend) / `8000` (ML) |
