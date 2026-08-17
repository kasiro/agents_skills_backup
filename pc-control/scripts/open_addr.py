#!/usr/bin/env python3
"""Открыть адрес на Яндекс Картах в Firefox с чистым профилем"""

import sys
import asyncio
from pathlib import Path

parent_dir = str(Path(__file__).parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from _firefox_clean import open_firefox_clean

# маршрут
# https://yandex.ru/maps/?rtext=Новосибирск, {FROM}~Новосибирск, {TO}


async def execute(context):
    addr = context.get("slots", {}).get("addr", "")
    if not addr:
        print(f"[Jarvis:ERROR] no address provided")
        return {"success": False, "error": "no address"}

    url = f"https://yandex.ru/maps/?text={addr}"
    print(f"[Jarvis:INFO] Opening address [{addr}] in clean Firefox...")
    success = open_firefox_clean(url)
    print(f"[Jarvis:INFO] Address is ready")
    return {"success": success}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Найти адрес на Яндекс Картах")
    parser.add_argument("addr", nargs="?", default="", help="Адрес для поиска")
    args = parser.parse_args()
    context = {"slots": {"addr": args.addr}} if args.addr else {}
    result = asyncio.run(execute(context))
    return result["success"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python3 open_addr.py <адрес>")
        print("Пример: python3 open_addr.py 'ул. Ленина, 1'")
        sys.exit(1)
    sys.exit(0 if main() else 1)
