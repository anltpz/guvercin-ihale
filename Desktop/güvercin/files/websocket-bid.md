---
name: websocket-bid
description: >
  Coder, WebSocket endpoint'i veya teklif (bid) mantığıyla ilgili
  herhangi bir kod yazarken bu skill'i okusun.
---

# Skill: WebSocket Teklif Sistemi

## Amaç
Coder, WS bağlantı yönetimi ve teklif işleme kodu yazarken bu adımları izler.

## Ön Koşullar
- [ ] `websocket_manager.py` mevcut veya oluşturulacak
- [ ] `auction_service.py` sayaç mantığı hazır
- [ ] JWT auth middleware kurulu

## Adımlar

### 1. Bağlantı Yönetimi
`WebSocketManager` singleton olmalı — her auction için ayrı `Set[WebSocket]`:

```python
class WebSocketManager:
    def __init__(self):
        self.connections: dict[int, set[WebSocket]] = {}

    async def connect(self, auction_id: int, ws: WebSocket, token: str):
        # JWT doğrula — geçersizse KAPAT
        payload = verify_jwt(token)
        if not payload:
            await ws.close(code=4001)
            return False
        await ws.accept()
        self.connections.setdefault(auction_id, set()).add(ws)
        return True

    async def disconnect(self, auction_id: int, ws: WebSocket):
        self.connections.get(auction_id, set()).discard(ws)

    async def broadcast(self, auction_id: int, message: dict):
        dead = set()
        for ws in self.connections.get(auction_id, set()):
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                dead.add(ws)
        self.connections[auction_id] -= dead
```

### 2. Teklif Endpoint'i

```python
@router.websocket("/ws/auction/{auction_id}")
async def auction_ws(
    auction_id: int,
    ws: WebSocket,
    manager: WebSocketManager = Depends(get_ws_manager),
):
    connected = await manager.connect(auction_id, ws, token=ws.query_params.get("token"))
    if not connected:
        return

    try:
        while True:
            data = await ws.receive_json()
            if data.get("type") == "bid":
                await handle_bid(auction_id, data, ws, manager)
    except WebSocketDisconnect:
        await manager.disconnect(auction_id, ws)
```

### 3. Teklif İşleme

```python
async def handle_bid(auction_id, data, sender_ws, manager):
    try:
        result = await bid_service.place_bid(
            auction_id=auction_id,
            user_id=data["user_id"],
            amount=data["amount"],
        )
        # Başarılı → herkese broadcast
        await manager.broadcast(auction_id, {
            "type": "bid_update",
            "auction_id": auction_id,
            "amount": result.amount,
            "bidder": result.bidder_username,
            "remaining_seconds": result.remaining_seconds,
            "extended": result.extended,
        })
    except AuctionEndedError:
        await sender_ws.send_json({
            "type": "error",
            "code": WS_ERROR_CODES["AUCTION_ENDED"],
            "message": "İhale sona ermiştir.",
        })
    except BidTooLowError:
        await sender_ws.send_json({
            "type": "error",
            "code": WS_ERROR_CODES["BID_TOO_LOW"],
            "message": "Teklifiniz mevcut en yüksek tekliften düşük.",
        })
```

## Çıktı / Beklenen Sonuç
- Geçersiz JWT → bağlantı kodu 4001 ile kapatılıyor
- Geçerli teklif → tüm bağlı istemcilere broadcast
- Hata → sadece gönderen istemciye, broadcast YOK
- Bağlantı kopunca `connections` setinden temizleniyor

## Gotchas

- ⚠️ `await ws.accept()` JWT doğrulamadan önce çağrılırsa — bağlantı
  doğrulanmadan açılır, güvenlik açığı. ÖNCE doğrula, SONRA accept et.
- ⚠️ Broadcast sırasında kopan bağlantı `WebSocketDisconnect` fırlatır —
  try/except olmadan tüm broadcast durur. Dead connection temizleme şart.
- ⚠️ `connections` dict'i singleton değilse — her restart'ta bağlantılar kaybolur.
  FastAPI lifespan event'e bağla.
- ⚠️ Hata mesajını broadcast etme — sadece ilgili client'a gönder.

## Referanslar
- `src/guvercin/services/websocket_manager.py`
- `src/guvercin/services/bid_service.py`
- `config.py → WS_ERROR_CODES`
