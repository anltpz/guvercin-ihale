import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from guvercin.database import get_db, get_redis
from guvercin.models import Base
from guvercin.models.auction import Auction
from guvercin.models.pigeon import Pigeon
from guvercin.models.user import User
from guvercin.services.auth import create_access_token, hash_password

# Test DB — SQLite async
TEST_DB_URL = "sqlite+aiosqlite:///./test.db"
test_engine = create_async_engine(TEST_DB_URL, echo=False)
test_session = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_db():
    """Her test öncesi tabloları oluştur, sonra temizle."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session() as session:
        yield session


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    async with test_session() as session:
        yield session


@pytest.fixture
async def fake_redis():
    """FakeRedis instance — gerçek Redis gerektirmez."""
    import fakeredis.aioredis

    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield client
    await client.aclose()


@pytest.fixture
async def client(fake_redis) -> AsyncGenerator[AsyncClient, None]:
    """Test HTTP istemcisi — DB ve Redis override'lı."""
    from guvercin.main import app

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = lambda: fake_redis

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture
async def seller(db: AsyncSession) -> User:
    """Test satıcı kullanıcısı."""
    user = User(
        username="seller_test",
        email="seller@test.com",
        hashed_password=hash_password("test123"),
        roles=["seller"],
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def buyer(db: AsyncSession) -> User:
    """Test alıcı kullanıcısı."""
    user = User(
        username="buyer_test",
        email="buyer@test.com",
        hashed_password=hash_password("test123"),
        roles=["buyer"],
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def pigeon(db: AsyncSession, seller: User) -> Pigeon:
    """Test güvercin ilanı."""
    p = Pigeon(
        seller_id=seller.id,
        name="Test Güvercin",
        breed="Taklacı",
    )
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@pytest.fixture
async def auction(
    db: AsyncSession, pigeon: Pigeon, seller: User, fake_redis
) -> Auction:
    """Test ihalesi — Redis sayacı da hazır."""
    from guvercin.services.auction_service import create_auction

    return await create_auction(
        pigeon_id=pigeon.id,
        seller_id=seller.id,
        db=db,
        redis_client=fake_redis,
    )


def auth_headers(user: User) -> dict[str, str]:
    """JWT ile Authorization header oluşturur."""
    token = create_access_token(data={"sub": user.username})
    return {"Authorization": f"Bearer {token}"}
