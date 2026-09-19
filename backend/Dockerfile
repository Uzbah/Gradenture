# Backend image — used directly for local dev (docker-compose) and as the
# base for the production build (see the root Dockerfile).
FROM python:3.12-slim

# `backend` is the importable package, so it has to sit inside the working
# directory rather than be the working directory: the app is started as
# `python -m backend.run` from /app.
WORKDIR /app

# Copy only the dependency list first so Docker can cache this layer —
# it only re-runs `pip install` when requirements.txt actually changes,
# not on every source-code edit.
COPY requirements.txt backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY . backend/

# Print logs immediately instead of buffering them (helps `docker logs`).
ENV PYTHONUNBUFFERED=1

EXPOSE 3001

CMD ["python", "-m", "backend.run"]
