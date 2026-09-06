# Production image: builds the frontend, then bakes the static files into
# the backend image so FastAPI serves both API and UI from one container
# on port 3001 — the same "serve frontend from backend" setup described in
# the README, just containerized.
#
# Build from the repo root:  docker build -t gradenture .
# Run:                       docker run -p 3001:3001 --env-file backend/.env gradenture

# --- Stage 1: build the frontend static bundle ---
FROM node:20-slim AS frontend-build

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend/ ./
RUN npm run build

# --- Stage 2: backend + the built frontend ---
FROM python:3.12-slim

WORKDIR /app/backend

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# main.py looks for the built frontend at ../frontend/dist relative to
# itself (/app/backend) — so it must land at /app/frontend/dist.
COPY --from=frontend-build /app/frontend/dist /app/frontend/dist

ENV PYTHONUNBUFFERED=1 \
    NODE_ENV=production

EXPOSE 3001

CMD ["python", "main.py"]
