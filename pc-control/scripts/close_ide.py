#!/usr/bin/env python3
"""IDE closer - закрывает редактор кода (Zed)"""

import sys
import asyncio
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api import init_jarvis


async def execute(context):
    """Закрыть редактор кода"""
    jarvis = init_jarvis(context)
    jarvis.log("info", "Closing IDE...")

    jarvis.system.exec_background("killall zed-editor")

    return {"success": True}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
