import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv, dotenv_values
from app.models import Post, User, Vote
from .config import settings

load_dotenv()
print(dotenv_values())
DATABASE_URL = (
    f"postgresql://{settings.database_username}:"
    f"{settings.database_password}@"
    f"{settings.database_hostname}:"
    f"{settings.database_port}/"
    f"{settings.database_name}"
)
engine = create_engine(DATABASE_URL, echo=True)

# SQLModel.metadata.create_all(bind=engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
