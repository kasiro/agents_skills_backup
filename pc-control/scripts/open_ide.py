#!/usr/bin/env python3
"""IDE launcher - открывает редактор кода (Zed) или переключается на него"""

import sys
import asyncio
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api import init_jarvis


async def execute(context):
    """Открыть редактор кода (Zed) или переключиться на него"""
    jarvis = init_jarvis(context)
    jarvis.log("info", "Opening IDE...")

    jarvis.environment.launch_or_move_app_background("zeditor", "dev.zed.Zed", 3)

    jarvis.log("info", "IDE ready")
    return {"success": True}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
