# Plan: GüvercinIhale MVP

Tarih: 2026-03-31
Status: APPROVED

## Amaç

Güvercin satıcılarının ilan listelediği, alıcıların sayaçlı canlı teklifler verebildiği
online ihale platformunun MVP sürümünü oluşturmak.

## Kapsam

- Dahil: Auth, güvercin CRUD, ihale oluşturma/listeleme, canlı teklif (WS),
  ödeme soyutlama katmanı (stub), frontend (Jinja2 + HTMX + Alpine.js), Docker
- Hariç: Gerçek ödeme sağlayıcı entegrasyonu, fotoğraf yükleme, bildirim sistemi

## Etkilenen Dosyalar

- Yeni: src/guvercin/ altındaki tüm modüller, templates, static, tests, Docker
- Değişen: Yok (sıfırdan oluşturuldu)

## Mimari Karar

- FastAPI + SQLAlchemy async + PostgreSQL + Redis
- Sayaç Redis'te tutulur, DB'ye sadece kapanışta yazılır
- Ödeme sağlayıcısı ABC ile soyutlanır, MVP'de StubPaymentProvider
- WebSocket JWT doğrulaması accept() öncesi yapılır
- Background task ile ihale sayacı otomatik kapatma

## Özel Dikkat Noktaları

- İhale sayacı: extend_if_needed() — <= operatörü, config'den sabitler
- Ödeme katmanı: PaymentProvider interface dışına çıkılmadı
- WebSocket: JWT doğrulama accept() öncesi, hata sadece sender'a

## Uygulama Fazları

### Faz 1 — Proje İskeleti
- [x] pyproject.toml, .gitignore, .env.example
- [x] config.py (pydantic-settings + sabitler)
- [x] database.py (async engine + session)
- [x] exceptions.py (4 custom exception)
- [x] models (User, Pigeon, Auction, Bid)
- [x] main.py (FastAPI app skeleton)
- [x] Alembic setup

### Faz 2 — Servisler
- [x] services/auth.py (JWT + bcrypt)
- [x] services/payment_service.py (ABC + Stub + DI)
- [x] services/auction_service.py (extend_if_needed, place_bid, close_auction)
- [x] services/websocket_manager.py (JWT before accept)
- [ ] Background task — ihale sayacı otomatik kapatma

### Faz 3 — Router'lar
- [x] routers/auth.py (register, login, me)
- [x] routers/pigeons.py (CRUD)
- [x] routers/auctions.py (CRUD + WS endpoint)
- [x] routers/payments.py (create, webhook, refund)
- [x] routers/pages.py (frontend sayfaları)

### Faz 4 — Frontend
- [x] templates/ (base, home, login, register, pigeons, auctions, auction_detail)
- [x] static/css/style.css (dark tema)
- [x] static/js/app.js (Alpine.js global state)

### Faz 5 — Docker
- [x] Dockerfile
- [x] docker-compose.yml (PostgreSQL + Redis + Web)

### Faz 6 — Testler
- [x] Boundary testleri (9/10/11 sn)
- [x] Auth testleri
- [x] Payment stub testleri
- [ ] WebSocket testleri
- [ ] Buyer role testi

## Test Stratejisi

- Auction sayacı: boundary testleri zorunlu (9/10/11 sn, extend sonrası extend, ended sonrası bid)
- WebSocket: invalid JWT → close 4001, broadcast, bid_too_low
- Rol: seller cannot bid own, buyer cannot create auction
- Payment: stub provider, DI override

## Reviewer Checklist
✅ APPROVED — 2026-03-31
- [x] Mimari uygun
- [x] Ödeme interface'i korunuyor — PaymentProvider ABC + DI, router bypass yok
- [x] WS protokolü uyumlu — JWT before accept, hata sadece sender'a
- [x] Sayaç mantığı bozulmadı — <= operatörü, config sabitleri
