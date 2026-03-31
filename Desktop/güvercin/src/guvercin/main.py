import asyncio
import pathlib
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from guvercin.config import settings
from guvercin.database import async_session
from guvercin.exceptions import (
    AuctionEndedError,
    BidTooLowError,
    ForbiddenBidError,
    InvalidTokenError,
)
from guvercin.routers import auctions, auth, payments, pigeons
from guvercin.routers import pages as pages_router
from guvercin.services.countdown import auction_countdown_loop

BASE_DIR = pathlib.Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlatma ve kapatma — background task'ları yönetir."""
    task = asyncio.create_task(
        auction_countdown_loop(async_session, settings.REDIS_URL)
    )
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="GüvercinIhale",
    description="Güvercin online ihale platformu",
    version="0.1.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API router'ları
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(pigeons.router, prefix="/pigeons", tags=["pigeons"])
app.include_router(auctions.router, prefix="/auctions", tags=["auctions"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])

# Sayfa router'ı
app.include_router(pages_router.router)


@app.exception_handler(AuctionEndedError)
async def auction_ended_handler(
    request: Request, exc: AuctionEndedError
) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(BidTooLowError)
async def bid_too_low_handler(request: Request, exc: BidTooLowError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(ForbiddenBidError)
async def forbidden_bid_handler(
    request: Request, exc: ForbiddenBidError
) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": exc.message})


@app.exception_handler(InvalidTokenError)
async def invalid_token_handler(
    request: Request, exc: InvalidTokenError
) -> JSONResponse:
    return JSONResponse(status_code=401, content={"detail": exc.detail})
