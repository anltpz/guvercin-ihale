from decimal import Decimal

import pytest

from guvercin.services.payment_service import (
    Order,
    PaymentResult,
    StubPaymentProvider,
)


@pytest.fixture
def stub_provider():
    return StubPaymentProvider()


@pytest.fixture
def test_order():
    return Order(id=1, auction_id=10, buyer_id=5, amount=Decimal("1500"))


@pytest.mark.asyncio
async def test_stub_creates_payment_link(stub_provider, test_order):
    """StubPaymentProvider ödeme linki oluşturur."""
    link = await stub_provider.create_payment_link(test_order)
    assert "/mock-payment/1" in link
    assert "1500" in link


@pytest.mark.asyncio
async def test_stub_verify_webhook(stub_provider):
    """Webhook doğrulama başarılı döner."""
    result = await stub_provider.verify_webhook({"order_id": 42})
    assert isinstance(result, PaymentResult)
    assert result.success is True
    assert "42" in result.payment_id


@pytest.mark.asyncio
async def test_stub_refund(stub_provider):
    """İade başarılı döner."""
    success = await stub_provider.refund("payment_123")
    assert success is True
