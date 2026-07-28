FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
# System dependencies: ODBC Driver 18 for SQL Server
# ---------------------------------------------------------------------------
RUN apt-get update && \
    apt-get install -y \
        curl \
        gnupg \
        ca-certificates \
        apt-transport-https \
        unixodbc \
        unixodbc-dev && \
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/microsoft-prod.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 && \
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
#   - docker run -e / --env-file        (local)
#   - docker-compose environment / env_file  (local dev)
#   - Azure Container App environment variable secrets  (production)
#   - GitHub Actions az containerapp update  (CI/CD)
#
# DO NOT set values here — this block documents what is required.
# ---------------------------------------------------------------------------
ENV SQL_CONNECTION_STRING_DEV="" \
    DB_SERVER="" \
    DB_NAME="" \
    DB_UID="" \
    DB_PWD="" \
    PORT=8080

# Expose the port uvicorn will listen on
EXPOSE 8080

CMD sh -c "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"