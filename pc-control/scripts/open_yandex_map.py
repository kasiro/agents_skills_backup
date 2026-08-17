#!/usr/bin/env python3
"""Открыть Яндекс Карты в Firefox с чистым профилем"""

import sys
import asyncio
from pathlib import Path

parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from _firefox_clean import open_firefox_clean


async def execute(context):
    url = "https://yandex.ru/maps/65/novosibirsk/"
    print(f"[Jarvis:INFO] Opening Yandex Maps in clean Firefox...")
    success = open_firefox_clean(url)
    print(f"[Jarvis:INFO] Yandex Maps is ready")
    return {"success": success}


def main():
    result = asyncio.run(execute({}))
    return result["success"]


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
