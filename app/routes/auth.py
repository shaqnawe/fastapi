from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app.database import SessionDep
from sqlmodel import select
from app.models import User
from ..schemas import Token

# from app.schemas import UserLogin
from ..utils import verify_password
from ..oauth import create_access_token

router = APIRouter(tags=["Authentication"])
OAuth2Dep = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/login", response_model=Token)
def login(credentials: OAuth2Dep, db: SessionDep):
    user = db.exec(select(User).where(User.email == credentials.username)).first()
    print(user.model_dump())
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials."
        )
    # generate access token
    access_token = create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
