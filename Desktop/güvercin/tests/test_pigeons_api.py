import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_pigeons_empty(client: AsyncClient):
    """Boş güvercin listesi 200 dönmeli."""
    resp = await client.get("/pigeons/")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_pigeon_not_found(client: AsyncClient):
    """Var olmayan güvercin 404 dönmeli."""
    resp = await client.get("/pigeons/999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_and_get_pigeon(client: AsyncClient):
    """Satıcı güvercin oluşturup detay alabilmeli."""
    reg = await client.post(
        "/auth/register",
        json={
            "username": "pigeonseller",
            "email": "pigeonseller@test.com",
            "password": "test123",
            "roles": ["seller"],
        },
    )
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/pigeons/",
        json={"name": "Ak Guvercin", "breed": "Donek"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    pigeon_id = create_resp.json()["id"]

    get_resp = await client.get(f"/pigeons/{pigeon_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Ak Guvercin"


@pytest.mark.asyncio
async def test_update_pigeon_owner_only(client: AsyncClient):
    """Başkasının güvercini güncellenemez."""
    reg1 = await client.post(
        "/auth/register",
        json={
            "username": "seller_a",
            "email": "a@test.com",
            "password": "test123",
            "roles": ["seller"],
        },
    )
    token1 = reg1.json()["access_token"]

    create_resp = await client.post(
        "/pigeons/",
        json={"name": "Test", "breed": "Test"},
        headers={"Authorization": f"Bearer {token1}"},
    )
    pigeon_id = create_resp.json()["id"]

    reg2 = await client.post(
        "/auth/register",
        json={
            "username": "seller_b",
            "email": "b@test.com",
            "password": "test123",
            "roles": ["seller"],
        },
    )
    token2 = reg2.json()["access_token"]

    resp = await client.put(
        f"/pigeons/{pigeon_id}",
        json={"name": "Hack", "breed": "Hack"},
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert resp.status_code == 403
