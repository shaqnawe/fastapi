import pytest
from jose import jwt
from app.config import settings
from app.schemas import UserResponse, Token


# def test_root(client):
#     res = client.get("/")
#     assert res.json().get("message") == "Welcome to my api!!"
#     assert res.status_code == 200


def test_create_user(client):
    res = client.post(
        "/users/",
        json={
            "first_name": "Test2",
            "last_name": "Tester2",
            "email": "test2@test.com",
            "password": "password123",
        },
    )
    new_user = UserResponse(**res.json())
    assert res.status_code == 201
    assert new_user.email == "test2@test.com"


def test_login_user(client, test_user):
    res = client.post(
        "/login",
        data={
            "username": test_user["email"],
            "password": test_user["password"],
        },
    )
    login_res = Token(**res.json())
    payload = jwt.decode(
        login_res.access_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    id: int = payload.get("user_id")
    assert id == test_user["id"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrongemail@test.com", "password123", 403),
        ("test3@test.com", "wrongpassword", 403),
        ("wrongemail@test.com", "wrongpassword", 403),
        (None, "password123", 403),
        ("test3@test.com", None, 403),
    ],
)
def test_invalid_login(client, test_user, email, password, status_code):
    res = client.post(
        "/login",
        data={
            "username": email,
            "password": password,
        },
    )
    assert res.status_code == status_code
