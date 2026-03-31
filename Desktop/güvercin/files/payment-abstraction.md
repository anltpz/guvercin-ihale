---
name: payment-abstraction
description: >
  Coder, ödeme ile ilgili herhangi bir kod yazarken bu skill'i okusun.
  Sağlayıcı henüz seçilmedi — interface dışına çıkma.
---

# Skill: Ödeme Soyutlama Katmanı

## Amaç
Ödeme sağlayıcısı henüz seçilmedi (Iyzico / PayTR / Stripe adaylar).
Bu skill, Coder'ın sağlayıcıdan bağımsız, değiştirilebilir bir yapı kurmasını sağlar.

## Ön Koşullar
- [ ] `payment_service.py` mevcut veya oluşturulacak
- [ ] `Order` modeli tanımlı

## Interface Tanımı

```python
# src/guvercin/services/payment_service.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal

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
```

## Geliştirme/Test Stub'ı

```python
class StubPaymentProvider(PaymentProvider):
    """Test ve geliştirme ortamı için — gerçek para hareketi yok."""

    async def create_payment_link(self, order: Order) -> str:
        return f"/mock-payment/{order.id}?amount={order.amount}"

    async def verify_webhook(self, payload: dict) -> PaymentResult:
        return PaymentResult(success=True, payment_id=f"stub_{payload.get('order_id')}")

    async def refund(self, payment_id: str) -> bool:
        return True
```

## Dependency Injection

```python
# src/guvercin/main.py — lifespan'de provider'ı seç
from guvercin.services.payment_service import StubPaymentProvider

def get_payment_provider() -> PaymentProvider:
    provider_name = settings.PAYMENT_PROVIDER  # config'den
    if provider_name == "stub":
        return StubPaymentProvider()
    # İleride: elif provider_name == "iyzico": return IyzicoAdapter()
    raise ValueError(f"Bilinmeyen ödeme sağlayıcısı: {provider_name}")

# Router'da kullanım
@router.post("/payments/complete")
async def complete_payment(
    order_id: int,
    payment_provider: PaymentProvider = Depends(get_payment_provider),
):
    link = await payment_provider.create_payment_link(order)
    return {"payment_url": link}
```

## Sağlayıcı Geldiğinde (Gelecekte)

Yeni sağlayıcı eklemek için sadece adapter yaz:

```python
# src/guvercin/services/adapters/iyzico_adapter.py
class IyzicoAdapter(PaymentProvider):
    async def create_payment_link(self, order: Order) -> str:
        # Iyzico SDK çağrısı
        ...
```

Router'a dokunma. `config.py → PAYMENT_PROVIDER = "iyzico"` yap, bitti.

## Çıktı / Beklenen Sonuç
- Router `PaymentProvider` interface'ini dependency olarak alıyor
- Test ortamında `StubPaymentProvider` inject ediliyor
- `config.py → PAYMENT_PROVIDER` değişkeni var
- Hiçbir router doğrudan SDK çağrısı yapmıyor

## Gotchas

- ⚠️ `import iyzipay` veya `import stripe` doğrudan router'a yazma —
  adapter katmanı olmadan sağlayıcı değişince tüm router yeniden yazılır.
- ⚠️ `StubPaymentProvider`'ı production'a sürükleme —
  `config.py → PAYMENT_PROVIDER` .env'den gelmeli, default "stub" olmamalı.
- ⚠️ Webhook doğrulamasını atla deme —
  `verify_webhook` olmadan sahte ödeme onayı gönderilebilir.

## Referanslar
- `src/guvercin/services/payment_service.py`
- `config.py → PAYMENT_PROVIDER`
- `src/guvercin/routers/payments.py`
