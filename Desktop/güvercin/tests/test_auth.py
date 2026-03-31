import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await client.post(
        "/auth/register",
        json={
            "username": "newuser",
            "email": "new@test.com",
            "password": "password123",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient):
    payload = {
        "username": "dupuser",
        "email": "dup@test.com",
        "password": "password123",
    }
    await client.post("/auth/register", json=payload)
    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={
            "username": "loginuser",
            "email": "login@test.com",
            "password": "password123",
        },
    )
    resp = await client.post(
        "/auth/login",
        json={
            "username": "loginuser",
            "password": "password123",
        },
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={
            "username": "wrongpw",
            "email": "wrongpw@test.com",
            "password": "password123",
        },
    )
    resp = await client.post(
        "/auth/login",
        json={
            "username": "wrongpw",
            "password": "yanlisifre",
        },
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_valid_token(client: AsyncClient):
    reg = await client.post(
        "/auth/register",
        json={
            "username": "meuser",
            "email": "me@test.com",
            "password": "password123",
        },
    )
    token = reg.json()["access_token"]
    resp = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == "meuser"


@pytest.mark.asyncio
async def test_me_without_token(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401
