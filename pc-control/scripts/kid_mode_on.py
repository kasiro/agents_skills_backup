#!/usr/bin/env python3
"""
Kid Mode ON - Включает детский режим

Команды:
- "детский режим"
- "запусти детский режим"
- "протокол мультики"
- "kid mode"

Функции детского режима:
- Запускает VPN (безопасное соединение)
- Сворачивает все окна (родительский контроль)
- Открывает YouTube Kids в Firefox
"""

import sys
import asyncio
from pathlib import Path
from time import sleep

from api import init_jarvis

# Добавляем parent directory в path для импорта api.vpn
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api.vpn import VPNController


def setup(jarvis, delay):
    """пропускает настройки при запуске"""
    sleep(25)                          # ← 25 секунд

    jarvis.environment.press_tab(2)
    jarvis.environment.press_enter()
    sleep(delay)

    jarvis.environment.press_tab()
    jarvis.environment.press_enter()
    sleep(delay)

    for num in [2, 0, 0, 3]:
        jarvis.environment.press_number(num)
    jarvis.environment.press_enter()

    sleep(delay)
    jarvis.environment.press_space()
    jarvis.environment.press_tab(6)
    jarvis.environment.press_enter()
    sleep(delay)
    jarvis.environment.press_tab(2)
    jarvis.environment.press_enter()
    sleep(delay)
    jarvis.environment.press_tab(3)
    jarvis.environment.press_enter()
    sleep(delay)
    jarvis.environment.press_tab(5)
    jarvis.environment.press_enter()
    sleep(delay)
    jarvis.environment.press_tab()
    jarvis.environment.press_enter()
    sleep(delay)
    jarvis.environment.press_tab()
    jarvis.environment.press_enter()
    sleep(delay)
    jarvis.environment.press_tab(2)
    jarvis.environment.press_enter()
    sleep(delay)
    jarvis.environment.press_tab(2)
    jarvis.environment.press_enter()


async def execute(context):
    jarvis = init_jarvis(context)

    success = await jarvis.modes.set_mode("kid")

    if success:
        jarvis.audio.play_ok()

        # 1. Запускаем VPN
        vpn = VPNController(server_index=1, cleanup=False)
        vpn_result = vpn.connect()

        # 2. Сворачиваем все окна
        jarvis.environment.minimize_all_windows()

        # 3. Открываем YouTube Kids
        jarvis.system.exec_background("gtk-launch WebApp-youtubekids8701")
        not_found = 10
        interval = 0.5
        count = 0
        delay = 0.5

        while True:
            is_run = jarvis.environment.is_app_running("WebApp-youtubekids8701")
            if is_run:
                break
            sleep(interval)
            count += 0.5
            if round((count * interval), 0) >= not_found:
                break

        sleep(3)

        sleep(delay)
        jarvis.environment.press_tab(3)
        jarvis.environment.type_text("синий трактор")
        jarvis.environment.press_enter()

        sleep(delay)
        jarvis.environment.press_tab()
        sleep(delay)
        jarvis.environment.press_enter()

        sleep(delay)
        jarvis.environment.press_tab(7, delay=0.2)
        sleep(delay)
        jarvis.environment.press_enter()

        return {"success": True}
    else:
        jarvis.log("error", "Failed to activate Kid Mode")
        jarvis.audio.play_error()
        jarvis.system.notify("Error", "Не удалось активировать детский режим")
        return {"success": False, "error": "Failed to activate Kid Mode"}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
