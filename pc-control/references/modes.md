# 👶 Режимы (сценарии)

Сценарии автоматизации, привязанные к режимам ассистента. Текущий режим хранится в `api/mode_manager.py` / `api/modes.py`.

## Категория 4 — Режимы

| Режим | Скрипт | Описание |
|-------|--------|----------|
| Детский режим ВКЛ | `scripts/kid_mode_on.py` | VPN → свернуть окна → YouTube Kids → «синий трактор» |
| Детский режим ВЫКЛ | `scripts/kid_mode_off.py` | Отключить VPN, закрыть YouTube Kids |
| Режим разработчика | `scripts/dev_mode_on.py` | Firefox → Консоль → Zed → YouGile по workspace'ам |
| Проверить режим | `scripts/check_mode.py` | Показать текущий режим в уведомлении |

## Описание работы

- **`kid_mode_on.py`** — последовательность: подключение VPN, сворачивание всех окон, запуск YouTube Kids, включение «синего трактора» (Playwright — `yt_kids_playwright.py`).
- **`kid_mode_off.py`** — отключение VPN и закрытие YouTube Kids.
- **`dev_mode_on.py`** — раскладка рабочего окружения разработчика по workspace'ам.
- **`check_mode.py`** — показывает текущий режим (normal/kid/dev) системным уведомлением + звуковой сигнал (audio.play_ok).

## Вспомогательные скрипты

| Скрипт | Назначение |
|--------|------------|
| `scripts/_firefox_clean.py` | Открытие Firefox с чистым профилем |
| `scripts/yt_kids_playwright.py` | Автоматизация YouTube Kids через Playwright |
