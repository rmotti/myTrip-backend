# app/main.py
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
import os

# garante que o Firebase Admin inicialize (usa as envs)
from app.core import firebase  # noqa: F401

# seus routers
from app.routers import auth, users
from app.routers import trips  # NEW

# ping do DB
from app.db import db_ping

# 1) instanciar o app primeiro
app = FastAPI(
    title="mytrip-backend",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# 2) (opcional) CORS – ajuste allow_origins em produção
def _cors_origins() -> list[str]:
    defaults = {
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://my-trip-frontend.vercel.app",
    }
    # Extra origins via env, comma-separated
    extra = os.getenv("CORS_ORIGINS", "").strip()
    if extra:
        for o in extra.split(","):
            o = o.strip()
            if o:
                defaults.add(o)
    return sorted(defaults)


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3) registrar routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(trips.router)  # NEW

# 4) rotas utilitárias/health
@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/health")
def health():
    db_ping()
    return {"status": "ok", "db": "neon"}

@app.get("/health/db")
def health_db():
    try:
        db_ping()
        return {"status": "ok", "db": "connected"}
    except OperationalError as e:
        raise HTTPException(status_code=503, detail=f"db_unavailable: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"unexpected_error: {e}")
