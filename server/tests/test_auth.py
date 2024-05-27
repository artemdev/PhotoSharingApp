from unittest.mock import Mock

import pytest
from sqlalchemy import select
from starlette.testclient import TestClient

from src.database.models import User
from src.routes.auth import router
from src.conf import messages
from tests.conftest import TestingSessionLocal

user_data = {"username": "agent", "email": "agent@gmail.com", "password": "00000000"}


def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data
    assert "avatar" in data


def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("api/auth/signup", json=user_data)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"


def test_not_confirmed_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"


@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.confirmed = True
            await session.commit()

    response = client.post("api/auth/login",
                           data={"username": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data


def test_wrong_password_login(client):
    response = client.post("api/auth/login",
                           data={"username": user_data.get("email"), "password": "password"})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"


def test_wrong_email_login(client):
    response = client.post("api/auth/login",
                           data={"username": "email", "password": user_data.get("password")})
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"


def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           data={"password": user_data.get("password")})
    assert response.status_code == 422, response.text
    data = response.json()
    assert "detail" in data


def test_request_email(client):
    response = client.post("/auth/request_email", json={"email": user_data["email"]})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Check your email for confirmation."


def test_request_email_confirmed(client):
    response = client.post("/auth/request_email", json={"email": "confirmed@gmail.com"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Your email is already confirmed"


@pytest.mark.asyncio
async def test_confirmed_email(client):
    async with TestingSessionLocal() as session:
        user = User(username="test", email="test@gmail.com", password="12345678", confirmed=False)
        session.add(user)
        await session.commit()

    response = client.get("/auth/confirmed_email/verification_token")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Email confirmed"


@pytest.mark.asyncio
async def test_refresh_token(client):
    async with TestingSessionLocal() as session:
        user = User(username="test", email="test@gmail.com", password="12345678", confirmed=True)
        session.add(user)
        await session.commit()

    response = client.get("/auth/refresh_token", headers={"Authorization": "Bearer valid_refresh_token"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert "token_type" in data
