#!/usr/bin/env python3
"""Calculator OFF - закрывает калькулятор"""
import sys
import asyncio
from pathlib import Path

# Добавляем parent directory в path для импорта api
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api import init_jarvis


async def execute(context):
    """Закрыть калькулятор"""
    jarvis = init_jarvis(context)
    jarvis.log("info", "Closing calculator...")

    jarvis.system.exec_background('killall gnome-calculator')

    return {"success": True}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
