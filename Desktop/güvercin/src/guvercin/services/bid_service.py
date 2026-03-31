"""Teklif servisi — place_bid iş mantığı."""

from decimal import Decimal

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from guvercin.config import MIN_BID_INCREMENT
from guvercin.exceptions import AuctionEndedError, BidTooLowError, ForbiddenBidError
from guvercin.models.auction import Auction, AuctionStatus
from guvercin.models.bid import Bid
from guvercin.services.auction_service import (
    BidResult,
    extend_if_needed,
    get_current_max_bid,
)


async def place_bid(
    auction_id: int,
    user_id: int,
    amount: Decimal,
    db: AsyncSession,
    redis_client: aioredis.Redis,
    bidder_username: str,
) -> BidResult:
    """Teklif yerleştirir — tüm kontrolleri yapar.

    Args:
        auction_id: İhale ID'si.
        user_id: Teklif veren kullanıcı ID'si.
        amount: Teklif miktarı.
        db: Veritabanı oturumu.
        redis_client: Redis bağlantısı.
        bidder_username: Teklif verenin kullanıcı adı.

    Returns:
        BidResult nesnesi.

    Raises:
        AuctionEndedError: İhale sona ermişse.
        ForbiddenBidError: Satıcı kendi ilanına teklif verirse.
        BidTooLowError: Teklif yetersizse.
    """
    auction = await db.get(Auction, auction_id)
    if auction is None or auction.status != AuctionStatus.ACTIVE.value:
        raise AuctionEndedError(auction_id)

    if auction.seller_id == user_id:
        raise ForbiddenBidError()

    current_max = await get_current_max_bid(auction_id, db)
    min_required = current_max + MIN_BID_INCREMENT
    if amount < min_required:
        raise BidTooLowError(current=current_max, minimum=min_required)

    extended, remaining = await extend_if_needed(auction_id, redis_client)

    bid = Bid(auction_id=auction_id, user_id=user_id, amount=amount)
    db.add(bid)
    await db.commit()

    await redis_client.set(f"auction:{auction_id}:max_bid", str(amount))

    return BidResult(
        amount=amount,
        bidder_username=bidder_username,
        remaining_seconds=remaining,
        extended=extended,
    )
