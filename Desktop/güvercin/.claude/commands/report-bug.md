# /report-bug

Screenshot veya açıklama ile hata bildirirken kullan.

## Adımlar

1. **Görseli tanımla** — 2-3 cümle: ne görünüyor, ne yanlış, nasıl olmalı
2. **KNOWN_BUGS.md tara** — eşleşen BUGID var mı?
   - EVET → `⚠️ REGRESSION [BUGID-XXX]` etiketi → `@agent-reviewer`
   - HAYIR → devam
3. **Bug report yaz** → `plans/bugs/YYYYMMDD-HHMMSS-<slug>.md`

```markdown
# Bug: <başlık>
Tarih: YYYY-MM-DD HH:MM
Durum: OPEN → FIXED → VERIFIED
Regression: EVET [BUGID-XXX] / HAYIR

## Görsel Tanım
<3 cümle>

## Kök Neden Hipotezi
<dosya · fonksiyon · yaklaşık satır>

## Düzeltme
<ne değişmeli>

## Regression Testi
tests/test_<slug>_no_regression.py yazılmalı

## Doğrulama
<düzeltme sonrası screenshot nasıl görünmeli>
```

4. **Yönlendir:**

| Durum | Agent |
|-------|-------|
| Neden net, düzeltme küçük | `@agent-coder` |
| Neden belirsiz | `@agent-planner` |
| Regression | `@agent-reviewer` → `@agent-coder` |
| Test/coverage sorunu | `@agent-tester` |

5. **Düzeltme sonrası** — yeni screenshot gelince:
   - Bug report `Status: VERIFIED`
   - `KNOWN_BUGS.md`'ye entry eklenmiş mi kontrol et
   - Regression testi var mı kontrol et
