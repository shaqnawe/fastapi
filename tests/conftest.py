import time
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from sqlmodel import create_engine, Session, SQLModel
from app.main import app
from app.config import settings
from app.database import get_session

DATABASE_URL = (
    f"postgresql+psycopg://{settings.database_username}:"
    f"{settings.database_password}@"
    f"{settings.database_hostname}:"
    f"{settings.database_port}/"
    f"{settings.database_name}_test"
)

engine = create_engine(DATABASE_URL, echo=True)

SQLModel.metadata.create_all(bind=engine)

# Retry logic: wait for DB to be ready
MAX_RETRIES = 10
for attempt in range(MAX_RETRIES):
    try:
        with engine.connect() as conn:
            print("Database connection successful!")
            break
    except OperationalError as e:
        print(f"DB connection failed (attempt {attempt + 1}/{MAX_RETRIES})")
        time.sleep(2)
else:
    print("Could not connect to the database after multiple retries.")
    raise RuntimeError("Database not available")


@pytest.fixture()
def session():
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


@pytest.fixture()
def client(session):
    def override_get_session():
        with session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)


@pytest.fixture
def test_user(client):
    user_data = {
        "first_name": "shakti",
        "last_name": "shah ",
        "email": "test3@test.com",
        "password": "password123",
    }
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    print(res.json())
    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user
