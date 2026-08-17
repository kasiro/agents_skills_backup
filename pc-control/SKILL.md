---
name: pc-control
description: |-
  Управление компьютером через голосовые команды. Запуск/закрытие приложений, управление окнами,
  системные действия (скриншот, сон, блокировка), буфер обмена, VPN, режимы (детский/разработчик),
  эмуляция клавиатуры (Tab, Enter, Space, ввод текста), работа с буфером обмена.
  Используй для выполнения команд управления ПК: запустить приложение, свернуть окна, сделать скриншот,
  переключить раскладку, очистить корзину, включить VPN, активировать режим.
  Все скрипты находятся локально в скилле pc-control.

  Примеры:
  - user: "открой калькулятор" → python3 ~/.agents/skills/pc-control/scripts/calc_on.py
  - user: "сделай скриншот" → python3 ~/.agents/skills/pc-control/scripts/screenshot.py
  - user: "сверни все окна" → python3 ~/.agents/skills/pc-control/scripts/roll_up_windows.py
  - user: "включи детский режим" → python3 ~/.agents/skills/pc-control/scripts/kid_mode_on.py
  - user: "открой браузер" → python3 ~/.agents/skills/pc-control/scripts/open_browser.py
  - user: "включи VPN" → python3 ~/.agents/skills/pc-control/scripts/vpn_connect.py
  - user: "отправь систему в сон" → python3 ~/.agents/skills/pc-control/scripts/sleep.py
  - user: "открой консоль" → python3 ~/.agents/skills/pc-control/scripts/open_console.py
  - user: "разблокируй компьютер" → python3 ~/.agents/skills/pc-control/scripts/unlock.py
  - user: "какой режим" → python3 ~/.agents/skills/pc-control/scripts/check_mode.py
  - user: "очисти корзину" → python3 ~/.agents/skills/pc-control/scripts/empty_trash.py
  - user: "переключи раскладку" → python3 ~/.agents/skills/pc-control/scripts/set_language.py
  - user: "покажи буфер обмена" → python3 ~/.agents/skills/pc-control/scripts/clipboard_show.py
  - user: "открой wildberries" → python3 ~/.agents/skills/pc-control/scripts/open_wildberries.py
  - user: "открой яндекс карты" → python3 ~/.agents/skills/pc-control/scripts/open_yandex_map.py
  - user: "найди адрес" → python3 ~/.agents/skills/pc-control/scripts/open_addr.py
  - user: "открой финансы" → python3 ~/.agents/skills/pc-control/scripts/open_fin.py
  - user: "закрой финансы" → python3 ~/.agents/skills/pc-control/scripts/close_fin.py
  - user: "выключи детский режим" → python3 ~/.agents/skills/pc-control/scripts/kid_mode_off.py
  - user: "режим разработчика" → python3 ~/.agents/skills/pc-control/scripts/dev_mode_on.py
  - user: "закрой калькулятор" → python3 ~/.agents/skills/pc-control/scripts/calc_off.py
  - user: "закрой консоль" → python3 ~/.agents/skills/pc-control/scripts/close_console.py
  - user: "закрой ide" → python3 ~/.agents/skills/pc-control/scripts/close_ide.py
  - user: "закрой браузер" → python3 ~/.agents/skills/pc-control/scripts/browser_close.py
  - user: "отключи vpn" → python3 ~/.agents/skills/pc-control/scripts/vpn_disconnect.py
  - user: "перезагрузи jarvis" → python3 ~/.agents/skills/pc-control/scripts/jarvis_reboot.py
  - user: "сделай ярче" → python3 ~/.agents/skills/pc-control/scripts/brightness_up.py
  - user: "сделай темнее" → python3 ~/.agents/skills/pc-control/scripts/brightness_down.py
  - user: "поставь яркость 60" → python3 ~/.agents/skills/pc-control/scripts/brightness_set.py 60
  - user: "какая яркость" → python3 ~/.agents/skills/pc-control/scripts/brightness_show.py
---
# PC Control — Управление компьютером

Скилл для выполнения команд управления ПК. Все скрипты в `scripts/`, детали по категориям — в `references/`.

## 📁 Расположение
- Скрипты: `~/.agents/skills/pc-control/scripts/`
- Референсы: `~/.agents/skills/pc-control/references/`

## 🗂️ Категории (загружай нужный референс)

| Категория | Референс | Команды |
|-----------|----------|---------|
| 🪟 Окна (скрипты + API) | `references/windows.md` | свернуть все, скриншот, раскладка, сон, корзина, буфер |
| 🚀 Приложения | `references/apps.md` | калькулятор, терминал, IDE, браузер, карты, WB, финансы |
| 🔐 Системные действия + API | `references/system.md` | VPN, разблокировка, ребут Jarvis, system.open/exec/notify |
| 👶 Режимы | `references/modes.md` | детский, разработчик, check_mode |
| 🎮 Клавиатура | `references/keyboard.md` | Tab/Enter/Space/цифры/текст через ydotool |
| 🔆 Яркость (DDC/CI) | `references/brightness.md` | ярче, темнее, set 0-100, показать |

## 🛠️ Зависимости
- ydotool (клавиатура Wayland), wl-clipboard, libnotify, gnome-screenshot/grim/flameshot, ddcutil (яркость), docker-py (open_fin), AmneziaVPN (vpn_connect)

## ⚠️ Важные замечания
1. **Безопасность:** `scripts/unlock.py` использует `scripts/pass_.py` с паролем в открытом виде — осторожно
2. **Wayland:** клавиатура через ydotool, сокет /run/user/1000/.ydotool_socket
3. **GNOME Shell:** окна через D-Bus расширение window-calls@domandoman.xyz
4. **Яркость:** монитор не подтверждает запись → `--noverify`, ddcutil без doas

## 🔍 Поиск по командам
1. Определи категорию (окна, приложения, система, режимы, клавиатура, яркость)
2. Загрузи соответствующий референс из references/
3. Запусти скрипт: `python3 ~/.agents/skills/pc-control/scripts/<script>.py`
