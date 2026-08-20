"""
Shared database engine — every script in this project imports from here,
so the connection settings only live in one place.
"""

import os
from sqlalchemy import create_engine
from dotenv import load_dotenv


# Always load values from the project's .env file.
# override=True ensures an old Windows environment variable
# does not override the current .env DATABASE_URL.
load_dotenv(override=True)


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL not found. Make sure .env exists in the project folder."
    )


# Create database engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=280,
)


TARGET_YEAR = int(
    os.getenv("TARGET_PERFORMANCE_YEAR", "2023")
)

CONTAMINATION = float(
    os.getenv("CONTAMINATION", "0.08")
)