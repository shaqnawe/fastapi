import os
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from .models import User
from .database import SessionDep
from sqlmodel import select
from datetime import datetime, timedelta, timezone
from .schemas import TokenData
from fastapi.security import OAuth2PasswordBearer
from .config import settings

KEY = settings.secret_key
ALGORITHM = settings.algorithm
TOKEN_EXPIRE_MINUTES = int(settings.access_token_expire_minutes)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    print("🔐 Verifying token:", token)
    try:
        payload = jwt.decode(token, KEY, algorithms=ALGORITHM)
        print("✅ Decoded payload:", payload)
        print(f"USER ID TYPE: {type(payload.get('user_id'))}")
        user_id: int = payload.get("user_id")
        if user_id is None:
            print("✅ Decoded payload:", payload)
            raise credentials_exception
        print(f"USERID : {user_id}")
        return TokenData(id=int(user_id))
    except JWTError as e:
        print("🚫 JWT error:", str(e))
        raise credentials_exception


def get_current_user(db: SessionDep, token: str = Depends(oauth2_scheme)):
    print("🔍 get_current_user called")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)
    print("✅ Token data:", token_data)
    user = db.exec(select(User).where(User.id == token_data.id)).first()
    if not user:
        raise credentials_exception
    print("✅ User found:", user.email)
    return user
