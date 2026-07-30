import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

PORT = int(os.getenv("PORT", "8080"))

# Database Configuration
SERVER = os.getenv("SERVER")
DATABASE = os.getenv("DATABASE")
UID = os.getenv("UID")
PWD = os.getenv("PWD")
DRIVER = os.getenv("DRIVER", "ODBC Driver 18 for SQL Server")

DATABASE_CONNECTION = (
    f"Driver={{{DRIVER}}};"
    f"Server={SERVER};"
    f"Database={DATABASE};"
    f"UID={UID};"
    f"PWD={PWD};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)