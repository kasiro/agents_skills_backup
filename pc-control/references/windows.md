# 🪟 Управление окнами

Две категории: самодостаточные Python-скрипты (subprocess, без API-зависимостей) и методы Python API (`api/environment.py`).

## Категория 1 — Самодостаточные Python-скрипты

Скрипты не требуют API-зависимостей, работают напрямую через subprocess:

| Команда | Скрипт | Что делает |
|---------|--------|------------|
| Свернуть все окна | `scripts/roll_up_windows.py` | Show Desktop через dbus GNOME |
| Развернуть все окна | (через Python API) | `environment.maximize_all_windows()` |
| Сделать скриншот | `scripts/screenshot.py` | gnome-screenshot → flameshot → grim |
| Смена раскладки | `scripts/set_language.py` | xdotool Super+Space или setxkbmap |
| Спящий режим | `scripts/sleep.py` | `systemctl suspend` |
| Очистить корзину | `scripts/empty_trash.py` | dbus Nautilus + rm -rf Trash |
| Показать буфер обмена | `scripts/clipboard_show.py` | wl-paste → xclip → xsel |

## Категория 6 — Управление окнами через Python API (`api/environment.py`)

| Метод | Описание |
|-------|----------|
| `environment.minimize_all_windows()` | Свернуть все |
| `environment.maximize_all_windows()` | Развернуть все |
| `environment.focus_window(wm_class)` | Сфокусировать окно |
| `environment.minimize_window(wm_class)` | Свернуть окно |
| `environment.maximize_window(wm_class)` | Развернуть окно |
| `environment.launch_or_move_app(app, wm_class, workspace)` | Запустить/переключить |
| `environment.launch_or_move_app_background(app, wm_class, workspace)` | Запустить в фоне/переключить |
| `environment.switch_to_workspace(number)` | Переключить workspace (1-4) |
| `environment.get_windows()` | Список окон |

## Пример использования Python API

Для сложной автоматизации (последовательности действий):

```python
import sys
sys.path.insert(0, '~/.agents/skills/pc-control')
from api import init_jarvis
from api.environment import Environment

env = Environment()
env.launch_or_move_app("brave", "brave-browser", 1)
env.switch_to_workspace(2)
```

## Зависимости

- **GNOME Shell:** управление окнами через D-Bus расширение `window-calls@domandoman.xyz`
- **Буфер обмена:** wl-clipboard (wl-paste), xclip/xsel как запасные
- **Скриншоты:** gnome-screenshot, grim, flameshot (в порядке приоритета)
