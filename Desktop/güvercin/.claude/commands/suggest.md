# /suggest

Observer'ın biriktirdiği fikir listesini gösterir.

## Kullanım
- `/suggest` → tümünü göster
- `/suggest büyük` → sadece büyük etkili
- `/suggest ödeme` → "ödeme" içerenleri filtrele

## Adımlar

1. `DEVELOPER_PROFILE.md → Idea Backlog` oku
2. Filtre varsa uygula, yoksa tüm `[ ]` fikirleri göster
3. Etki büyüklüğü + güncellik sırasıyla listele
4. Geliştirici seçince:
   - `[x]` olarak işaretle, tarih ekle
   - `@agent-planner`'a devret

Backlog boşsa:
> "Henüz birikmiş fikir yok. Observer birkaç oturum izledikten sonra öneriler sunacak."
