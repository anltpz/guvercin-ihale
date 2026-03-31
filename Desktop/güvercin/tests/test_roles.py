import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_buyer_cannot_create_pigeon(client: AsyncClient):
    """Alıcı güvercin ilanı oluşturamaz → 403."""
    reg = await client.post(
        "/auth/register",
        json={
            "username": "onlybuyer",
            "email": "onlybuyer@test.com",
            "password": "test123",
            "roles": ["buyer"],
        },
    )
    token = reg.json()["access_token"]
    resp = await client.post(
        "/pigeons/",
        json={"name": "Test", "breed": "Taklaci"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_buyer_cannot_create_auction(client: AsyncClient):
    """Alıcı ihale başlatamaz → 403."""
    reg = await client.post(
        "/auth/register",
        json={
            "username": "buyer2",
            "email": "buyer2@test.com",
            "password": "test123",
            "roles": ["buyer"],
        },
    )
    token = reg.json()["access_token"]
    resp = await client.post(
        "/auctions/",
        json={"pigeon_id": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_seller_can_create_pigeon(client: AsyncClient):
    """Satıcı güvercin ilanı oluşturabilir → 201."""
    reg = await client.post(
        "/auth/register",
        json={
            "username": "selleruser",
            "email": "seller@test.com",
            "password": "test123",
            "roles": ["seller"],
        },
    )
    token = reg.json()["access_token"]
    resp = await client.post(
        "/pigeons/",
        json={"name": "Beyaz Guvercin", "breed": "Taklaci"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Beyaz Guvercin"
