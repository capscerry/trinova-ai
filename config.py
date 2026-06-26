import os
from dotenv import load_dotenv

load_dotenv()

SERVER = os.getenv("SERVER")
DATABASE = os.getenv("DATABASE")
UID = os.getenv("UID")
PWD = os.getenv("PWD")
DRIVER = os.getenv("DRIVER")

DATABASE_CONNECTION = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    f"UID={UID};"
    f"PWD={PWD};"
    "TrustServerCertificate=yes;"
)