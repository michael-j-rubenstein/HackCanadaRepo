# HackCanadaRepo

Full-stack project with React Native Expo frontend, FastAPI backend, and PostgreSQL database.

## Prerequisites

- Docker & Docker Compose
- Node.js 18+
- Expo CLI (`npm install -g expo-cli`)

## Quick Start

```bash
chmod +x run_dev.sh
./run_dev.sh
```

This will:
1. Start PostgreSQL and FastAPI backend via Docker Compose
2. Wait for the backend health check
3. Start the Expo dev server

## Backend

- API docs: http://localhost:8080/docs
- Health check: http://localhost:8080/health

```bash
cd backend
docker-compose up --build
```

## Frontend

```bash
cd frontend
npm install
npx expo start
```

## Database

```bash
docker exec -it hackcanada-postgres psql -U hackcanada -d hackcanada_db
```

## Migrations

```bash
cd backend
docker-compose exec backend alembic revision --autogenerate -m "description"
docker-compose exec backend alembic upgrade head
```
