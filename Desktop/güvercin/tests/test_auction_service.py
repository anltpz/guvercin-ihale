from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from guvercin.config import EXTENSION_SECONDS
from guvercin.exceptions import AuctionEndedError, BidTooLowError, ForbiddenBidError
from guvercin.models.auction import AuctionStatus
from guvercin.services.auction_service import close_auction, extend_if_needed
from guvercin.services.bid_service import place_bid

# ──────────────────────────────────────────
# extend_if_needed — ZORUNLU boundary testleri
# ──────────────────────────────────────────


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "remaining,expect_extend",
    [
        (9, True),  # eşiğin altı → uzatılmalı
        (10, True),  # tam eşik → uzatılmalı (<=)
        (11, False),  # eşiğin üstü → uzatılmamalı
    ],
)
async def test_extend_boundary(remaining: int, expect_extend: bool):
    """Boundary: 9sn/10sn/11sn'de uzatma davranışı."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value=str(remaining))
    mock_redis.set = AsyncMock()

    extended, new_remaining = await extend_if_needed(
        auction_id=1, redis_client=mock_redis
    )
    assert extended == expect_extend

    if expect_extend:
        assert new_remaining == EXTENSION_SECONDS
        mock_redis.set.assert_called_once()
    else:
        assert new_remaining == remaining
        mock_redis.set.assert_not_called()


@pytest.mark.asyncio
async def test_extend_after_extend():
    """Uzatma sonrası tekrar uzatma çalışmalı."""
    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock()

    # İlk uzatma — 5 saniye kaldı
    mock_redis.get = AsyncMock(return_value="5")
    extended1, _ = await extend_if_needed(auction_id=1, redis_client=mock_redis)
    assert extended1 is True

    # İkinci uzatma — yine 5 saniye kaldı
    mock_redis.get = AsyncMock(return_value="5")
    extended2, _ = await extend_if_needed(auction_id=1, redis_client=mock_redis)
    assert extended2 is True


@pytest.mark.asyncio
async def test_bid_after_auction_ended():
    """Süre bittikten sonra teklif → AuctionEndedError."""
    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value="0")

    with pytest.raises(AuctionEndedError):
        await extend_if_needed(auction_id=1, redis_client=mock_redis)


# ──────────────────────────────────────────
# place_bid testleri
# ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_seller_cannot_bid_own_auction(db, seller, auction, fake_redis):
    """Satıcı kendi ilanına teklif veremez."""
    with pytest.raises(ForbiddenBidError):
        await place_bid(
            auction_id=auction.id,
            user_id=seller.id,
            amount=Decimal("500"),
            db=db,
            redis_client=fake_redis,
            bidder_username=seller.username,
        )


@pytest.mark.asyncio
async def test_bid_too_low(db, seller, buyer, auction, fake_redis):
    """Düşük teklif → BidTooLowError."""
    # Önce geçerli teklif ver
    await place_bid(
        auction_id=auction.id,
        user_id=buyer.id,
        amount=Decimal("500"),
        db=db,
        redis_client=fake_redis,
        bidder_username=buyer.username,
    )

    # Şimdi düşük teklif
    with pytest.raises(BidTooLowError):
        await place_bid(
            auction_id=auction.id,
            user_id=buyer.id,
            amount=Decimal("510"),  # min_increment=50, gerekli 550
            db=db,
            redis_client=fake_redis,
            bidder_username=buyer.username,
        )


@pytest.mark.asyncio
async def test_place_bid_success(db, seller, buyer, auction, fake_redis):
    """Başarılı teklif — BidResult döner."""
    result = await place_bid(
        auction_id=auction.id,
        user_id=buyer.id,
        amount=Decimal("500"),
        db=db,
        redis_client=fake_redis,
        bidder_username=buyer.username,
    )
    assert result.amount == Decimal("500")
    assert result.bidder_username == buyer.username
    assert result.remaining_seconds > 0


@pytest.mark.asyncio
async def test_close_auction_sets_winner(db, seller, buyer, auction, fake_redis):
    """İhale kapatılınca kazanan belirlenir."""
    await place_bid(
        auction_id=auction.id,
        user_id=buyer.id,
        amount=Decimal("500"),
        db=db,
        redis_client=fake_redis,
        bidder_username=buyer.username,
    )

    await close_auction(auction.id, db, fake_redis)
    await db.refresh(auction)

    assert auction.status == AuctionStatus.ENDED.value
    assert auction.winner_id == buyer.id


@pytest.mark.asyncio
async def test_close_auction_idempotent(db, seller, auction, fake_redis):
    """İhaleyi iki kez kapatma hata vermez."""
    await close_auction(auction.id, db, fake_redis)
    await close_auction(auction.id, db, fake_redis)  # İkinci çağrı sessizce döner
