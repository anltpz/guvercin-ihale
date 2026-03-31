"""İhale servisi — sayaç, uzatma, kapatma mantığı."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal

import redis.asyncio as aioredis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from guvercin.config import (
    AUCTION_DURATION_SECONDS,
    EXTENSION_SECONDS,
    EXTENSION_THRESHOLD,
)
from guvercin.exceptions import AuctionEndedError
from guvercin.models.auction import Auction, AuctionStatus
from guvercin.models.bid import Bid
from guvercin.services.websocket_manager import ws_manager


@dataclass
class BidResult:
    amount: Decimal
    bidder_username: str
    remaining_seconds: int
    extended: bool


async def create_auction(
    pigeon_id: int,
    seller_id: int,
    db: AsyncSession,
    redis_client: aioredis.Redis,
) -> Auction:
    """Yeni ihale oluşturur ve Redis sayacını başlatır.

    Args:
        pigeon_id: Güvercin ID'si.
        seller_id: Satıcı kullanıcı ID'si.
        db: Veritabanı oturumu.
        redis_client: Redis bağlantısı.

    Returns:
        Oluşturulan Auction nesnesi.
    """
    auction = Auction(
        pigeon_id=pigeon_id,
        seller_id=seller_id,
        status=AuctionStatus.ACTIVE.value,
        start_time=datetime.now(timezone.utc),
        duration_seconds=AUCTION_DURATION_SECONDS,
    )
    db.add(auction)
    await db.commit()
    await db.refresh(auction)

    await redis_client.set(f"auction:{auction.id}:remaining", AUCTION_DURATION_SECONDS)
    await redis_client.set(f"auction:{auction.id}:max_bid", "0")
    await redis_client.set(f"auction:{auction.id}:status", "active")

    return auction


async def extend_if_needed(
    auction_id: int,
    redis_client: aioredis.Redis,
) -> tuple[bool, int]:
    """Kalan süreyi kontrol eder, gerekirse uzatır.

    Args:
        auction_id: İhale ID'si.
        redis_client: Redis bağlantısı.

    Returns:
        (uzatıldı_mı, yeni_kalan_saniye) tuple'ı.

    Raises:
        AuctionEndedError: Süre sıfıra ulaşmışsa.
    """
    key = f"auction:{auction_id}:remaining"
    remaining = int(await redis_client.get(key) or 0)

    if remaining <= 0:
        raise AuctionEndedError(auction_id)

    extended = False
    if remaining <= EXTENSION_THRESHOLD:
        await redis_client.set(key, EXTENSION_SECONDS)
        remaining = EXTENSION_SECONDS
        extended = True

    return extended, remaining


async def get_current_max_bid(auction_id: int, db: AsyncSession) -> Decimal:
    """İhaledeki en yüksek teklifi döndürür.

    Args:
        auction_id: İhale ID'si.
        db: Veritabanı oturumu.

    Returns:
        En yüksek teklif miktarı, yoksa Decimal("0").
    """
    result = await db.execute(
        select(Bid.amount)
        .where(Bid.auction_id == auction_id)
        .order_by(Bid.amount.desc())
        .limit(1)
    )
    max_bid = result.scalar_one_or_none()
    return max_bid if max_bid is not None else Decimal("0")


async def get_winning_bid(auction_id: int, db: AsyncSession) -> Bid | None:
    """İhalenin kazanan teklifini döndürür.

    Args:
        auction_id: İhale ID'si.
        db: Veritabanı oturumu.

    Returns:
        En yüksek Bid nesnesi veya None.
    """
    result = await db.execute(
        select(Bid)
        .where(Bid.auction_id == auction_id)
        .order_by(Bid.amount.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def close_auction(
    auction_id: int,
    db: AsyncSession,
    redis_client: aioredis.Redis,
) -> None:
    """İhaleyi kapatır, kazananı belirler, WS broadcast gönderir.

    Args:
        auction_id: İhale ID'si.
        db: Veritabanı oturumu.
        redis_client: Redis bağlantısı.
    """
    auction = await db.get(Auction, auction_id)
    if auction is None or auction.status != AuctionStatus.ACTIVE.value:
        return

    winner_bid = await get_winning_bid(auction_id, db)
    auction.status = AuctionStatus.ENDED.value
    auction.winner_id = winner_bid.user_id if winner_bid else None
    await db.commit()

    await redis_client.set(f"auction:{auction_id}:status", "ended")

    # WS broadcast — ihale kapandı
    await ws_manager.broadcast(
        auction_id,
        {
            "type": "auction_ended",
            "auction_id": auction_id,
            "winner": winner_bid.user.username if winner_bid else None,
            "final_price": float(winner_bid.amount) if winner_bid else 0,
        },
    )
