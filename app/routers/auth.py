from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as fba
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])
bearer = HTTPBearer()

def _upsert_user_from_firebase(decoded: dict, db: Session) -> User:
    uid = decoded.get("uid")
    email = decoded.get("email") or f"{uid}@no-email.firebase"
    name = decoded.get("name")
    picture = decoded.get("picture")

    if not uid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="firebase token missing uid")

    user = (
        db.query(User)
          .filter((User.firebase_uid == uid) | (User.email == email))
          .first()
    )

    if user is None:
        user = User(
            firebase_uid=uid,
            email=email,
            name=name,
            photo_url=picture,
            is_active=True,
            last_login_at=datetime.now(timezone.utc),
        )
        db.add(user)
    else:
        changed = False
        if not user.firebase_uid:
            user.firebase_uid = uid; changed = True
        if name and user.name != name:
            user.name = name; changed = True
        if picture and user.photo_url != picture:
            user.photo_url = picture; changed = True
        if not user.is_active:
            user.is_active = True; changed = True
        user.last_login_at = datetime.now(timezone.utc)
        if changed:
            pass

    db.commit()
    db.refresh(user)
    return user

@router.post("/exchange")
def exchange_token(
    cred: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    """
    Recebe um Firebase ID Token via Authorization: Bearer <ID_TOKEN>,
    valida, faz upsert no Postgres e devolve um JWT curto (HS256) com sub=firebase_uid.
    """
    try:
        decoded = fba.verify_id_token(cred.credentials, check_revoked=True)
    except Exception:
        # evita 500 e deixa claro para o cliente
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid firebase token")

    user = _upsert_user_from_firebase(decoded, db)
    token = create_access_token(sub=user.firebase_uid)
    return {"access_token": token, "token_type": "bearer", "expires_in_min": 60}
