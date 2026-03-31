import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_auctions_empty(client: AsyncClient):
    """Boş ihale listesi 200 dönmeli."""
    resp = await client.get("/auctions/")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_auction_not_found(client: AsyncClient):
    """Var olmayan ihale 404 dönmeli."""
    resp = await client.get("/auctions/999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_auction_as_seller(client: AsyncClient):
    """Satıcı ihale oluşturabilmeli."""
    reg = await client.post(
        "/auth/register",
        json={
            "username": "auctionseller",
            "email": "auctionseller@test.com",
            "password": "test123",
            "roles": ["seller"],
        },
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    pigeon = await client.post(
        "/pigeons/",
        json={"name": "Ihale Guvercini", "breed": "Oynak"},
        headers=headers,
    )
    pigeon_id = pigeon.json()["id"]

    resp = await client.post(
        "/auctions/",
        json={"pigeon_id": pigeon_id},
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["status"] == "active"
    assert resp.json()["pigeon_id"] == pigeon_id
