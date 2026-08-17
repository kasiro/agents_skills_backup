---
name: vpn
description: Управление VPN-инфраструктурой — мониторинг VLESS-прокси через Xray Checker (Docker), эндпоинты онлайн-подписок, клиенты Happ и Amnezia VPN. Использовать когда сэр спрашивает про VPN, подписки, Xray Checker, BobrVPN, Happ, Amnezia, VLESS, проверку прокси.

Examples:
- user: "какие у меня есть прокси" → показать статус из Xray Checker
- user: "подписка для Happ" → показать ссылку http://192.168.0.17:2113/subscribe
- user: "сколько серверов работает" → curl http://localhost:2113/online
- user: "обнови конфиги Xray Checker" → перегенерировать подписки
- user: "проверь подписки BobrVPN" → curl к bobrvpn.com/sub/...
- user: "настрой Amnezia/Happ" → показать инструкцию
- user: "создай маппинг для новых подписок" → обновить mapping.json
---

# VPN Infrastructure

Управление VPN-инфраструктурой на базе Xray-Checker, мониторинг VLESS-прокси BobrVPN, эндпоинты для Happ и Amnezia VPN.

## 🗺️ Архитектура

```
┌─────────────────────────────────────────────────────┐
│                    Сервер 192.168.0.17                │
│                                                       │
│  ┌─────────────────┐    ┌──────────────────────────┐  │
│  │  Xray Checker    │    │  VLESS Online Endpoint   │  │
│  │  (Docker)        │    │  (Python, systemd)       │  │
│  │  port :2112      │◄──►│  port :2113              │  │
│  │  kutovoys/       │    │                          │  │
│  │  xray-checker    │    │  /online  — JSON (online)│  │
│  └────────┬─────────┘    │  /subscribe — base64     │  │
│           │              └──────────┬───────────────┘  │
│           ▼                         ▼                  │
│  ┌──────────────────────────────────────────────┐     │
│  │  /home/kasiro/xray-checker-configs/           │     │
│  │  ├── xem.txt    (сайт mail.ru)                │     │
│  │  ├── ksyro.txt  (сайт mail.ru)                │     │
│  │  ├── bot3.txt   (Telegram бот)                │     │
│  │  ├── bot4.txt   (Telegram бот)                │     │
│  │  └── mapping.json (name→vless://)             │     │
│  └──────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐
│  Локальная сеть      │
│  Happ / Amnezia VPN  │
│  → :2113/subscribe   │
└─────────────────────┘
```

## 📦 Подписки BobrVPN

4 подписки BobrVPN (домен bobrvpn.com, IP: 188.127.253.54):

| # | UUID | Источник | Статус | Expire |
|---|------|----------|--------|--------|
| 1 | 0f492a11... | Сайт (mail.ru) — Xem | ✅ Истекла 21.04.2026, но сервера живы |
| 2 | 84e9bd11... | Сайт (mail.ru) — Ksyro | ✅ Истекла 25.06.2026, но сервера живы |
| 3 | 3ff2d95b... | Telegram бот + рефералка | ✅ Работает (expire ~23.07.2026) |
| 4 | e600180f... | Telegram бот + рефералка | ✅ Работает (expire ~24.07.2026) |

### Особенности BobrVPN

- **Бэкенд:** nginx → Laravel (PHP) → только HTTP/2
- **Проблема:** Laravel Session Locking — генерация подписки ~40 секунд
- **Симптом:** параллельные запросы → HTTP 500
- **Решение:** параметр `?raw=1` в URL подписки, последовательные запросы с паузой >50с
- **User-Agent:** влияет на формат ответа:
  - `V2RayNG/1.8.1` или `curl/...` → base64 подписка
  - `Mozilla/5.0 ...` → HTML портал

### Серверы (VLESS+REALITY)

| Локация | Хост | sni |
|---------|------|-----|
| 🇮🇹 Italy | vpn.it1.corlo.io:48790 | yahoo.com |
| 🇨🇿 Czech Republic | 194.182.77.123:443 | cloudflare.com |
| 🇺🇸 USA | 77.110.114.125:443 | amazon.com |
| 🇵🇱 Poland | 80.211.252.173:443 | nvidia.com |
| 🇸🇪 Sweden | 89.22.237.6:443 | ads.x5.ru |
| 🇷🇺 Russia | 82.146.41.176:443 | yahoo.com |

## 🐳 Docker: Xray Checker

**Образ:** `kutovoys/xray-checker`  
**Порт:** 2112 (веб-дашборд + API)  
**Статус:** `docker ps | grep xray-checker`

### Запуск
```bash
docker run -d \
  --name xray-checker \
  --restart unless-stopped \
  -v /home/kasiro/xray-checker-configs:/configs:ro \
  -e SUBSCRIPTION_URL="folder:///configs" \
  -e PROXY_CHECK_INTERVAL=300 \
  -e PROXY_TIMEOUT=20 \
  -e SUBSCRIPTION_UPDATE=false \
  -e WEB_PUBLIC=true \
  -e METRICS_PROTECTED=true \
  -e METRICS_USERNAME=xray \
  -e METRICS_PASSWORD=xray2024 \
  -p 2112:2112 \
  kutovoys/xray-checker
```

### API endpoints
- `GET /` — веб-дашборд
- `GET /api/v1/proxies` — JSON список всех прокси
- `GET /api/v1/status` — сводка (total/online/offline/avgLatencyMs)
- `GET /config/{stableId}` — статус конкретного прокси (200=OK / 503=Failed)
- `GET /health` — healthcheck

### Дашборд
- URL: http://localhost:2112
- Логин/пароль: `xray` / `xray2024`

## 🐍 VLESS Online Endpoint

**Скрипт:** `/home/kasiro/vless-online-server.py`  
**Systemd сервис:** `vless-online.service`  
**Порт:** 2113 (доступен из локальной сети)  
**Автозапуск:** включён

### Эндпоинты

#### GET /online — JSON со списком только рабочих прокси
```bash
curl -s http://192.168.0.17:2113/online | jq .
```
Формат ответа:
```json
{
  "proxies": ["vless://...", "vless://..."],
  "count": 4,
  "total_online": 4,
  "updated": "2026-07-04T12:12:54+00:00"
}
```

#### GET /subscribe — base64-подписка для Happ / Amnezia
```bash
curl -s http://192.168.0.17:2113/subscribe | base64 -d
```
Используйте эту ссылку в клиентах: `http://192.168.0.17:2113/subscribe`

### Маппинг
Файл: `/home/kasiro/xray-checker-configs/mapping.json`
Сопоставляет имена прокси из Xray Checker с оригинальными vless:// URL из подписок.

## 🔥 Firewall

Порт 2113 открыт в iptables (сохраняется через iptables.service).

## 📱 Клиенты

### Happ (iOS/Android)
- Поддерживает VLESS+REALITY
- Добавить подписку: `http://192.168.0.17:2113/subscribe`
- Автоматически получает только живые серверы

### Amnezia VPN (iOS/Android/Desktop)
- Поддерживает VLESS
- Добавить подписку: `http://192.168.0.17:2113/subscribe`
- Поддерживает стандартный base64 формат подписок

## 🔧 Обслуживание

### Обновить подписки BobrVPN
```bash
# 1. Скачать свежие подписки
curl -s -L --max-time 120 "https://bobrvpn.com/sub/....?raw=1" | base64 -d | grep -v "^#message:" > /home/kasiro/xray-checker-configs/имя.txt

# 2. Обновить mapping.json (добавить новые name→vless)
# 3. Перезапустить Xray Checker
docker restart xray-checker
```

### Посмотреть логи
```bash
# Xray Checker
docker logs --tail 50 xray-checker

# VLESS Online Endpoint
sudo journalctl -u vless-online.service --no-pager -n 30
```

### Перезапустить компоненты
```bash
# Xray Checker
docker restart xray-checker

# VLESS Online Endpoint
sudo systemctl restart vless-online.service
```
