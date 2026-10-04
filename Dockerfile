# Production image: builds the frontend, then bakes the static files into
# the backend image so FastAPI serves both API and UI from one container
# on port 3001 — the same "serve frontend from backend" setup described in
# the README, just containerized.
#
# Build from the repo root:  docker build -t gradenture .
# Run:                       docker run -p 3001:3001 --env-file backend/.env gradenture
#
# Redis is not in this image. Point REDIS_HOST at one; the app exits at startup
# if it cannot reach it.

# --- Stage 1: build the frontend static bundle ---
FROM node:20-slim AS frontend-build

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# --- Stage 2: backend + the built frontend ---
FROM python:3.12-slim

# /app is the import root: `backend` is a package inside it, and
# core/path_conf.py resolves the frontend to its sibling ../frontend/dist.
WORKDIR /app

COPY backend/requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ backend/

COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

ENV PYTHONUNBUFFERED=1 \
    ENVIRONMENT=prod

EXPOSE 3001

CMD ["python", "-m", "backend.run"]
