import asyncio
import logging

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from guvercin.services.auction_service import close_auction

logger = logging.getLogger(__name__)


async def auction_countdown_loop(
    session_factory: async_sessionmaker[AsyncSession],
    redis_url: str,
) -> None:
    """Aktif ihalelerin sayacını her saniye düşürür, sıfıra ulaşınca kapatır.

    Args:
        session_factory: Veritabanı oturum factory'si.
        redis_url: Redis bağlantı URL'i.
    """
    redis_client = aioredis.from_url(redis_url, decode_responses=True)

    try:
        while True:
            await asyncio.sleep(1)
            try:
                keys = []
                async for key in redis_client.scan_iter("auction:*:remaining"):
                    keys.append(key)

                for key in keys:
                    remaining = int(await redis_client.get(key) or 0)
                    if remaining <= 0:
                        continue

                    new_remaining = remaining - 1
                    await redis_client.set(key, new_remaining)

                    if new_remaining <= 0:
                        auction_id = int(key.split(":")[1])
                        logger.info(
                            "İhale #%d süresi doldu, kapatılıyor.",
                            auction_id,
                        )
                        async with session_factory() as db:
                            await close_auction(auction_id, db, redis_client)
            except Exception:
                logger.exception("Countdown döngüsünde hata.")
    finally:
        await redis_client.aclose()
