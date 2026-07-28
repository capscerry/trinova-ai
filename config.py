import os
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv("SQL_CONNECTION_STRING_DEV")

if connection_string:
    DATABASE_CONNECTION = connection_string
else:
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