FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
# System dependencies
# ---------------------------------------------------------------------------
# httpx uses the system's CA bundle for TLS verification.
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
# These are the NAMES of the variables the app expects.
# Their VALUES must be injected at runtime via:
#   - docker run -e / --env-file              (local)
#   - docker-compose environment / env_file   (local dev)
#   - Azure Container App environment variable secrets  (production)
#   - GitHub Actions az containerapp update   (CI/CD)
#
# DO NOT set values here — this block documents what is required.
# ---------------------------------------------------------------------------
ENV INVENTORY_API_BASE_URL="" \
    API_KEY="" \
    REQUEST_TIMEOUT="30" \
    MAX_RETRIES="3" \
    RETRY_BACKOFF="1.0" \
    PORT=8080

EXPOSE 8080

CMD sh -c "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"
