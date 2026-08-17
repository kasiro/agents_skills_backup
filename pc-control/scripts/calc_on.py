#!/usr/bin/env python3
"""Calculator ON - запускает калькулятор или переключается на него"""

import sys
import asyncio
from pathlib import Path

# Добавляем parent directory в path для импорта api
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api import init_jarvis
from api.wm_manager import AppManager


async def execute(context):
    """Запустить калькулятор или переключиться на него"""
    jarvis = init_jarvis(context)
    jarvis.log("info", "Opening calculator...")

    manager = AppManager()
    manager.execute_background(["gnome-calculator"])

    jarvis.log("info", "Calculator ready")
    return {"success": True}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
