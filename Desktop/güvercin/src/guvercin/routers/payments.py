from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from guvercin.services.payment_service import (
    Order,
    PaymentProvider,
    PaymentResult,
    get_payment_provider,
)

router = APIRouter()


class PaymentCreateRequest(BaseModel):
    order_id: int
    auction_id: int
    buyer_id: int
    amount: float


class PaymentCreateResponse(BaseModel):
    payment_url: str


class WebhookRequest(BaseModel):
    order_id: int
    status: str
    provider_data: dict = {}


class RefundRequest(BaseModel):
    payment_id: str


class RefundResponse(BaseModel):
    success: bool


@router.post("/create", response_model=PaymentCreateResponse)
async def create_payment(
    body: PaymentCreateRequest,
    provider: PaymentProvider = Depends(get_payment_provider),
) -> PaymentCreateResponse:
    """Ödeme linki oluştur — PaymentProvider DI ile."""
    order = Order(
        id=body.order_id,
        auction_id=body.auction_id,
        buyer_id=body.buyer_id,
        amount=Decimal(str(body.amount)),
    )
    link = await provider.create_payment_link(order)
    return PaymentCreateResponse(payment_url=link)


@router.post("/webhook")
async def payment_webhook(
    body: WebhookRequest,
    provider: PaymentProvider = Depends(get_payment_provider),
) -> PaymentResult:
    """Ödeme sağlayıcı webhook'u — doğrulama PaymentProvider ile."""
    return await provider.verify_webhook(body.model_dump())


@router.post("/refund", response_model=RefundResponse)
async def refund_payment(
    body: RefundRequest,
    provider: PaymentProvider = Depends(get_payment_provider),
) -> RefundResponse:
    """İade işlemi — PaymentProvider DI ile."""
    success = await provider.refund(body.payment_id)
    return RefundResponse(success=success)
