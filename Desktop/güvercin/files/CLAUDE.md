# CLAUDE.md — GüvercinIhale

## Proje Özeti

**GüvercinIhale** — güvercin satıcılarının ilanlarını listeleyebildiği,
alıcıların sayaçlı canlı teklifler verebildiği bir online ihale platformu.

**Stack:**
- Backend : Python 3.11 · FastAPI · SQLAlchemy (async) · PostgreSQL
- Realtime : WebSocket (FastAPI native) · Redis (sayaç + broadcast)
- Auth     : JWT (python-jose) · bcrypt
- Ödeme    : Soyutlama katmanı — sağlayıcı sonra seçilecek (Iyzico / PayTR / Stripe)
- Frontend : Jinja2 + HTMX + Alpine.js
- Test     : pytest · pytest-asyncio · httpx

**Repo yapısı:**
```
guvercin-ihale/
├── CLAUDE.md
├── KNOWN_BUGS.md
├── .claude/
│   ├── agents/          # planner · coder · reviewer · tester · observer
│   ├── commands/        # /report-bug · /suggest
│   ├── skills/          # websocket-bid · auction-timer · payment-abstraction
│   └── agent-memory/
│       └── DEVELOPER_PROFILE.md
├── plans/
│   └── bugs/
├── src/
│   └── guvercin/
│       ├── main.py
│       ├── config.py            # Tüm sabitler
│       ├── database.py          # Async engine + session
│       ├── models/
│       │   ├── user.py
│       │   ├── pigeon.py        # Güvercin ilanı
│       │   ├── auction.py       # İhale + sayaç
│       │   └── bid.py
│       ├── routers/
│       │   ├── auth.py
│       │   ├── pigeons.py
│       │   ├── auctions.py
│       │   └── payments.py
│       ├── services/
│       │   ├── auction_service.py    # Sayaç + uzatma mantığı
│       │   ├── bid_service.py
│       │   ├── payment_service.py   # Ödeme interface + stub
│       │   └── websocket_manager.py
│       └── templates/
├── tests/
├── alembic/
└── .github/workflows/
```

---

## Mission Critical Rules

1. **Pipeline atlanamaz.** Her özellik:
   `Planner → Coder → Reviewer → Tester → PR`

2. **Plan dosyası zorunlu.** Kod yazmadan önce
   `plans/YYYYMMDD-<özellik>-plan.md` var olmalı.

3. **İhale sayacı dokunulmazı.**
   `auction_service.py → extend_if_needed()` fonksiyonu ve
   `EXTENSION_SECONDS` / `EXTENSION_THRESHOLD` sabitleri Reviewer onayı
   olmadan değiştirilemez. Bu mantık para kaybına yol açar.

4. **Ödeme soyutlaması kırılmaz.**
   Hiçbir router `PaymentProvider` interface'ini bypass etmez.
   Sağlayıcı gelince sadece adapter yazılır, router dokunulmaz.

5. **WebSocket her zaman kimlik doğrular.**
   JWT geçersizse bağlantı anında kapatılır, mesaj işlenmez.

6. **Sabitler config'de.**
   Süre, eşik, tutar, kod — hepsi `config.py`. Hardcode yasak.

7. **Context hijyeni.**
   Agent'lar arası büyük veri `plans/` dosyaları üzerinden akar,
   inline paste değil.

---

## Kullanıcı Rolleri

| Rol | Yapabilir | Yapamaz |
|-----|-----------|---------|
| **Satıcı** | Güvercin ekle/düzenle/sil · İhale başlat · Kazananı onayla | Kendi ilanına teklif ver |
| **Alıcı** | Aktif ihalelere teklif ver · Ödeme yap · Geçmişi gör | İlan açamaz |

> Bir kullanıcı her iki rolü de taşıyabilir.
> `user.roles` → JSON array: `["seller"]` · `["buyer"]` · `["seller","buyer"]`

---

## İhale Sayacı Mantığı (KRİTİK)

```
İhale başlar
    ↓
Süre akar (AUCTION_DURATION_SECONDS — config)
    ↓
Yeni teklif gelir
    ├── kalan < EXTENSION_THRESHOLD (10 sn)?
    │       EVET → süreyi EXTENSION_SECONDS (10 sn) uzat
    │               → WS broadcast: { extended: true, remaining: 10 }
    │       HAYIR → dokunma
    ↓
Süre = 0
    → Kazanan = en yüksek teklif sahibi
    → Satıcıya bildirim
    → Alıcıya ödeme linki
    → Geç gelen teklifler REDDEDİLİR (auction.status == "ended")
```

**`extend_if_needed()` için Tester ZORUNLU boundary testleri yazar:**
- Tam eşikte teklif: 9.9 sn / 10.0 sn / 10.1 sn
- Uzatma sonrası tekrar uzatma
- Süre bittikten sonra gelen teklif → `AuctionEndedError`

---

## WebSocket Mesaj Protokolü

```jsonc
// Client → Server (teklif ver)
{ "type": "bid", "auction_id": 42, "amount": 1500, "token": "JWT..." }

// Server → Tüm izleyiciler (yeni teklif broadcast)
{ "type": "bid_update", "auction_id": 42, "amount": 1500,
  "bidder": "ali_k", "remaining_seconds": 47, "extended": true }

// Server → Tüm izleyiciler (ihale kapandı)
{ "type": "auction_ended", "auction_id": 42,
  "winner": "ali_k", "final_price": 1500 }

// Server → İlgili client (hata)
{ "type": "error", "code": "BID_TOO_LOW",
  "message": "Teklifiniz mevcut en yüksek tekliften düşük." }
```

Hata kodları: `config.py → WS_ERROR_CODES`

---

## Ödeme Soyutlama Katmanı

Sağlayıcı henüz seçilmedi. Coder bu interface'i uygular:

```python
# src/guvercin/services/payment_service.py
class PaymentProvider(ABC):
    async def create_payment_link(self, order: Order) -> str: ...
    async def verify_webhook(self, payload: dict) -> PaymentResult: ...
    async def refund(self, payment_id: str) -> bool: ...

# Geliştirme & test için stub
class StubPaymentProvider(PaymentProvider):
    async def create_payment_link(self, order: Order) -> str:
        return f"/mock-payment/{order.id}"
```

Router'lar dependency injection ile `PaymentProvider` alır,
asla doğrudan sağlayıcıya bağlanmaz.

---

## Sub-Agent Routing

| Görev | Agent |
|-------|-------|
| Yeni özellik planla | `@agent-planner` |
| Kod yaz / değiştir | `@agent-coder` |
| Kod incele | `@agent-reviewer` |
| Test yaz / çalıştır | `@agent-tester` |
| Oturum özeti / fikir | `@agent-observer` |

**Paralel dispatch** — tüm koşullar sağlanmalı:
- 3+ bağımsız görev, paylaşılan state yok
- Dosya sınırları net, çakışma riski yok

**Sıralı dispatch** — biri bile yeterliyse:
- B görevi A'nın çıktısına bağlı
- Aynı dosyayı değiştiriyorlar
- Kapsam belirsiz

---

## Coding Standards

| Kural | Detay |
|-------|-------|
| Dil | Python 3.11+ |
| Async | Tüm I/O'da `async/await` |
| Format | `black` (88 karakter) |
| Lint | `ruff` |
| Type | Tüm public fonksiyonlarda zorunlu |
| Docstring | Google style |
| Imports | stdlib → third-party → local |
| Secrets | `.env` + `python-dotenv`, hardcode yasak |
| Sabitler | `config.py`, BÜYÜK_HARF_SNAKE_CASE |

---

## Skills

| Skill | Kim okur | Ne zaman |
|-------|----------|----------|
| `websocket-bid.md` | Coder | WS endpoint / bid mantığı yazarken |
| `auction-timer.md` | Coder | Sayaç / uzatma kodu yazarken |
| `payment-abstraction.md` | Coder | Ödeme ile ilgili herhangi bir kod yazarken |

Yeni skill eklemek için `SKILL_TEMPLATE.md`'yi kopyala.
`description` alanını tetikleyici gibi yaz — özet değil, koşul.

---

## GitHub Workflow

```
main
 └── feat/<slug>          ← Planner açar
      └── [Coder commit'leri]
           └── PR          ← Tester açar (coverage ≥ 80%, CI yeşil)
```

- PR başlığı: `feat: <kısa açıklama>`
- PR gövdesi: Özet · Plan linki · Coverage % · Reviewer onayı

---

## Definition of Done

- [ ] `plans/` altında plan dosyası var
- [ ] `ruff` + `black --check` geçiyor
- [ ] Tüm public fonksiyonlarda type hint + docstring
- [ ] `pytest` geçiyor, coverage ≥ 80%
- [ ] İhale sayacı boundary testleri yazılmış (değişiklik varsa)
- [ ] WebSocket mesajları protokole uygun
- [ ] Ödeme katmanı interface dışına çıkmıyor
- [ ] Reviewer `✅ APPROVED` vermiş
- [ ] PR açılmış, CI yeşil

---

## Hata Sınıfları

Tüm custom exception'lar `src/guvercin/exceptions.py` içinde tanımlanır:

| Exception | Nerede fırlatılır | HTTP / WS Kodu |
|-----------|-------------------|----------------|
| `AuctionEndedError` | `auction_service.py` — süre bitmiş ihaleye teklif | 400 / `AUCTION_ENDED` |
| `BidTooLowError` | `auction_service.py` — teklif yetersiz | 400 / `BID_TOO_LOW` |
| `ForbiddenBidError` | `auction_service.py` — satıcı kendi ilanına teklif | 403 / `FORBIDDEN_BID` |
| `InvalidTokenError` | JWT doğrulama — geçersiz/süresi dolmuş token | 401 / WS close 4001 |

---

## WS Hata Kodları

`config.py → WS_ERROR_CODES` dict'inden gelir:

```python
WS_ERROR_CODES = {
    "BID_TOO_LOW": "BID_TOO_LOW",
    "AUCTION_ENDED": "AUCTION_ENDED",
    "FORBIDDEN_BID": "FORBIDDEN_BID",
    "INVALID_TOKEN": "INVALID_TOKEN",
    "INVALID_MESSAGE": "INVALID_MESSAGE",
}
```

---

## Redis Key Convention

Tüm key'ler `auction:` prefix'i ile başlar:

| Key | Tip | Açıklama |
|-----|-----|----------|
| `auction:{id}:remaining` | `int` | Kalan saniye (sayaç) |
| `auction:{id}:max_bid` | `string(Decimal)` | Anlık en yüksek teklif (cache) |
| `auction:{id}:status` | `string` | `active` / `ended` |

TTL: `auction:{id}:remaining` key'ine `AUCTION_DURATION_SECONDS` kadar TTL atanır. TTL sıfırlanınca `close_auction` tetiklenir.

---

## Environment Değişkenleri

`.env` dosyasından `python-dotenv` ile yüklenir. Zorunlu olanlar `*` ile işaretli:

```
DATABASE_URL=*          # postgresql+asyncpg://user:pass@host:5432/guvercin
REDIS_URL=*             # redis://localhost:6379/0
SECRET_KEY=*            # JWT signing key
PAYMENT_PROVIDER=stub   # stub | iyzico | paytr | stripe
CORS_ORIGINS=*          # http://localhost:8000
```

---

## Geliştirme Ortamı

```bash
# Bağımlılıklar
pip install -e ".[dev]"

# Redis başlat (Docker)
docker run -d --name guvercin-redis -p 6379:6379 redis:7-alpine

# PostgreSQL (Docker)
docker run -d --name guvercin-db -p 5432:5432 \
  -e POSTGRES_DB=guvercin -e POSTGRES_PASSWORD=dev \
  postgres:16-alpine

# Migration
alembic upgrade head                    # Tüm migration'ları uygula
alembic revision --autogenerate -m ""   # Yeni migration oluştur

# Sunucuyu başlat
uvicorn guvercin.main:app --reload --port 8000

# Lint + format + test
ruff check .
black --check .
pytest --cov=src/guvercin --cov-report=term-missing --cov-fail-under=80
```

---

## SQLAlchemy Model Referansı

| Model | Tablo | Kritik Alanlar |
|-------|-------|----------------|
| `User` | `users` | `id`, `username`, `email`, `hashed_password`, `roles: JSON` (`["seller"]`, `["buyer"]`, `["seller","buyer"]`) |
| `Pigeon` | `pigeons` | `id`, `seller_id` (FK→users), `name`, `breed`, `photo_url`, `description` |
| `Auction` | `auctions` | `id`, `pigeon_id` (FK→pigeons), `seller_id` (FK→users), `status` (`active`/`ended`), `start_time`, `duration_seconds`, `winner_id` (FK→users) |
| `Bid` | `bids` | `id`, `auction_id` (FK→auctions), `user_id` (FK→users), `amount: Decimal`, `created_at` |

Tüm modeller `src/guvercin/models/` altında. `database.py` async engine + session factory sağlar.

---

## Token Budget

- `plans/` dosyası referansı — büyük context inline paste değil
- `@agent-planner` önce, `@agent-coder` sonra
- `@agent-tester` sadece Reviewer onayından sonra
- Context %70'e gelince `/compact`
