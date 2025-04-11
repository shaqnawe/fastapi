from fastapi import status, HTTPException, APIRouter
from app.database import SessionDep
from sqlmodel import select
from app.models import User
from app.schemas import UserCreate, UserResponse
from ..utils import hash_password


router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, db: SessionDep):
    # Hash the password
    hashed_password = hash_password(user.password)
    user.password = hashed_password
    new_user = User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=list[UserResponse])
def get_users(db: SessionDep):
    users = db.exec(select(User)).all()
    return users


@router.get("/{id}", response_model=UserResponse)
def get_user(id: int, db: SessionDep):
    user = db.get(User, id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id: {id} was not found.",
        )
    return user
