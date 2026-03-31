from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

from guvercin.config import settings


@dataclass
class Order:
    id: int
    auction_id: int
    buyer_id: int
    amount: Decimal


@dataclass
class PaymentResult:
    success: bool
    payment_id: str | None
    error: str | None = None


class PaymentProvider(ABC):
    """Ödeme sağlayıcı interface'i — tüm sağlayıcılar bunu uygular."""

    @abstractmethod
    async def create_payment_link(self, order: Order) -> str:
        """Ödeme linki oluştur, URL döndür."""
        ...

    @abstractmethod
    async def verify_webhook(self, payload: dict) -> PaymentResult:
        """Sağlayıcıdan gelen webhook'u doğrula."""
        ...

    @abstractmethod
    async def refund(self, payment_id: str) -> bool:
        """İade işlemi başlat."""
        ...


class StubPaymentProvider(PaymentProvider):
    """Test ve geliştirme ortamı için — gerçek para hareketi yok."""

    async def create_payment_link(self, order: Order) -> str:
        return f"/mock-payment/{order.id}?amount={order.amount}"

    async def verify_webhook(self, payload: dict) -> PaymentResult:
        return PaymentResult(success=True, payment_id=f"stub_{payload.get('order_id')}")

    async def refund(self, payment_id: str) -> bool:
        return True


def get_payment_provider() -> PaymentProvider:
    """Config'e göre ödeme sağlayıcısı döndürür."""
    provider_name = settings.PAYMENT_PROVIDER
    if provider_name == "stub":
        return StubPaymentProvider()
    raise ValueError(f"Bilinmeyen ödeme sağlayıcısı: {provider_name}")
