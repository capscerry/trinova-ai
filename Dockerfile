FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
# System dependencies
# ---------------------------------------------------------------------------
# curl is required by the Docker health check.
# ---------------------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies before copying app code (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code — .dockerignore prevents .env from being baked in
COPY . .

# ---------------------------------------------------------------------------
# Runtime environment variables
# ---------------------------------------------------------------------------
# PORT: the port uvicorn listens on inside the container.
# Its value can be overridden at runtime via docker run -e PORT=<n> or the
# platform's environment variable injection (Azure Container Apps, etc.).
# ---------------------------------------------------------------------------
ENV PORT=8080

EXPOSE 8080

CMD sh -c "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"
