#!/usr/bin/env python3
"""
Kid Mode OFF - Выключает детский режим

Команды:
- "обычный режим"
- "выключи детский режим"
- "деактивируй детский режим"
- "normal mode"

Функции выключения детского режима:
- Останавливает VPN через VPNController
- Закрывает YouTube Kids
- Разворачивает окна обратно
"""

import sys
import asyncio
from pathlib import Path

from api import init_jarvis

# Добавляем parent directory в path для импорта api.vpn
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api.vpn import VPNController


async def execute(context):
    jarvis = init_jarvis(context)

    success = await jarvis.modes.set_mode("normal")

    if success:
        jarvis.audio.play_ok()

        # 1. Останавливаем VPN
        vpn = VPNController(server_index=0, cleanup=False)
        # VPN не отключаем — требуется для OpenCode
        # vpn_result = vpn.disconnect()

        # 2. Закрываем YouTube Kids
        jarvis.system.exec("killall WebApp-youtubekids8701")

        # 3. Разворачиваем все окна обратно
        jarvis.environment.maximize_all_windows()

        return {"success": True}
    else:
        jarvis.log("error", "Failed to deactivate Kid Mode")
        jarvis.audio.play_error()
        jarvis.system.notify("Error", "Не удалось деактивировать детский режим")
        return {"success": False, "error": "Failed to deactivate Kid Mode"}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
