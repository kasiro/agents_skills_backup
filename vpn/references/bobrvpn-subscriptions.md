# BobrVPN — Подписки

**Домен:** bobrvpn.com  
**IP:** 188.127.253.54  
**Бэкенд:** nginx → Laravel (PHP), только HTTP/2  
**TLS:** Let's Encrypt, TLSv1.3  

## Подписки

1. **Xem** (сайт, mail.ru) — 0f492a11... — expired 21.04.2026
2. **Ksyro** (сайт, mail.ru) — 84e9bd11... — expired 25.06.2026
3. **Telegram бот** — 3ff2d95b... — expire ~23.07.2026
4. **Telegram бот** — e600180f... — expire ~24.07.2026

## Особенности

- Генерация подписки ~40 секунд (Laravel Session Locking)
- Параллельные запросы → HTTP 500 Server Error
- Решение: ?raw=1, последовательные запросы с паузой >50с
- User-Agent влияет на формат: V2RayNG/1.8.1 → base64, Chrome → HTML
