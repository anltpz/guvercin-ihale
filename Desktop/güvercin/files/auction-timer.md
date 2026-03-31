---
name: auction-timer
description: >
  Coder, ihale sayacı veya uzatma mantığıyla ilgili herhangi bir
  kod yazarken ya da değiştirirken bu skill'i okusun.
  UYARI: Bu kod para kaybına yol açabilir — dikkatli ol.
---

# Skill: İhale Sayacı ve Uzatma Mantığı

## Amaç
`auction_service.py` içindeki sayaç ve uzatma mantığını doğru yazmak.
Bu kod yanlışsa kullanıcı para kaybeder veya ihale erken/geç kapanır.

## Ön Koşullar
- [ ] `config.py`'de sabitler tanımlı:
  - `AUCTION_DURATION_SECONDS`
  - `EXTENSION_THRESHOLD` (10)
  - `EXTENSION_SECONDS` (10)
- [ ] Redis bağlantısı hazır (sayaç Redis'te tutulur)

## Temel Yapı

```python
# src/guvercin/services/auction_service.py

from guvercin.config import (
    EXTENSION_THRESHOLD,
    EXTENSION_SECONDS,
)

async def extend_if_needed(
    auction_id: int,
    redis: Redis,
) -> tuple[bool, int]:
    """
    Kalan süreyi kontrol eder, gerekirse uzatır.

    Args:
        auction_id: İhale ID'si
        redis: Redis bağlantısı

    Returns:
        (uzatıldı_mı: bool, yeni_kalan_saniye: int)
    """
    key = f"auction:{auction_id}:remaining"
    remaining = int(await redis.get(key) or 0)

    if remaining <= 0:
        raise AuctionEndedError(auction_id)

    extended = False
    if remaining <= EXTENSION_THRESHOLD:
        await redis.set(key, EXTENSION_SECONDS)
        remaining = EXTENSION_SECONDS
        extended = True

    return extended, remaining
```

## Teklif Yerleştirme Akışı

```python
async def place_bid(
    auction_id: int,
    user_id: int,
    amount: Decimal,
    db: AsyncSession,
    redis: Redis,
) -> BidResult:
    # 1. İhale aktif mi?
    auction = await db.get(Auction, auction_id)
    if auction.status != AuctionStatus.ACTIVE:
        raise AuctionEndedError(auction_id)

    # 2. Satıcı kendi ilanına teklif veremez
    if auction.seller_id == user_id:
        raise ForbiddenBidError("Kendi ilanınıza teklif veremezsiniz.")

    # 3. Teklif yeterince yüksek mi?
    current_max = await get_current_max_bid(auction_id, db)
    min_required = current_max + Decimal(str(MIN_BID_INCREMENT))
    if amount < min_required:
        raise BidTooLowError(current=current_max, minimum=min_required)

    # 4. Sayaç kontrolü ve uzatma
    extended, remaining = await extend_if_needed(auction_id, redis)

    # 5. Teklifi kaydet
    bid = Bid(auction_id=auction_id, user_id=user_id, amount=amount)
    db.add(bid)
    await db.commit()

    return BidResult(
        amount=amount,
        bidder_username=...,
        remaining_seconds=remaining,
        extended=extended,
    )
```

## İhale Kapatma

```python
async def close_auction(auction_id: int, db: AsyncSession, redis: Redis):
    """Redis TTL sıfırlanınca veya manuel kapatılınca çağrılır."""
    auction = await db.get(Auction, auction_id)
    if auction.status != AuctionStatus.ACTIVE:
        return  # Zaten kapanmış

    winner_bid = await get_winning_bid(auction_id, db)
    auction.status = AuctionStatus.ENDED
    auction.winner_id = winner_bid.user_id if winner_bid else None
    await db.commit()

    # Ödeme linkini tetikle
    if winner_bid:
        await payment_service.create_payment_link(
            Order(auction_id=auction_id, buyer_id=winner_bid.user_id,
                  amount=winner_bid.amount)
        )
```

## Çıktı / Beklenen Sonuç
- Kalan süre ≤ `EXTENSION_THRESHOLD` → uzatılır, `extended=True` döner
- Kalan süre > `EXTENSION_THRESHOLD` → dokunulmaz, `extended=False`
- Süre = 0 → `AuctionEndedError` fırlatılır
- Satıcı kendi ilanına teklif → `ForbiddenBidError`

## Boundary Testleri (Tester Zorunlu Yazar)

```python
# tests/test_auction_service.py — Bu testler OLMADAN PR açılamaz

@pytest.mark.parametrize("remaining,expect_extend", [
    (9,  True),   # eşiğin altı
    (10, True),   # tam eşik — uzatılmalı
    (11, False),  # eşiğin üstü
])
async def test_extend_boundary(remaining, expect_extend, mock_redis):
    mock_redis.get.return_value = str(remaining)
    extended, _ = await extend_if_needed(auction_id=1, redis=mock_redis)
    assert extended == expect_extend
```

## Gotchas

- ⚠️ `remaining <= EXTENSION_THRESHOLD` değil `< EXTENSION_THRESHOLD` yazarsan —
  tam 10 saniyede gelen teklif uzatılmaz. Eşik DAHİL olmalı (`<=`).
- ⚠️ Sayacı DB'de tutarsan — her teklif bir DB write + lock demek.
  Redis'te tut, sadece kapanışta DB'ye yaz.
- ⚠️ `close_auction` iki kez çağrılabilir (race condition) —
  `if auction.status != ACTIVE: return` guard'ı şart.
- ⚠️ `EXTENSION_THRESHOLD` ve `EXTENSION_SECONDS` hardcode yazma —
  her ikisi de `config.py`'den gelmiyor olursa Reviewer blocker verir.

## Referanslar
- `src/guvercin/services/auction_service.py`
- `config.py → EXTENSION_THRESHOLD, EXTENSION_SECONDS, MIN_BID_INCREMENT`
- `CLAUDE.md → İhale Sayacı Mantığı`
