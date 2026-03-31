from unittest.mock import AsyncMock

import pytest
from fastapi import WebSocket

from guvercin.services.auth import create_access_token
from guvercin.services.websocket_manager import WebSocketManager


@pytest.mark.asyncio
async def test_ws_rejects_invalid_jwt():
    """Geçersiz token → bağlantı kodu 4001 ile kapatılmalı."""
    manager = WebSocketManager()
    ws = AsyncMock(spec=WebSocket)

    result = await manager.connect(auction_id=1, ws=ws, token="invalid-token")

    assert result is False
    ws.close.assert_called_once_with(code=4001)
    ws.accept.assert_not_called()


@pytest.mark.asyncio
async def test_ws_rejects_empty_token():
    """Token yoksa bağlantı kapatılmalı."""
    manager = WebSocketManager()
    ws = AsyncMock(spec=WebSocket)

    result = await manager.connect(auction_id=1, ws=ws, token=None)

    assert result is False
    ws.close.assert_called_once_with(code=4001)


@pytest.mark.asyncio
async def test_ws_accepts_valid_jwt():
    """Geçerli token → bağlantı kabul edilmeli."""
    manager = WebSocketManager()
    ws = AsyncMock(spec=WebSocket)
    token = create_access_token(data={"sub": "testuser"})

    result = await manager.connect(auction_id=1, ws=ws, token=token)

    assert result is True
    ws.accept.assert_called_once()
    assert ws in manager.connections[1]


@pytest.mark.asyncio
async def test_ws_broadcast_reaches_all_clients():
    """Broadcast tüm bağlı istemcilere mesaj göndermeli."""
    manager = WebSocketManager()
    ws1 = AsyncMock(spec=WebSocket)
    ws2 = AsyncMock(spec=WebSocket)

    token = create_access_token(data={"sub": "user1"})
    await manager.connect(auction_id=1, ws=ws1, token=token)

    token2 = create_access_token(data={"sub": "user2"})
    await manager.connect(auction_id=1, ws=ws2, token=token2)

    msg = {"type": "bid_update", "amount": 500}
    await manager.broadcast(1, msg)

    ws1.send_json.assert_called_once_with(msg)
    ws2.send_json.assert_called_once_with(msg)


@pytest.mark.asyncio
async def test_ws_disconnect_removes_client():
    """Disconnect sonrası istemci listeden kaldırılmalı."""
    manager = WebSocketManager()
    ws = AsyncMock(spec=WebSocket)
    token = create_access_token(data={"sub": "testuser"})

    await manager.connect(auction_id=1, ws=ws, token=token)
    assert ws in manager.connections[1]

    await manager.disconnect(auction_id=1, ws=ws)
    assert ws not in manager.connections[1]


@pytest.mark.asyncio
async def test_ws_broadcast_cleans_dead_connections():
    """Kopan bağlantı broadcast sırasında temizlenmeli."""
    from fastapi import WebSocketDisconnect

    manager = WebSocketManager()
    ws_alive = AsyncMock(spec=WebSocket)
    ws_dead = AsyncMock(spec=WebSocket)
    ws_dead.send_json.side_effect = WebSocketDisconnect()

    token = create_access_token(data={"sub": "alive"})
    await manager.connect(auction_id=1, ws=ws_alive, token=token)
    token2 = create_access_token(data={"sub": "dead"})
    await manager.connect(auction_id=1, ws=ws_dead, token=token2)

    await manager.broadcast(1, {"type": "test"})

    ws_alive.send_json.assert_called_once()
    assert ws_dead not in manager.connections[1]
    assert ws_alive in manager.connections[1]
