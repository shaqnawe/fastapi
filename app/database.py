import os
import time
from typing import Annotated
from fastapi import Depends
from sqlalchemy.exc import OperationalError
from sqlmodel import SQLModel, create_engine, Session
# from dotenv import load_dotenv, dotenv_values
from app.models import Post, User, Vote
from .config import settings

# load_dotenv()
# print(dotenv_values())
DATABASE_URL = (
    f"postgresql+psycopg://{settings.database_username}:"
    f"{settings.database_password}@"
    f"{settings.database_hostname}:"
    f"{settings.database_port}/"
    f"{settings.database_name}"
)
engine = create_engine(DATABASE_URL, echo=True)

# Retry logic: wait for DB to be ready
MAX_RETRIES = 10
for attempt in range(MAX_RETRIES):
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful!")
            break
    except OperationalError as e:
        print(f"❌ DB connection failed (attempt {attempt + 1}/{MAX_RETRIES})")
        time.sleep(2)
else:
    print("💥 Could not connect to the database after multiple retries.")
    raise RuntimeError("Database not available")

# SQLModel.metadata.create_all(bind=engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
