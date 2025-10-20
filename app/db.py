from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
import os

# Carrega .env (deixe o .env ganhar do ambiente local quando estiver desenvolvendo)
load_dotenv(override=True)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL não definido")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    # Ajustes úteis em dev:
    pool_recycle=1800,   # evita conexões velhas
    pool_size=5,
    max_overflow=5,
)

def db_ping() -> None:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
