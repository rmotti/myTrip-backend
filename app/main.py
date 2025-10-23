# app/main.py
from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import OperationalError
import os
from datetime import datetime, timezone  # NEW

# garante que o Firebase Admin inicialize (usa as envs)
from app.core import firebase  # noqa: F401

# seus routers
from app.routers import auth, users
from app.routers.trips import router as trips_router


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

# --- HEALTH METADATA --- #
START_TIME = datetime.now(timezone.utc)  # NEW


def _env(name: str, default: str = "unknown") -> str:  # NEW
    val = os.getenv(name, default).strip()
    return val or default


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
app.include_router(trips_router)

# 4) rotas utilitárias/health
@app.get("/", include_in_schema=False)
def root():
    return {"message": "MyTrip API running 🚀"}

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


# -------- NEW: /health/app com metadados de deploy -------- #
@app.get("/health/app", tags=["health"])
def health_app():
    # DB status
    try:
        db_ping()
        db_status = "connected"
    except Exception:
        db_status = "unavailable"

    # Metadados (Vercel + genéricos)
    return {
        "status": "ok",
        "service": "mytrip-backend",
        "version": app.version,
        "environment": _env("ENV", _env("VERCEL_ENV", "development")),
        "database": db_status,
        "firebase": "initialized",
        "uptime_seconds": int((datetime.now(timezone.utc) - START_TIME).total_seconds()),
        # Vercel Git metadata
        "git_commit": _env("VERCEL_GIT_COMMIT_SHA", _env("GIT_COMMIT_SHA", "local")),
        "git_message": _env("VERCEL_GIT_COMMIT_MESSAGE", ""),
        "git_branch": _env("VERCEL_GIT_COMMIT_REF", _env("GIT_BRANCH", "")),
        # Infra hints
        "region": _env("VERCEL_REGION", _env("RAILWAY_REGION", _env("FLY_REGION", ""))),
        "node": _env("HOSTNAME", ""),
    }
