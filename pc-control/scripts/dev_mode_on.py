#!/usr/bin/env python3
"""
Dev Mode ON - Включает режим разработчика

Команды:
- "режим разработчика"
- "dev режим"
- "включи режим разработчика"
- "dev mode"

Функции режима разработчика:
- Управление рабочими столами
- Быстрый запуск приложений (Firefox, Консоль, Zed, YouGile)
- Развёрнутые окна
"""

import sys
import asyncio
from pathlib import Path
from time import sleep

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api import init_jarvis


async def execute(context):
    jarvis = init_jarvis(context)
    jarvis.log("info", "Activating Dev Mode...")

    success = await jarvis.modes.set_mode("dev")

    if success:
        jarvis.log("info", "Dev Mode activated successfully")
        jarvis.audio.play_ok()

        jarvis.environment.launch_or_move_app_background("firefox", "firefox", 1)
        jarvis.environment.wait_for_new_window_wmclass("firefox")

        jarvis.environment.launch_or_move_app_background(
            "kgx --working-directory '/home/kasiro/'", "org.gnome.Console", 2
        )
        jarvis.environment.wait_for_new_window_wmclass("org.gnome.Console")

        jarvis.environment.launch_or_move_app_background("zeditor", "dev.zed.Zed", 3)
        jarvis.environment.wait_for_new_window_wmclass("dev.zed.Zed")

        jarvis.environment.gtk_launch_background("WebApp-yougile3417", 4)
        jarvis.environment.wait_for_new_window_wmclass("WebApp-yougile3417")

        return {"success": True}
    else:
        jarvis.log("error", "Failed to activate Dev Mode")
        jarvis.audio.play_error()
        jarvis.system.notify("Error", "Не удалось активировать режим разработчика")
        return {"success": False, "error": "Failed to activate Dev Mode"}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
