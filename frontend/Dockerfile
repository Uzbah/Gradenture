# Dev-only image — runs the Vite dev server with hot reload.
# (Production doesn't use this: the frontend is built to static files and
# served by the backend instead — see the root Dockerfile.)
FROM node:20-slim

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

# --host exposes the dev server outside the container. Without it, Vite
# binds to 127.0.0.1 *inside* the container and nothing outside can reach it,
# even with the port published — a classic Docker+Vite gotcha.
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
