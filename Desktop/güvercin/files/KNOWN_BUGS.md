# KNOWN_BUGS.md — GüvercinIhale Anti-Recurrence Registry

> **TÜM AGENTLAR:** Her oturum başında bu dosyayı oku.
> Kod yazmadan önce "Pattern to avoid" sütununu tara.
> Planladığın kod bir kalıpla eşleşiyorsa — DUR ve fix'i uygula.

---

## Nasıl eklenir

Bug düzeltilince şu formatla ekle:

```
## [BUGID-XXX] <başlık> — düzeltildi YYYY-MM-DD
**Kaçınılacak kalıp:** <tek satır — kötü kod/davranış>
**Kök neden:** <neden oldu>
**Doğru yaklaşım:** <ne yapılmalı>
**Etkilenen dosyalar:** <dosya yolları>
**Screenshot ref:** plans/bugs/YYYYMMDD-slug.md
```

BUGID numarasını sırayla artır. Eski entry'leri silme.

---

## Aktif Entry'ler

<!-- Buglar raporlandıkça buraya eklenir -->
<!-- Örnek (ilk gerçek entry eklenince bu yorumu sil):

## [BUGID-001] WebSocket JWT doğrulama atlandı — düzeltildi 2026-04-01
**Kaçınılacak kalıp:** ws.accept() JWT kontrolünden önce çağrılıyor
**Kök neden:** accept() önce çağrılmazsa mesaj alınamaz sanıldı
**Doğru yaklaşım:** ÖNCE token doğrula, geçersizse close(4001), SONRA accept()
**Etkilenen dosyalar:** src/guvercin/services/websocket_manager.py
**Screenshot ref:** plans/bugs/20260401-120000-ws-auth.md

-->
