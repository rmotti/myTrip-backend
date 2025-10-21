# app/db.py
from __future__ import annotations
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Lazy singletons
_engine = None
_SessionLocal = None

Base = declarative_base()

def _get_database_url() -> str:
    url = os.getenv("DATABASE_URL_UNPOOLED") or os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL não definido")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    # SSL obrigatório no Neon
    if "sslmode=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            _get_database_url(),
            pool_pre_ping=True,
            pool_recycle=1800,  # bom p/ serverless
            future=True,
        )
    return _engine

def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=get_engine()
        )
    return _SessionLocal()

def db_ping() -> None:
    # chama apenas quando precisar (ex.: /health)
    with get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
