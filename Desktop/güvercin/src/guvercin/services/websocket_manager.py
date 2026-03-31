from fastapi import WebSocket, WebSocketDisconnect

from guvercin.services.auth import decode_access_token


class WebSocketManager:
    """WebSocket bağlantı yöneticisi — ihale başına bağlantı seti tutar."""

    def __init__(self) -> None:
        self.connections: dict[int, set[WebSocket]] = {}

    async def connect(self, auction_id: int, ws: WebSocket, token: str | None) -> bool:
        """Bağlantıyı doğrular ve kabul eder.

        JWT ÖNCE doğrulanır, geçersizse bağlantı kapatılır.
        accept() doğrulamadan ÖNCE çağrılmaz.
        """
        if not token:
            await ws.close(code=4001)
            return False

        try:
            decode_access_token(token)
        except Exception:
            await ws.close(code=4001)
            return False

        await ws.accept()
        self.connections.setdefault(auction_id, set()).add(ws)
        return True

    async def disconnect(self, auction_id: int, ws: WebSocket) -> None:
        """Bağlantıyı kaldırır."""
        self.connections.get(auction_id, set()).discard(ws)

    async def broadcast(self, auction_id: int, message: dict) -> None:
        """İhaledeki tüm bağlantılara mesaj gönderir."""
        dead: set[WebSocket] = set()
        for ws in self.connections.get(auction_id, set()):
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                dead.add(ws)
            except Exception:
                dead.add(ws)
        if dead:
            self.connections[auction_id] -= dead


ws_manager = WebSocketManager()


def get_ws_manager() -> WebSocketManager:
    """WebSocketManager dependency'si."""
    return ws_manager
