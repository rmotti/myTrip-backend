from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from sqlalchemy import select
from sqlalchemy.orm import Session
from firebase_admin import auth as fba

from app.core.settings import settings
from app.db import get_db
from app.models import User  # garante que app/models.py exporta User (ou use: from app.models import User as User)


bearer = HTTPBearer()


def create_access_token(sub: str, extra: Optional[dict] = None) -> str:
    """
    Cria um JWT curto (HS256) assinado com JWT_SECRET.
    sub = firebase_uid
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expires_min)).timestamp()),
        **(extra or {}),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def _get_user_by_uid(db: Session, uid: str) -> Optional[User]:
    return db.scalar(select(User).where(User.firebase_uid == uid))


def get_current_user(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    Lê Authorization: Bearer <token>.
    1) Tenta validar como ID token do Firebase.
       - espelha/sincroniza no Postgres (cria se não existir)
    2) Se falhar, tenta como JWT curto interno (HS256).
    Retorna o objeto User ativo.
    """
    token = cred.credentials

    # 1) Tenta ID token do Firebase
    try:
        decoded = fba.verify_id_token(token, check_revoked=True)
        uid = decoded["uid"]
        email = decoded.get("email")
        name = decoded.get("name")
        picture = decoded.get("picture")

        user = _get_user_by_uid(db, uid)
        if not user:
            # cria espelho no Postgres
            user = User(
                firebase_uid=uid,
                email=email or f"{uid}@no-email.firebase",
                name=name,
                photo_url=picture,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # sincronização leve de perfil
            changed = False
            if email and user.email != email:
                user.email = email
                changed = True
            if name and user.name != name:
                user.name = name
                changed = True
            if picture and user.photo_url != picture:
                user.photo_url = picture
                changed = True
            if changed:
                db.commit()

        # atualiza last_login_at
        user.last_login_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)

        if not user.is_active:
            raise HTTPException(status_code=401, detail="user inactive")

        return user

    except Exception:
        # 2) Tenta JWT curto interno
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
            uid = payload.get("sub")
            if not uid:
                raise HTTPException(status_code=401, detail="invalid token")
        except Exception:
            raise HTTPException(status_code=401, detail="invalid token")

        user = _get_user_by_uid(db, uid)
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="user not found or inactive")
        return user
