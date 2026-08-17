# 🚀 Запуск приложений

Все скрипты имеют единый интерфейс: `async def execute(context)` + `main()` для прямого запуска.
Запускаются через `python3 <путь/к/скрипту>`.

## Категория 2 — Приложения

| Действие | Скрипт | Приложение |
|----------|--------|------------|
| Открыть калькулятор | `scripts/calc_on.py` | gnome-calculator |
| Закрыть калькулятор | `scripts/calc_off.py` | killall gnome-calculator |
| Открыть терминал | `scripts/open_console.py` | kgx на workspace 2 |
| Закрыть терминал | `scripts/close_console.py` | killall kgx |
| Открыть IDE | `scripts/open_ide.py` | Zed на workspace 3 |
| Закрыть IDE | `scripts/close_ide.py` | killall zed-editor |
| Открыть браузер | `scripts/open_browser.py` | Brave на workspace 1 |
| Закрыть браузер | `scripts/browser_close.py` | killall brave |
| Открыть Яндекс Карты | `scripts/open_yandex_map.py` | В браузере |
| Найти адрес | `scripts/open_addr.py` | Яндекс Карты {addr} |
| Открыть Wildberries | `scripts/open_wildberries.py` | В браузере |
| Открыть финансы | `scripts/open_fin.py` | Docker контейнер + WebApp |
| Закрыть финансы | `scripts/close_fin.py` | pkill WebApp |
| Построить маршрут | `scripts/open_route.py <откуда> <куда>` | Яндекс Карты, маршрут A→B в чистом Firefox |

## Примеры запуска

```bash
python3 ~/.agents/skills/pc-control/scripts/calc_on.py
python3 ~/.agents/skills/pc-control/scripts/open_browser.py
python3 ~/.agents/skills/pc-control/scripts/open_route.py 'ул. Ленина, 1' 'ул. Пушкина, 10'
```

## Зависимости

- **Docker:** `scripts/open_fin.py` требует `docker-py` (управление контейнером ezbookkeeping). Остальные скрипты — без дополнительных Python-зависимостей.
- **Firefox:** `scripts/open_route.py` использует `scripts/_firefox_clean.py` (чистый профиль Firefox).
