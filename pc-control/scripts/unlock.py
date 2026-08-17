#!/usr/bin/env python3
"""Разблокировать компьютер (ввести пароль)"""

import sys
import asyncio
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api import init_jarvis
from .pass_ import password


async def execute(context):
    jarvis = init_jarvis(context)
    jarvis.environment.press_space()
    jarvis.environment.type_text_english(password, char_delay_ms=30, hold_delay_ms=30)
    jarvis.environment.press_enter()

    return {"success": True}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
