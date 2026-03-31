from decimal import Decimal

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from guvercin.config import WS_ERROR_CODES
from guvercin.database import get_db, get_redis
from guvercin.exceptions import AuctionEndedError, BidTooLowError, ForbiddenBidError
from guvercin.models.auction import Auction, AuctionStatus
from guvercin.models.user import User
from guvercin.services.auction_service import create_auction
from guvercin.services.auth import decode_access_token, require_role
from guvercin.services.bid_service import place_bid
from guvercin.services.websocket_manager import WebSocketManager, get_ws_manager

router = APIRouter()


class AuctionCreate(BaseModel):
    pigeon_id: int


class AuctionResponse(BaseModel):
    id: int
    pigeon_id: int
    seller_id: int
    status: str
    duration_seconds: int
    winner_id: int | None

    model_config = {"from_attributes": True}


@router.post("/", response_model=AuctionResponse, status_code=201)
async def create_auction_endpoint(
    body: AuctionCreate,
    seller: User = Depends(require_role("seller")),
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
) -> AuctionResponse:
    """Yeni ihale başlat — sadece satıcı."""
    auction = await create_auction(
        pigeon_id=body.pigeon_id,
        seller_id=seller.id,
        db=db,
        redis_client=redis_client,
    )
    return auction


@router.get("/", response_model=list[AuctionResponse])
async def list_auctions(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> list[AuctionResponse]:
    """Aktif ihaleleri listele."""
    result = await db.execute(
        select(Auction)
        .where(Auction.status == AuctionStatus.ACTIVE.value)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


@router.get("/{auction_id}", response_model=AuctionResponse)
async def get_auction(
    auction_id: int,
    db: AsyncSession = Depends(get_db),
) -> AuctionResponse:
    """İhale detayı."""
    auction = await db.get(Auction, auction_id)
    if not auction:
        raise HTTPException(status_code=404, detail="İhale bulunamadı.")
    return auction


@router.websocket("/ws/{auction_id}")
async def auction_ws(
    auction_id: int,
    ws: WebSocket,
    manager: WebSocketManager = Depends(get_ws_manager),
    db: AsyncSession = Depends(get_db),
    redis_client: aioredis.Redis = Depends(get_redis),
) -> None:
    """Canlı ihale WebSocket endpoint'i."""
    token = ws.query_params.get("token")
    connected = await manager.connect(auction_id, ws, token)
    if not connected:
        return

    try:
        while True:
            data = await ws.receive_json()
            if data.get("type") == "bid":
                await _handle_bid(auction_id, data, ws, manager, db, redis_client)
    except WebSocketDisconnect:
        await manager.disconnect(auction_id, ws)


async def _handle_bid(
    auction_id: int,
    data: dict,
    sender_ws: WebSocket,
    manager: WebSocketManager,
    db: AsyncSession,
    redis_client: aioredis.Redis,
) -> None:
    """Gelen teklifi işler, sonucu broadcast eder veya hata döner."""
    try:
        payload = decode_access_token(data.get("token", ""))
        username = payload["sub"]

        user_result = await db.execute(select(User).where(User.username == username))
        user = user_result.scalar_one_or_none()
        if not user:
            await sender_ws.send_json(
                {
                    "type": "error",
                    "code": WS_ERROR_CODES["INVALID_TOKEN"],
                    "message": "Kullanıcı bulunamadı.",
                }
            )
            return

        result = await place_bid(
            auction_id=auction_id,
            user_id=user.id,
            amount=Decimal(str(data.get("amount", 0))),
            db=db,
            redis_client=redis_client,
            bidder_username=username,
        )

        await manager.broadcast(
            auction_id,
            {
                "type": "bid_update",
                "auction_id": auction_id,
                "amount": float(result.amount),
                "bidder": result.bidder_username,
                "remaining_seconds": result.remaining_seconds,
                "extended": result.extended,
            },
        )

    except AuctionEndedError:
        await sender_ws.send_json(
            {
                "type": "error",
                "code": WS_ERROR_CODES["AUCTION_ENDED"],
                "message": "İhale sona ermiştir.",
            }
        )
    except BidTooLowError as e:
        await sender_ws.send_json(
            {
                "type": "error",
                "code": WS_ERROR_CODES["BID_TOO_LOW"],
                "message": f"Teklifiniz çok düşük. Minimum: {e.minimum}",
            }
        )
    except ForbiddenBidError:
        await sender_ws.send_json(
            {
                "type": "error",
                "code": WS_ERROR_CODES["FORBIDDEN_BID"],
                "message": "Kendi ilanınıza teklif veremezsiniz.",
            }
        )
