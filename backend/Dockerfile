# Backend image — used directly for local dev (docker-compose) and as the
# base for the production build (see the root Dockerfile).
FROM python:3.12-slim

WORKDIR /app

# Copy only the dependency list first so Docker can cache this layer —
# it only re-runs `pip install` when requirements.txt actually changes,
# not on every source-code edit.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Print logs immediately instead of buffering them (helps `docker logs`).
ENV PYTHONUNBUFFERED=1

EXPOSE 3001

CMD ["python", "main.py"]
