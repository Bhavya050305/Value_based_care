import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not found. Copy .env.example to .env and fill it in.")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=280)
