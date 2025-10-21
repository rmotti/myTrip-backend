from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import OperationalError
from .db import db_ping

app = FastAPI(title="mytrip-backend (conexão DB)")

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
