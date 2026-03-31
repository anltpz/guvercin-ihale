# Plan: Güvercin Modeli Genişletme + İhale Başlatma İyileştirmesi

Tarih: 2026-03-31
Status: IN_REVIEW

## Amaç

Güvercin modeline alıcıların karar vermesini kolaylaştıran alanlar eklemek (yaş, cinsiyet, renk, ağırlık)
ve ihale başlatma akışını satıcının süre ve başlangıç fiyatı belirleyebildiği bir yapıya dönüştürmek.

## Kapsam

- Dahil:
  - Pigeon modeline yeni alanlar (age, gender, color, weight_kg)
  - Auction modeline starting_price alanı
  - İhale oluşturmada duration_seconds ve starting_price parametreleri
  - Frontend: ilan formu yeni alanlar, ihale başlatma dialog'u, güvercin düzenleme formu
  - İhale detayında güvercin bilgi kartı
  - Alembic migration
- Hariç:
  - health_status, vaccination_date (gelecek plan)
  - Fotoğraf yükleme (gelecek plan)
  - Satıcı profil sayfası (gelecek plan)

## Etkilenen Dosyalar

- Değişen:
  - `src/guvercin/models/pigeon.py` — yeni alanlar
  - `src/guvercin/models/auction.py` — starting_price
  - `src/guvercin/models/__init__.py` — re-export
  - `src/guvercin/routers/pigeons.py` — schema güncelleme + validation
  - `src/guvercin/routers/auctions.py` — AuctionCreate schema güncelleme
  - `src/guvercin/services/auction_service.py` — create_auction parametreleri
  - `src/guvercin/services/bid_service.py` — starting_price kontrolü
  - `src/guvercin/templates/pigeon_create.html` — yeni form alanları
  - `src/guvercin/templates/pigeon_detail.html` — yeni bilgiler + düzenleme + ihale dialog
  - `src/guvercin/templates/pigeons.html` — kart bilgileri güncelleme
  - `src/guvercin/templates/auction_detail.html` — güvercin bilgi kartı
  - `tests/test_auction_service.py` — starting_price testleri
  - `tests/test_pigeons_api.py` — validation testleri
- Yeni:
  - `src/guvercin/templates/pigeon_edit.html` — düzenleme formu
  - `alembic/versions/XXXX_add_pigeon_fields_and_starting_price.py`

## Mimari Karar

- Pigeon modeline eklenen alanlar nullable olacak (geriye dönük uyumluluk)
- starting_price Decimal(12,2), default 0
- duration_seconds artık AuctionCreate'den gelecek, config'deki değer varsayılan olarak kalacak
- bid_service.py'de ilk teklif >= starting_price kontrolü eklenecek
- Frontend'de ihale başlatma artık modal dialog ile olacak (Alpine.js)

## Özel Dikkat Noktaları

- İhale sayacı değişiyor mu? HAYIR — extend_if_needed dokunulmuyor
- Ödeme katmanı değişiyor mu? HAYIR
- WebSocket mesajı ekleniyor mu? HAYIR — mevcut protokol yeterli

## Uygulama Fazları

### Faz 1 — Model + Migration
- [ ] `pigeon.py`: age (Integer, nullable), gender (String(10), nullable), color (String(50), nullable), weight_kg (Numeric(5,2), nullable) ekle
- [ ] `auction.py`: starting_price (Numeric(12,2), default=0) ekle
- [ ] `models/__init__.py` güncelle
- [ ] Alembic migration oluştur ve uygula

### Faz 2 — Backend Servis + Router
- [ ] `routers/pigeons.py`: PigeonCreate ve PigeonResponse schema'larına yeni alanlar ekle
- [ ] `routers/pigeons.py`: Validation ekle (name min 2 karakter, breed min 2 karakter)
- [ ] `routers/auctions.py`: AuctionCreate'e duration_seconds (opsiyonel, default config) ve starting_price (opsiyonel, default 0) ekle
- [ ] `services/auction_service.py`: create_auction'a duration_seconds ve starting_price parametreleri
- [ ] `services/bid_service.py`: İlk teklif >= starting_price kontrolü

### Faz 3 — Frontend
- [ ] `pigeon_create.html`: yaş, cinsiyet (select), renk, ağırlık alanları
- [ ] `pigeon_edit.html`: düzenleme formu (create ile benzer, mevcut verilerle dolu)
- [ ] `pigeon_detail.html`: yeni bilgileri göster + "Düzenle" butonu + ihale başlatma modal'ı (süre seçici + başlangıç fiyatı)
- [ ] `pigeons.html`: kart üzerinde yaş, cinsiyet, renk göster
- [ ] `auction_detail.html`: güvercin bilgi kartı (isim, cins, renk, fotoğraf)
- [ ] `pages.py`: /ilan-duzenle/{pigeon_id} route ekle

## Test Stratejisi

- Pigeon CRUD: yeni alanlarla oluşturma/güncelleme/listeleme
- Validation: boş name, 1 karakterli breed → 422
- Auction create: custom duration + starting_price
- Bid: ilk teklif < starting_price → BidTooLowError
- İhale sayacı boundary testleri: DEĞİŞMEDİ, mevcut testler yeterli

## Reviewer Checklist
(Reviewer doldurur)
- [ ] Mimari uygun
- [ ] Ödeme interface'i korunuyor
- [ ] WS protokolü uyumlu
- [ ] Sayaç mantığı bozulmadı
