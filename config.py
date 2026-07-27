from dotenv import load_dotenv
import os

load_dotenv()

SERVER = os.getenv("SERVER")
DATABASE = os.getenv("DATABASE")
UID = os.getenv("UID")
PWD = os.getenv("PWD")
DRIVER = os.getenv("DRIVER", "ODBC Driver 18 for SQL Server")

DATABASE_CONNECTION = (
    f"Driver={{{DRIVER}}};"
    f"Server=tcp:{SERVER},1433;"
    f"Database={DATABASE};"
    f"Uid={UID};"
    f"Pwd={PWD};"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Connection Timeout=30;"
)

print("=== DATABASE CONFIG ===")
print(f"SERVER={SERVER}")
print(f"DATABASE={DATABASE}")
print(f"UID={UID}")
print(DATABASE_CONNECTION.replace(PWD, "********"))