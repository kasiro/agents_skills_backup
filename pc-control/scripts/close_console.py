#!/usr/bin/env python3
"""Закрыть консоль (kgx)"""

import sys
import asyncio
from pathlib import Path

parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from api import init_jarvis


async def execute(context):
    """Закрыть консоль"""
    jarvis = init_jarvis(context)
    jarvis.log("info", "Closing console...")

    jarvis.system.exec("killall kgx")

    return {"success": True}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
