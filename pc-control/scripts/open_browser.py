#!/usr/bin/env python3
"""Browser launcher - открывает браузер или переключается на него"""

import sys
import asyncio
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api import init_jarvis


async def execute(context):
    """Открыть браузер или переключиться на него"""
    jarvis = init_jarvis(context)
    jarvis.log("info", "Opening browser...")

    jarvis.environment.launch_or_move_app_background("brave", "brave-browser", 1)

    jarvis.log("info", "Browser ready")
    return {"success": True}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
