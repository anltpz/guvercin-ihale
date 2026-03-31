import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_home_page(client: AsyncClient):
    """Ana sayfa 200 dönmeli."""
    resp = await client.get("/")
    assert resp.status_code == 200
    assert "GüvercinIhale" in resp.text


@pytest.mark.asyncio
async def test_login_page(client: AsyncClient):
    """Giriş sayfası 200 dönmeli."""
    resp = await client.get("/giris")
    assert resp.status_code == 200
    assert "Giriş" in resp.text


@pytest.mark.asyncio
async def test_register_page(client: AsyncClient):
    """Kayıt sayfası 200 dönmeli."""
    resp = await client.get("/kayit")
    assert resp.status_code == 200
    assert "Kayıt" in resp.text


@pytest.mark.asyncio
async def test_pigeons_page(client: AsyncClient):
    """İlanlar sayfası 200 dönmeli."""
    resp = await client.get("/ilanlar")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_auctions_page(client: AsyncClient):
    """İhaleler sayfası 200 dönmeli."""
    resp = await client.get("/ihaleler")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_pigeon_create_page(client: AsyncClient):
    """İlan ekleme sayfası 200 dönmeli."""
    resp = await client.get("/ilan-ekle")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_auction_detail_page(client: AsyncClient):
    """İhale detay sayfası 200 dönmeli."""
    resp = await client.get("/ihale/1")
    assert resp.status_code == 200
