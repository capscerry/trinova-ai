import os
import sys
import logging
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment loading
# ---------------------------------------------------------------------------
# load_dotenv() reads a .env file when running locally.
# In a container (Azure Container App, docker run, docker-compose) there is
# NO .env file — variables must be injected by the platform at runtime.
# load_dotenv() is safe to call in both cases: it is a no-op when the file
# is absent, and the already-injected os.environ values are left untouched
# (override=False is the default).
# ---------------------------------------------------------------------------
load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Startup validation — runs before anything else imports DATABASE_CONNECTION
# ---------------------------------------------------------------------------
def _startup_check() -> None:
    has_conn_string = bool(os.getenv("SQL_CONNECTION_STRING_DEV", "").strip())
    has_discrete    = all([
        os.getenv("DB_SERVER", "").strip(),
        os.getenv("DB_NAME",   "").strip(),
        os.getenv("DB_UID",    "").strip(),
        os.getenv("DB_PWD",    "").strip(),
    ])

    # Safe diagnostic — always printed so it appears in container logs
    print("[DB STARTUP] ----------------------------------------")
    print("[DB STARTUP] SQL_CONNECTION_STRING_DEV present :", has_conn_string)
    print("[DB STARTUP] Discrete DB_* vars all present    :", has_discrete)
    print("[DB STARTUP] DB_SERVER                         :", os.getenv("DB_SERVER") or "(not set)")
    print("[DB STARTUP] DB_NAME                           :", os.getenv("DB_NAME")   or "(not set)")
    print("[DB STARTUP] DB_UID                            :", os.getenv("DB_UID")    or "(not set)")
    print("[DB STARTUP] DB_PWD present                    :", bool(os.getenv("DB_PWD", "").strip()))
    print("[DB STARTUP] ----------------------------------------")

    if not has_conn_string and not has_discrete:
        msg = (
            "\n"
            "============================================================\n"
            " STARTUP FAILURE: No database credentials found.\n"
            "============================================================\n"
            " The container received none of the required env variables.\n"
            "\n"
            " Provide EITHER:\n"
            "   SQL_CONNECTION_STRING_DEV=Server=...;Database=...;...\n"
            "\n"
            " OR all four discrete variables:\n"
            "   DB_SERVER   = <azure-sql-hostname>\n"
            "   DB_NAME     = <database>\n"
            "   DB_UID      = <user@admin>   ← short form, no @server-name suffix\n"
            "   DB_PWD      = <password>\n"
            "\n"
            " Injection checklist:\n"
            "   Local dev     →  copy .env.example to .env, fill values,\n"
            "                    run: docker compose up --build\n"
            "   Azure CA      →  Portal → Container App → Environment variables\n"
            "                    add SQL_CONNECTION_STRING_DEV as a secret ref\n"
            "   GitHub Actions→  add secret SQL_CONNECTION_STRING_DEV in repo,\n"
            "                    workflow passes it via az containerapp update\n"
            "============================================================\n"
        )
        print(msg, file=sys.stderr)
        raise EnvironmentError(msg)


_startup_check()

# ---------------------------------------------------------------------------
# Connection string parser / builder
# ---------------------------------------------------------------------------

def _parse_ado_string(raw: str) -> dict:
    """
    Parse a semicolon-delimited ADO.NET/JDBC connection string into a dict.

    Splits on the FIRST '=' per segment so values that contain '=' are safe.

    Example:
        "Server=host;Database=db;User Id=user@admin;Password=p@ss;"
    Returns:
        {"server": "host", "database": "db", "user id": "user@admin",
         "password": "p@ss"}
    """
    parts = {}
    for segment in raw.split(";"):
        segment = segment.strip()
        if not segment or "=" not in segment:
            continue
        key, _, value = segment.partition("=")
        parts[key.strip().lower()] = value.strip()
    return parts


def _build_pyodbc_string(server: str, database: str, uid: str, pwd: str) -> str:
    """
    Build a valid pyodbc DSN-less connection string for ODBC Driver 18.

    Enforced requirements:
    - DRIVER={ODBC Driver 18 for SQL Server}
    - SERVER uses  tcp:<host>,1433  (Azure SQL requires tcp: + explicit port)
    - UID is the Azure SQL username  e.g.  user@admin  (no @server-name suffix)
    - TrustServerCertificate=yes  (pyodbc needs yes/no, NOT True/False)
    - Encrypt=yes  (required by ODBC Driver 18 by default; explicit for clarity)
    """
    # Normalise: strip any existing "tcp:" prefix and port before re-adding
    server_host = server.replace("tcp:", "").split(",")[0].strip()

    return (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER=tcp:{server_host},1433;"
        f"DATABASE={database};"
        f"UID={uid};"
        f"PWD={pwd};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )


# ---------------------------------------------------------------------------
# Resolve connection parameters
# ---------------------------------------------------------------------------
# Priority 1 — discrete env vars (unambiguous, no parsing needed)
_server   = os.getenv("DB_SERVER",  "").strip() or None
_database = os.getenv("DB_NAME",    "").strip() or None
_uid      = os.getenv("DB_UID",     "").strip() or None
_pwd      = os.getenv("DB_PWD",     "").strip() or None

# Priority 2 — parse SQL_CONNECTION_STRING_DEV if any discrete var is missing
if not all([_server, _database, _uid, _pwd]):
    _raw = os.getenv("SQL_CONNECTION_STRING_DEV", "").strip()
    if _raw:
        _parsed = _parse_ado_string(_raw)
        # Map both ADO.NET "user id" and pyodbc "uid" key variants
        _server   = _server   or _parsed.get("server")
        _database = _database or _parsed.get("database")
        _uid      = _uid      or _parsed.get("uid") or _parsed.get("user id")
        _pwd      = _pwd      or _parsed.get("pwd") or _parsed.get("password")

# ---------------------------------------------------------------------------
# Final guard — fail fast with a clear per-parameter message
# ---------------------------------------------------------------------------
_missing = [name for name, val in [
    ("SERVER",   _server),
    ("DATABASE", _database),
    ("UID",      _uid),
    ("PWD",      _pwd),
] if not val]

if _missing:
    raise EnvironmentError(
        f"Database configuration incomplete. Missing parameter(s): "
        f"{', '.join(_missing)}. "
        f"Check that SQL_CONNECTION_STRING_DEV (or DB_SERVER / DB_NAME / "
        f"DB_UID / DB_PWD) are injected into the container at runtime."
    )

# ---------------------------------------------------------------------------
# Build the final pyodbc connection string
# ---------------------------------------------------------------------------
DATABASE_CONNECTION = _build_pyodbc_string(_server, _database, _uid, _pwd)
