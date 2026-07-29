import os
import logging
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment loading
# ---------------------------------------------------------------------------
# load_dotenv() reads a .env file when running locally.
# In a container (Azure Container App, docker run, docker-compose) there is
# NO .env file — variables must be injected by the platform at runtime.
# load_dotenv() is a no-op when the file is absent; already-injected
# os.environ values are left untouched (override=False is the default).
# ---------------------------------------------------------------------------
load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Startup validation — runs before anything else imports settings
# ---------------------------------------------------------------------------
def _startup_check() -> None:
    has_base_url = bool(os.getenv("INVENTORY_API_BASE_URL", "").strip())

    print("[STARTUP] ----------------------------------------")
    print("[STARTUP] INVENTORY_API_BASE_URL present :", has_base_url)
    print("[STARTUP] INVENTORY_API_BASE_URL          :", os.getenv("INVENTORY_API_BASE_URL") or "(not set)")
    print("[STARTUP] API_KEY present                 :", bool(os.getenv("API_KEY", "").strip()))
    print("[STARTUP] ----------------------------------------")

    if not has_base_url:
        msg = (
            "\n"
            "============================================================\n"
            " STARTUP FAILURE: No backend API URL found.\n"
            "============================================================\n"
            " The container received none of the required env variables.\n"
            "\n"
            " Provide:\n"
            "   INVENTORY_API_BASE_URL=https://<backend-host>/api\n"
            "\n"
            " Optionally:\n"
            "   API_KEY=<bearer-token-or-api-key>\n"
            "\n"
            " Injection checklist:\n"
            "   Local dev     →  copy .env.example to .env, fill values,\n"
            "                    run: docker compose up --build\n"
            "   Azure CA      →  Portal → Container App → Environment variables\n"
            "   GitHub Actions→  add secret INVENTORY_API_BASE_URL in repo\n"
            "============================================================\n"
        )
        import sys
        print(msg, file=sys.stderr)
        raise EnvironmentError(msg)


_startup_check()

# ---------------------------------------------------------------------------
# HTTP client settings — consumed by client/inventory_client.py
# ---------------------------------------------------------------------------

# Base URL of the ASP.NET Core backend (e.g. https://trinova-backend.azurewebsites.net/api)
INVENTORY_API_BASE_URL: str = os.getenv("INVENTORY_API_BASE_URL", "").strip().rstrip("/")

# Optional bearer token or x-api-key credential.
# The client sends this as "Authorization: Bearer <token>" when present.
API_KEY: str = os.getenv("API_KEY", "").strip()

# Request timeout in seconds (connect + read).  Azure cold-starts can be slow.
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "30"))

# Retry policy: number of retries on transient HTTP errors (5xx / network).
MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "3"))

# Seconds to wait between retries (exponential back-off base).
RETRY_BACKOFF: float = float(os.getenv("RETRY_BACKOFF", "1.0"))
