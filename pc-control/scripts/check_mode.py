#!/usr/bin/env python3
"""
Check Mode - Показывает текущий режим

Команды:
- "какой режим"
- "текущий режим"
- "покажи режим"
- "current mode"
"""

import sys
import asyncio
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api import init_jarvis


async def execute(context):
    jarvis = init_jarvis(context)

    current_mode = jarvis.modes.get_current()
    jarvis.log("info", f"Current mode: {current_mode}")

    mode_descriptions = {
        "normal": "Обычный режим",
        "kid": "Детский режим",
        "dev": "Режим разработчика"
    }

    description = mode_descriptions.get(current_mode, "Неизвестный режим")

    jarvis.system.notify("Current Mode", description)
    jarvis.audio.play_ok()

    return {"success": True}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
