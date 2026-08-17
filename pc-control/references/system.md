# 🔐 Системные действия + системный API

Две категории: системные скрипты (VPN, разблокировка, ребут) и методы системного API (`api/system.py`).

## Категория 3 — Системные скрипты

| Действие | Скрипт | Описание |
|----------|--------|----------|
| Подключить VPN | `scripts/vpn_connect.py` | AmneziaVPN, server_index=1 |
| Отключить VPN | `scripts/vpn_disconnect.py` | Отключение AmneziaVPN |
| Разблокировать ПК | `scripts/unlock.py` | ⚠️ Вводит пароль (см. безопасность) |
| Ребут Jarvis | `scripts/jarvis_reboot.py` | Перезагрузка ассистента |

⚠️ **Безопасность:** `scripts/unlock.py` использует `scripts/pass_.py` с паролем в открытом виде (`truerealyexp`) — использовать с осторожностью.

## Категория 7 — Системный API (`api/system.py`)

| Метод | Описание |
|-------|----------|
| `system.open(target)` | Открыть URL/файл (xdg-open) |
| `system.exec(cmd, args)` | Выполнить команду, ждать результат |
| `system.exec_background(cmd, args)` | Выполнить команду в фоне |
| `system.notify(title, message)` | Системное уведомление |
| `system.clipboard.get()` | Получить текст из буфера обмена |
| `system.clipboard.set(text)` | Установить текст в буфер обмена |

## Зависимости

- **VPN:** AmneziaVPN CLI. Требуется `doas` для pkill (при отключении).
- **Уведомления:** libnotify.
