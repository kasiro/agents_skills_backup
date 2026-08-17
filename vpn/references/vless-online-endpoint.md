# VLESS Online Endpoint

**Скрипт:** /home/kasiro/vless-online-server.py  
**Systemd:** vless-online.service  
**Порт:** 2113 (доступен из локальной сети)  
**Автозапуск:** enabled  
**Логи:** sudo journalctl -u vless-online.service  

## Эндпоинты

- `/online` — JSON со списком только рабочих vless:// ссылок
- `/subscribe` — base64-подписка для Happ, Amnezia VPN и других клиентов

## Маппинг

Файл: /home/kasiro/xray-checker-configs/mapping.json  
Связывает имена прокси (из Xray Checker API) с оригинальными vless:// URL.
