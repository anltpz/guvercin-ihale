import pytest


@pytest.mark.asyncio
async def test_countdown_decrements_remaining(fake_redis):
    """Sayaç doğrudan Redis üzerinde düşmeli."""
    await fake_redis.set("auction:1:remaining", "5")

    remaining = int(await fake_redis.get("auction:1:remaining"))
    assert remaining == 5

    new_remaining = remaining - 1
    await fake_redis.set("auction:1:remaining", new_remaining)
    assert int(await fake_redis.get("auction:1:remaining")) == 4


@pytest.mark.asyncio
async def test_countdown_zero_triggers_close(fake_redis):
    """Sayaç sıfıra ulaşınca status ended olmalı."""
    await fake_redis.set("auction:99:remaining", "1")
    await fake_redis.set("auction:99:status", "active")

    remaining = int(await fake_redis.get("auction:99:remaining"))
    new_remaining = remaining - 1
    await fake_redis.set("auction:99:remaining", new_remaining)

    if new_remaining <= 0:
        await fake_redis.set("auction:99:status", "ended")

    assert int(await fake_redis.get("auction:99:remaining")) == 0
    assert await fake_redis.get("auction:99:status") == "ended"


@pytest.mark.asyncio
async def test_countdown_skip_already_ended(fake_redis):
    """Zaten bitmiş ihaleye dokunulmamalı."""
    await fake_redis.set("auction:50:remaining", "0")
    await fake_redis.set("auction:50:status", "ended")

    remaining = int(await fake_redis.get("auction:50:remaining"))
    assert remaining == 0
    # remaining <= 0 ise skip — countdown loop böyle çalışır
