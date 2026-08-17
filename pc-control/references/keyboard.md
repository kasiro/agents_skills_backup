# 🎮 Клавиатурная эмуляция

Методы `api/environment.py` для автоматизации навигации (например, для обхода меню). Работают через `ydotool` (pydotool).

## Категория 5 — Методы клавиатуры

| Метод | Описание |
|-------|----------|
| `environment.press_tab(count=1, delay=0.1)` | Tab N раз |
| `environment.press_enter()` | Enter |
| `environment.press_space()` | Space |
| `environment.press_number(n)` | Цифра (0-4) |
| `environment.press_super_number(n)` | Super+цифра (переключение workspace) |
| `environment.type_text(text)` | Ввод текста (через ctrl+v, wl-copy) |
| `environment.type_text_english(text, char_delay_ms=50)` | Ввод англ. текста (ydotool type_string) |

## Пример

```python
import sys
sys.path.insert(0, '~/.agents/skills/pc-control')
from api.environment import Environment

env = Environment()
env.press_tab(3)        # три Tab для навигации по меню
env.press_enter()       # подтвердить выбор
env.type_text("hello")  # ввод текста
```

## Важно (Wayland)

- Эмуляция клавиатуры работает через **ydotool** (pydotool) — под Wayland xdotool не работает.
- Требуется запущенный демон `ydotool` и доступный сокет `/run/user/1000/.ydotool_socket`.
- `pydotool` установлен в `.venv` проекта Jarvis.

## Зависимости

```bash
doas pacman -S ydotool
```
