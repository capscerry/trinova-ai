import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Connection string builder
# ---------------------------------------------------------------------------
# Azure SQL via ODBC Driver 18 requires a specific pyodbc DSN-less format.
# The ADO.NET-style key "User Id=" is NOT recognised by pyodbc — it expects
# "UID=".  Passing the raw ADO.NET string causes the username to be dropped
# entirely, which is why Azure SQL returns error 18456 (login failed).
#
# Strategy:
#   1. Prefer individual env vars (DB_SERVER, DB_NAME, DB_UID, DB_PWD).
#   2. Fall back to SQL_CONNECTION_STRING_DEV, but PARSE it into parts and
#      REBUILD it as a valid pyodbc string — never pass the raw value.
# ---------------------------------------------------------------------------

def _parse_ado_string(raw: str) -> dict:
    """
    Parse a semicolon-delimited ADO.NET / JDBC connection string into a dict.
    Handles keys that contain '=' in their value by splitting only on the
    first '=' per segment.

    Example input:
        Server=host;Database=db;User Id=user@server;Password=p@ss;
    Returns:
        {"server": "host", "database": "db", "user id": "user@server",
         "password": "p@ss"}
    """
    parts = {}
    for segment in raw.split(";"):
        segment = segment.strip()
        if not segment:
            continue
        if "=" not in segment:
            continue
        key, _, value = segment.partition("=")
        parts[key.strip().lower()] = value.strip()
    return parts


def _build_pyodbc_string(server: str, database: str, uid: str, pwd: str) -> str:
    """
    Build a pyodbc DSN-less connection string for ODBC Driver 18 for SQL Server.

    Key rules enforced here:
    - DRIVER must be {ODBC Driver 18 for SQL Server}
    - SERVER must use the tcp: prefix and explicit port 1433
    - UID must be the full Azure SQL username (e.g. user@admin@server-name)
    - TrustServerCertificate=yes  (pyodbc uses yes/no, NOT True/False)
    - Encrypt=yes is required by ODBC Driver 18 by default; explicit here for
      clarity
    """
    # Normalise server — strip any existing "tcp:" prefix or port so we can
    # re-add them consistently.
    server_host = server.replace("tcp:", "").split(",")[0].strip()

    conn_str = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER=tcp:{server_host},1433;"
        f"DATABASE={database};"
        f"UID={uid};"
        f"PWD={pwd};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
    )
    return conn_str


# ---------------------------------------------------------------------------
# Resolve individual connection parameters
# ---------------------------------------------------------------------------
# Priority 1: discrete env vars (cleanest, no parsing needed)
_server   = os.getenv("DB_SERVER")
_database = os.getenv("DB_NAME")
_uid      = os.getenv("DB_UID")
_pwd      = os.getenv("DB_PWD")

# Priority 2: parse SQL_CONNECTION_STRING_DEV if discrete vars are absent
if not all([_server, _database, _uid, _pwd]):
    _raw = os.getenv("SQL_CONNECTION_STRING_DEV", "")
    if _raw:
        _parsed = _parse_ado_string(_raw)

        # Map ADO.NET key variants → our internal names
        _server   = _server   or _parsed.get("server")
        _database = _database or _parsed.get("database")
        # ADO.NET uses "user id"; pyodbc uses "uid" — map both
        _uid      = _uid      or _parsed.get("uid") or _parsed.get("user id")
        _pwd      = _pwd      or _parsed.get("pwd") or _parsed.get("password")

# ---------------------------------------------------------------------------
# Debug logging — safe (password is never printed)
# ---------------------------------------------------------------------------
logger.debug("=== Azure SQL Connection Debug ===")
logger.debug("SQL_CONNECTION_STRING_DEV present : %s", bool(os.getenv("SQL_CONNECTION_STRING_DEV")))
logger.debug("Resolved SERVER                   : %s", _server)
logger.debug("Resolved DATABASE                 : %s", _database)
logger.debug("Resolved UID                      : %s", _uid)
logger.debug("Password present                  : %s", bool(_pwd))

# Also print to stdout so the debug info is visible in the container/server
# log even when the logging level hasn't been configured yet.
print("[DB DEBUG] SQL_CONNECTION_STRING_DEV present :", bool(os.getenv("SQL_CONNECTION_STRING_DEV")))
print("[DB DEBUG] Resolved SERVER                   :", _server)
print("[DB DEBUG] Resolved DATABASE                 :", _database)
print("[DB DEBUG] Resolved UID                      :", _uid)
print("[DB DEBUG] Password present                  :", bool(_pwd))

# ---------------------------------------------------------------------------
# Guard: fail fast with a clear message if any required parameter is missing
# ---------------------------------------------------------------------------
_missing = [name for name, val in [
    ("SERVER",   _server),
    ("DATABASE", _database),
    ("UID",      _uid),
    ("PWD",      _pwd),
] if not val]

if _missing:
    raise EnvironmentError(
        f"Missing required database connection parameter(s): {', '.join(_missing)}. "
        "Set DB_SERVER, DB_NAME, DB_UID, DB_PWD  —or—  SQL_CONNECTION_STRING_DEV."
    )

# ---------------------------------------------------------------------------
# Build the final pyodbc connection string
# ---------------------------------------------------------------------------
DATABASE_CONNECTION = _build_pyodbc_string(_server, _database, _uid, _pwd)
